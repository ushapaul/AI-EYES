"""
Alert Manager Module
Handles email notifications, database logging, and real-time alerts
for suspicious activities detected by the surveillance system
"""

import smtplib
import cv2
import os
import time
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Callable
import logging
from pathlib import Path
from datetime import datetime, timedelta
import threading
import queue

from .activity_analyzer import SuspiciousActivity, ThreatLevel, ActivityType

logger = logging.getLogger(__name__)

class AlertManager:
    """
    Manages alerts, notifications, and logging for the surveillance system
    """
    
    def __init__(self,
                 smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 email_user: str = "",
                 email_password: str = "",
                 alert_emails: Optional[List[str]] = None,
                 alert_cooldown: float = 300.0,  # 5 minutes
                 snapshot_dir: str = "alerts/snapshots"):
        """
        Initialize alert manager
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            email_user: Email username
            email_password: Email password or app password
            alert_emails: List of email addresses to send alerts to
            alert_cooldown: Minimum time between alerts for same activity type (seconds)
            snapshot_dir: Directory to save alert snapshots
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password
        self.alert_emails = alert_emails or []
        self.alert_cooldown = alert_cooldown
        
        # Create directories
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Alert tracking
        self.last_alert_times: Dict[str, float] = {}  # activity_type -> timestamp
        self.alert_queue = queue.Queue()
        self.alert_thread = None
        self.is_running = False
        
        # Statistics
        self.stats = {
            'total_alerts': 0,
            'emails_sent': 0,
            'email_failures': 0,
            'last_alert_time': 0.0
        }
        
        # External callbacks
        self.database_callback: Optional[Callable[[Dict], None]] = None
        self.websocket_callback: Optional[Callable[[Dict], None]] = None
        
    def set_database_callback(self, callback: Callable[[Dict], None]):
        """
        Set callback for database logging
        
        Args:
            callback: Function to call for database logging
        """
        self.database_callback = callback
    
    def set_websocket_callback(self, callback: Callable[[Dict], None]):
        """
        Set callback for real-time websocket notifications
        
        Args:
            callback: Function to call for websocket notifications
        """
        self.websocket_callback = callback
    
    def start(self):
        """Start the alert processing thread"""
        self.is_running = True
        self.alert_thread = threading.Thread(target=self._process_alerts, daemon=True)
        self.alert_thread.start()
        logger.info("Alert manager started")
    
    def stop(self):
        """Stop the alert processing"""
        self.is_running = False
        if self.alert_thread:
            self.alert_thread.join(timeout=2)
        logger.info("Alert manager stopped")
    
    def process_activity(self, activity: SuspiciousActivity, frame: Optional[cv2.Mat] = None):
        """
        Process suspicious activity and trigger alerts
        
        Args:
            activity: SuspiciousActivity object
            frame: Current frame for snapshot
        """
        try:
            # Check cooldown
            if self._is_in_cooldown(activity):
                logger.debug(f"Activity {activity.activity_type.value} in cooldown, skipping alert")
                return
            
            # Update last alert time
            self.last_alert_times[activity.activity_type.value] = activity.timestamp
            
            # Create alert data
            alert_data = self._create_alert_data(activity, frame)
            
            # Add to processing queue
            self.alert_queue.put(alert_data)
            
            # Update statistics
            self.stats['total_alerts'] += 1
            self.stats['last_alert_time'] = time.time()
            
            logger.info(f"Alert queued: {activity.activity_type.value} - {activity.description}")
            
        except Exception as e:
            logger.error(f"Error processing activity alert: {e}")
    
    def _is_in_cooldown(self, activity: SuspiciousActivity) -> bool:
        """
        Check if activity type is in cooldown period
        
        Args:
            activity: SuspiciousActivity object
            
        Returns:
            True if in cooldown
        """
        activity_type = activity.activity_type.value
        if activity_type not in self.last_alert_times:
            return False
        
        time_since_last = activity.timestamp - self.last_alert_times[activity_type]
        return time_since_last < self.alert_cooldown
    
    def _create_alert_data(self, activity: SuspiciousActivity, frame: Optional[cv2.Mat] = None) -> Dict:
        """
        Create alert data dictionary
        
        Args:
            activity: SuspiciousActivity object
            frame: Current frame
            
        Returns:
            Alert data dictionary
        """
        # Save snapshot if frame provided
        snapshot_path = None
        if frame is not None:
            snapshot_path = self._save_alert_snapshot(activity, frame)
        
        # Create alert data
        alert_data = {
            'timestamp': activity.timestamp,
            'datetime': datetime.fromtimestamp(activity.timestamp).isoformat(),
            'activity_type': activity.activity_type.value,
            'threat_level': activity.threat_level.value,
            'track_id': activity.track_id,
            'description': activity.description,
            'location': activity.location,
            'zone_name': activity.zone_name,
            'confidence': activity.confidence,
            'evidence': activity.evidence,
            'snapshot_path': snapshot_path,
            'camera_id': 'default',  # TODO: Add camera identification
            'alert_id': f"{activity.activity_type.value}_{int(activity.timestamp)}_{activity.track_id}"
        }
        
        return alert_data
    
    def _save_alert_snapshot(self, activity: SuspiciousActivity, frame: cv2.Mat) -> str:
        """
        Save snapshot for alert
        
        Args:
            activity: SuspiciousActivity object
            frame: Frame to save
            
        Returns:
            Path to saved snapshot
        """
        try:
            timestamp_str = datetime.fromtimestamp(activity.timestamp).strftime("%Y%m%d_%H%M%S")
            filename = f"alert_{activity.activity_type.value}_{timestamp_str}_track{activity.track_id}.jpg"
            filepath = self.snapshot_dir / filename
            
            # Add alert annotation to frame
            annotated_frame = self._annotate_alert_frame(frame.copy(), activity)
            
            cv2.imwrite(str(filepath), annotated_frame)
            logger.info(f"Alert snapshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save alert snapshot: {e}")
            return ""
    
    def _annotate_alert_frame(self, frame: cv2.Mat, activity: SuspiciousActivity) -> cv2.Mat:
        """
        Add alert annotations to frame
        
        Args:
            frame: Frame to annotate
            activity: SuspiciousActivity object
            
        Returns:
            Annotated frame
        """
        try:
            # Add timestamp
            timestamp_str = datetime.fromtimestamp(activity.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp_str, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add alert information
            alert_text = f"ALERT: {activity.activity_type.value.upper()}"
            cv2.putText(frame, alert_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            threat_text = f"Threat Level: {activity.threat_level.value.upper()}"
            cv2.putText(frame, threat_text, (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Highlight activity location
            x, y = activity.location
            cv2.circle(frame, (x, y), 20, (0, 0, 255), 3)
            cv2.putText(frame, "ALERT", (x - 25, y - 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            return frame
            
        except Exception as e:
            logger.error(f"Frame annotation error: {e}")
            return frame
    
    def _process_alerts(self):
        """Process alerts in background thread"""
        while self.is_running:
            try:
                # Get alert from queue
                try:
                    alert_data = self.alert_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Process the alert
                self._handle_alert(alert_data)
                
            except Exception as e:
                logger.error(f"Alert processing error: {e}")
                time.sleep(0.1)
    
    def _handle_alert(self, alert_data: Dict):
        """
        Handle a single alert
        
        Args:
            alert_data: Alert data dictionary
        """
        try:
            # Send email notification
            if self.alert_emails and self.email_user and self.email_password:
                self._send_email_alert(alert_data)
            
            # Database logging
            if self.database_callback:
                try:
                    self.database_callback(alert_data)
                except Exception as e:
                    logger.error(f"Database callback error: {e}")
            
            # WebSocket notification
            if self.websocket_callback:
                try:
                    self.websocket_callback(alert_data)
                except Exception as e:
                    logger.error(f"WebSocket callback error: {e}")
            
            logger.info(f"Alert processed: {alert_data['alert_id']}")
            
        except Exception as e:
            logger.error(f"Alert handling error: {e}")
    
    def _send_email_alert(self, alert_data: Dict):
        """
        Send email alert
        
        Args:
            alert_data: Alert data dictionary
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = ', '.join(self.alert_emails)
            msg['Subject'] = f"🚨 Security Alert: {alert_data['activity_type'].upper()}"
            
            # Create email body
            body = self._create_email_body(alert_data)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach snapshot if available
            if alert_data['snapshot_path'] and os.path.exists(alert_data['snapshot_path']):
                with open(alert_data['snapshot_path'], 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data)
                    image.add_header('Content-Disposition', 
                                   f'attachment; filename="alert_snapshot.jpg"')
                    msg.attach(image)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_user, self.alert_emails, text)
            server.quit()
            
            self.stats['emails_sent'] += 1
            logger.info(f"Email alert sent to {len(self.alert_emails)} recipients")
            
        except Exception as e:
            self.stats['email_failures'] += 1
            logger.error(f"Email sending failed: {e}")
    
    def _create_email_body(self, alert_data: Dict) -> str:
        """
        Create HTML email body
        
        Args:
            alert_data: Alert data dictionary
            
        Returns:
            HTML email body
        """
        threat_colors = {
            'low': '#28a745',
            'medium': '#ffc107', 
            'high': '#fd7e14',
            'critical': '#dc3545'
        }
        
        threat_color = threat_colors.get(alert_data['threat_level'], '#6c757d')
        
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 15px; border-radius: 5px; }}
                .content {{ padding: 20px; border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }}
                .threat-level {{ display: inline-block; padding: 5px 10px; color: white; 
                               background-color: {threat_color}; border-radius: 3px; font-weight: bold; }}
                .detail {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #333; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 AI Eyes Security Alert</h2>
            </div>
            
            <div class="content">
                <div class="detail">
                    <span class="label">Alert Type:</span> {alert_data['activity_type'].replace('_', ' ').title()}
                </div>
                
                <div class="detail">
                    <span class="label">Threat Level:</span> 
                    <span class="threat-level">{alert_data['threat_level'].upper()}</span>
                </div>
                
                <div class="detail">
                    <span class="label">Description:</span> {alert_data['description']}
                </div>
                
                <div class="detail">
                    <span class="label">Location:</span> Zone "{alert_data['zone_name']}" at coordinates {alert_data['location']}
                </div>
                
                <div class="detail">
                    <span class="label">Time:</span> {alert_data['datetime']}
                </div>
                
                <div class="detail">
                    <span class="label">Track ID:</span> {alert_data['track_id']}
                </div>
                
                <div class="detail">
                    <span class="label">Confidence:</span> {alert_data['confidence']:.2f}
                </div>
                
                {self._format_evidence(alert_data.get('evidence', {}))}
            </div>
            
            <div class="footer">
                <p>This alert was generated by the AI Eyes Security System.</p>
                <p>Please review the attached snapshot and take appropriate action if necessary.</p>
                <p><strong>Do not reply to this email.</strong></p>
            </div>
        </body>
        </html>
        """
        
        return body
    
    def _format_evidence(self, evidence: Dict) -> str:
        """
        Format evidence data for email
        
        Args:
            evidence: Evidence dictionary
            
        Returns:
            Formatted HTML string
        """
        if not evidence:
            return ""
        
        html = '<div class="detail"><span class="label">Additional Evidence:</span><ul>'
        for key, value in evidence.items():
            html += f'<li><strong>{key.replace("_", " ").title()}:</strong> {value}</li>'
        html += '</ul></div>'
        
        return html
    
    def send_test_alert(self) -> bool:
        """
        Send test email alert
        
        Returns:
            True if successful
        """
        try:
            test_alert = {
                'timestamp': time.time(),
                'datetime': datetime.now().isoformat(),
                'activity_type': 'test_alert',
                'threat_level': 'low',
                'track_id': 999,
                'description': 'This is a test alert from AI Eyes Security System',
                'location': (100, 100),
                'zone_name': 'Test Zone',
                'confidence': 1.0,
                'evidence': {'test': True},
                'snapshot_path': None,
                'camera_id': 'test',
                'alert_id': f"test_{int(time.time())}"
            }
            
            self._send_email_alert(test_alert)
            return True
            
        except Exception as e:
            logger.error(f"Test alert failed: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get alert statistics
        
        Returns:
            Statistics dictionary
        """
        return self.stats.copy()
    
    def get_recent_alerts(self, hours: int = 24) -> List[str]:
        """
        Get list of recent alert snapshot files
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of snapshot file paths
        """
        try:
            cutoff_time = time.time() - (hours * 3600)
            recent_files = []
            
            for file_path in self.snapshot_dir.glob("alert_*.jpg"):
                if file_path.stat().st_mtime > cutoff_time:
                    recent_files.append(str(file_path))
            
            return sorted(recent_files, key=lambda x: os.path.getmtime(x), reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []
    
    def cleanup_old_snapshots(self, days: int = 7):
        """
        Clean up old alert snapshots
        
        Args:
            days: Number of days to keep snapshots
        """
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            deleted_count = 0
            
            for file_path in self.snapshot_dir.glob("alert_*.jpg"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old alert snapshots")
            
        except Exception as e:
            logger.error(f"Snapshot cleanup error: {e}")

if __name__ == "__main__":
    # Test the alert manager
    import argparse
    
    parser = argparse.ArgumentParser(description="Test AI Eyes Alert Manager")
    parser.add_argument("--email", type=str, help="Email address for test")
    parser.add_argument("--smtp-user", type=str, help="SMTP username")
    parser.add_argument("--smtp-pass", type=str, help="SMTP password")
    args = parser.parse_args()
    
    if args.email and args.smtp_user and args.smtp_pass:
        # Test email alert
        alert_manager = AlertManager(
            email_user=args.smtp_user,
            email_password=args.smtp_pass,
            alert_emails=[args.email]
        )
        
        alert_manager.start()
        
        print("Sending test alert...")
        success = alert_manager.send_test_alert()
        
        if success:
            print("Test alert sent successfully!")
        else:
            print("Test alert failed!")
        
        alert_manager.stop()
    else:
        print("Please provide --email, --smtp-user, and --smtp-pass arguments for testing")
        print("Example: python alert_manager.py --email test@example.com --smtp-user user@gmail.com --smtp-pass password")