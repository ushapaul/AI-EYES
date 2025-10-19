from flask_socketio import emit
from app.services.email_service import EmailAlertService
import threading
import time
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Import database models
try:
    from database.models import AlertModel
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️ MongoDB models not available, using in-memory storage only")

class AlertManager:
    def __init__(self, socketio):
        self.socketio = socketio
        self.email_service = EmailAlertService()
        self.active_alerts = {}
        self.alert_history = []
        
        # Initialize MongoDB alert model
        if MONGODB_AVAILABLE:
            try:
                self.alert_model = AlertModel()
                print("✅ MongoDB AlertModel initialized")
            except Exception as e:
                self.alert_model = None
                print(f"⚠️ MongoDB AlertModel initialization failed: {e}")
        else:
            self.alert_model = None
        
        # Email cooldown settings (to prevent spam)
        self.email_cooldown_minutes = int(os.getenv('ALERT_COOLDOWN_MINUTES', '5'))
        self.last_email_sent = defaultdict(lambda: datetime.min)
        
        # Alert severity mapping
        self.severity_mapping = {
            'multiple_persons': 'high', 
            'intruder': 'high',
            'suspicious_activity': 'high',
            'weapon_detected': 'critical',
            'armed_threat': 'critical'
        }
        
        print(f"🚨 Alert Manager initialized with SendGrid email service")
        print(f"📧 Email cooldown: {self.email_cooldown_minutes} minutes")
        print(f"📊 Email service status: {self.email_service.get_configuration_status()}")
        
    def send_alert(self, alert_data):
        """Send alert through multiple channels with smart filtering"""
        # Enhance alert data
        alert_data['id'] = self._generate_alert_id()
        alert_data['timestamp'] = datetime.now().isoformat()
        alert_data['severity'] = self.severity_mapping.get(alert_data['type'], 'medium')
        
        # Store alert in MongoDB
        if self.alert_model:
            try:
                db_alert_id = self.alert_model.create_alert(
                    camera_id=alert_data.get('camera_id', 'unknown'),
                    alert_type=alert_data['type'],
                    message=alert_data.get('description', ''),
                    severity=alert_data['severity'],
                    image_path=alert_data.get('image_path')
                )
                alert_data['db_id'] = db_alert_id
                print(f"💾 Alert saved to database: {db_alert_id}")
            except Exception as e:
                print(f"⚠️ Failed to save alert to database: {e}")
        
        # Store alert in memory
        self.active_alerts[alert_data['id']] = alert_data
        self.alert_history.append(alert_data)
        
        # Keep only last 100 alerts in memory
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        # Send real-time notification via WebSocket
        if self.socketio:
            self.socketio.emit('new_alert', alert_data)
        
        # Determine if email should be sent
        should_send_email = self._should_send_email(alert_data)
        
        if should_send_email:
            # Send email notification in background
            email_thread = threading.Thread(
                target=self._send_email_alert, 
                args=(alert_data,)
            )
            email_thread.daemon = True
            email_thread.start()
            
            # Update last email sent time
            self.last_email_sent[alert_data['type']] = datetime.now()
        
        # Log alert
        severity_icons = {
            'low': '🟢',
            'medium': '🟡', 
            'high': '🟠',
            'critical': '🔴'
        }
        icon = severity_icons.get(alert_data['severity'], '⚪')
        
        print(f"{icon} Alert [{alert_data['severity'].upper()}]: {alert_data['type']} at {alert_data.get('location', 'Unknown')} "
              f"(Email: {'✅' if should_send_email else '❌ Cooldown'})")
        
        return alert_data['id']
    
    def _should_send_email(self, alert_data):
        """Determine if email should be sent based on severity and cooldown"""
        # Check if email alerts are enabled
        if not self.email_service.enabled:
            return False
            
        # Always send critical alerts
        if alert_data['severity'] == 'critical':
            return True
            
        # Check cooldown for other alert types
        alert_type = alert_data['type']
        last_sent = self.last_email_sent[alert_type]
        cooldown_period = timedelta(minutes=self.email_cooldown_minutes)
        
        if datetime.now() - last_sent > cooldown_period:
            # Send high/medium severity alerts after cooldown
            return alert_data['severity'] in ['high', 'medium']
        
        return False
    
    def _send_email_alert(self, alert_data):
        """Send email alert with error handling"""
        try:
            success = self.email_service.send_alert(alert_data)
            if success:
                print(f"📧 Email alert sent successfully for {alert_data['type']}")
            else:
                print(f"❌ Failed to send email alert for {alert_data['type']}")
        except Exception as e:
            print(f"❌ Error sending email alert: {e}")
    
    def send_person_detection_alert(self, detections, camera_id, image_path=None):
        """Send person detection alert with smart classification - DISABLED"""
        # This method is disabled to prevent duplicate emails
        # Only intruder alerts are sent now
        return None
    
    def send_suspicious_activity_alert(self, activity_type, camera_id, confidence, image_path=None):
        """Send suspicious activity alert"""
        alert_data = {
            'type': 'suspicious_activity',
            'description': f"Suspicious activity detected: {activity_type}",
            'location': f"Camera {camera_id}",
            'camera_id': camera_id,
            'confidence': confidence * 100,
            'activity_type': activity_type
        }
        
        if image_path and os.path.exists(image_path):
            alert_data['image_path'] = image_path
            
        return self.send_alert(alert_data)
    
    def send_weapon_detection_alert(self, weapon_type, camera_id, confidence, image_path=None):
        """Send weapon detection alert (always critical)"""
        alert_data = {
            'type': 'weapon_detected',
            'description': f"WEAPON DETECTED: {weapon_type}",
            'location': f"Camera {camera_id}",
            'camera_id': camera_id,
            'confidence': confidence * 100,
            'weapon_type': weapon_type
        }
        
        if image_path and os.path.exists(image_path):
            alert_data['image_path'] = image_path
            
        return self.send_alert(alert_data)
    
    def send_intruder_alert(self, person_name, camera_id, confidence, image_path=None):
        """Send intruder detection alert for unauthorized person (always high priority)"""
        alert_data = {
            'type': 'intruder',
            'description': f"Unauthorized person detected in farm area: {person_name}",
            'location': f"Camera {camera_id}",
            'camera_id': camera_id,
            'confidence': confidence * 100,
            'person_name': person_name
        }
        
        if image_path and os.path.exists(image_path):
            alert_data['image_path'] = image_path
            
        return self.send_alert(alert_data)
    
    def test_email_system(self):
        """Test the email system with SendGrid"""
        print("🧪 Testing SendGrid email system...")
        
        # Show configuration status
        config_status = self.email_service.get_configuration_status()
        print(f"📧 Email Configuration:")
        for key, value in config_status.items():
            icon = "✅" if value else "❌"
            print(f"   {icon} {key}: {value}")
        
        # Send test email
        if config_status['configured']:
            return self.email_service.send_test_alert()
        else:
            print("❌ SendGrid not properly configured. Please check your API key and settings.")
            return False
    
    def get_alert_stats(self):
        """Get alert statistics"""
        if not self.alert_history:
            return {
                'total_alerts': 0,
                'alerts_by_type': {},
                'alerts_by_severity': {},
                'recent_alerts': []
            }
        
        # Count by type and severity
        alerts_by_type = defaultdict(int)
        alerts_by_severity = defaultdict(int)
        
        for alert in self.alert_history:
            alerts_by_type[alert['type']] += 1
            alerts_by_severity[alert['severity']] += 1
        
        return {
            'total_alerts': len(self.alert_history),
            'alerts_by_type': dict(alerts_by_type),
            'alerts_by_severity': dict(alerts_by_severity),
            'recent_alerts': self.alert_history[-10:],  # Last 10 alerts
            'email_service_status': self.email_service.get_configuration_status()
        }
    
    def _generate_alert_id(self):
        """Generate unique alert ID"""
        return f"ALERT_{int(time.time() * 1000)}"

# Global alert manager instance
alert_manager = None

def init_alert_manager(socketio):
    """Initialize global alert manager"""
    global alert_manager
    alert_manager = AlertManager(socketio)
    return alert_manager