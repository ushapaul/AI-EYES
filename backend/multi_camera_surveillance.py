#!/usr/bin/env python3
"""
Multi-Camera AI Surveillance System
Automatically detects and monitors ALL live IP webcam cameras
Provides unified surveillance across multiple camera feeds
"""

import sys
import os

# Get the directory where this script is located (backend directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(SCRIPT_DIR, "storage")
SNAPSHOTS_DIR = os.path.join(STORAGE_DIR, "snapshots")

# Suppress TensorFlow warnings for cleaner output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=info, 2=warning, 3=error
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom operations message
os.environ['OPENCV_FFMPEG_LOGLEVEL'] = '-8'  # Suppress FFmpeg connection errors

import cv2
import time
import threading
import requests
from datetime import datetime
from flask import Flask, jsonify, Response, render_template_string, request
import json
from dotenv import load_dotenv

# Suppress additional warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Set OpenCV log level to ERROR only
cv2.setLogLevel(3)  # 0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR, 4=FATAL

# Load environment variables
load_dotenv()

sys.path.append('.')
from surveillance.detector import YOLOv9Detector
from ai_models.face_recognition.mobilenet_face_recognition import MobileNetFaceRecognitionSystem
from surveillance.activity_analyzer import SuspiciousActivityAnalyzer, DetectionZone, ActivityType
from surveillance.tracker import PersonTracker
from app.services.alert_manager import AlertManager

class MultiCameraAISurveillance:
    """
    Automatic multi-camera surveillance system
    Detects all available IP cameras and runs AI surveillance on each
    """
    
    # ═══════════════════════════════════════════════════════════
    # 🎯 PERFORMANCE CONFIGURATION - ADJUST HERE
    # ═══════════════════════════════════════════════════════════
    FRAME_SKIP_INTERVAL = 3  # Process every Nth frame (3 = every 3rd frame)
                             # Lower = More accurate but slower (1 = every frame, 2 = every 2nd frame)
                             # Higher = Faster but may miss detections (5 = every 5th frame, 10 = every 10th)
    # ═══════════════════════════════════════════════════════════
    
    def __init__(self):
        self.app = Flask(__name__)
        
        # Initialize Alert Manager with SendGrid integration
        self.alert_manager = AlertManager(socketio=None)  # No WebSocket for multi-camera system
        
        # Auto-detect your IP cameras
        self.camera_urls = self.auto_detect_cameras()
        
        # Surveillance state
        self.active_cameras = {}
        self.latest_frames = {}
        self.activity_logs = []
        self.alert_count = 0
        self.detection_stats = {}
        
        # Frame processing counters for optimization
        self.frame_counters = {}  # Track frame numbers per camera
        
        # Camera auto-discovery settings
        self.camera_discovery_interval = 10  # Check for new cameras every 10 seconds
        self.discovery_thread = None
        self.discovery_running = False
        
        # Person tracking for activity analysis
        self.person_trackers = {}  # Track person movements per camera
        
        # Activity analyzers for each camera
        self.activity_analyzers = {}  # Suspicious activity detection per camera
        
        # Face detection memory - tracks last authorized person per camera
        # Prevents false alerts when authorized person's face is temporarily obscured
        self.last_authorized_person = {}  # camera_name -> {'names': [list], 'timestamp': datetime, 'frames_since_seen': int}
        self.max_frames_without_face = 10  # Allow 10 frames (~5 seconds) before alerting on "no face"
        
        # AI Components - Optimized for ULTRA performance with minimal lag
        self.detector = YOLOv9Detector(
            conf_threshold=0.4,   # Higher threshold for faster processing and less noise
            device='cpu'          # Ensure CPU usage for stability
        )
        
        # Face Recognition - MobileNetV2 Model (100% Validated)
        # Uses transfer learning with ImageNet pre-training for superior accuracy
        # Trained on 555 samples with 100% validation accuracy
        # Includes aggressive Unknown class calibration for stable recognition
        self.face_recognizer = MobileNetFaceRecognitionSystem()
        print(f"👤 Face Recognition: {'✅ MobileNetV2 Model Loaded' if self.face_recognizer.is_trained else '⚠️ Model not found'}")
        print(f"🔒 Recognition Model: MobileNetV2 with MediaPipe Face Detection + Unknown Calibration")
        if self.face_recognizer.is_trained:
            authorized = self.face_recognizer.get_authorized_persons()
            print(f"✅ Authorized Persons: {', '.join(authorized)}")
        
        # Initialize activity analyzers and trackers for each camera
        self._initialize_activity_detection()
        
        print(f"🔍 Multi-Camera AI Surveillance System Initialized")
        print(f"📹 Found {len(self.camera_urls)} live cameras")
        print(f"🚨 SendGrid Email Alerts: {'✅ Enabled' if self.alert_manager.email_service.enabled else '❌ Disabled'}")
        print(f"🎯 Activity Detection: Loitering | Zone Intrusion | Running | Fighting | Abandoned Objects")
        
        self.setup_flask_routes()
    
    def auto_detect_cameras(self, silent=False):
        """Automatically detect all live IP cameras using discovery service"""
        if not silent:
            print("🔎 Auto-detecting live IP cameras...")
        
        cameras = {}
        
        # Method 1: Try to load from camera discovery service (discovered_cameras collection)
        try:
            from app.services.camera_discovery import camera_discovery
            
            # Load previously discovered cameras
            discovered_cameras = camera_discovery.get_cameras()
            
            if discovered_cameras:
                if not silent:
                    print(f"📂 Found {len(discovered_cameras)} cameras in discovery database")
                
                for cam in discovered_cameras:
                    # Only use online cameras
                    if cam['status'] == 'online':
                        camera_name = cam['id']
                        camera_url = cam['url']
                        
                        # Verify camera is still accessible
                        try:
                            response = requests.head(camera_url, timeout=2)
                            if response.status_code in [200, 302]:
                                cameras[camera_name] = camera_url
                                if not silent:
                                    print(f"✅ {camera_name}: {camera_url}")
                        except:
                            if not silent:
                                print(f"❌ {camera_name}: {camera_url} (not accessible)")
        
        except ImportError:
            if not silent:
                print("⚠️ Camera discovery service not available")
        
        # Method 2: Load from main cameras collection (MongoDB)
        if not cameras:
            try:
                from database.config import get_database
                db = get_database()
                if db is not None:
                    cameras_collection = db['cameras']
                    db_cameras = list(cameras_collection.find({'enabled': True}))
                    
                    if db_cameras:
                        if not silent:
                            print(f"📂 Found {len(db_cameras)} cameras in main database")
                        
                        for cam in db_cameras:
                            camera_name = cam.get('name', cam.get('_id'))
                            camera_url = cam.get('url')
                            
                            if camera_url:
                                # Add camera regardless of current accessibility status
                                # System will auto-retry connection in surveillance thread
                                cameras[camera_name] = {
                                    'url': camera_url,
                                    'ai_mode': cam.get('ai_mode', 'both')
                                }
                                
                                # Check current accessibility for status display
                                if not silent:
                                    try:
                                        response = requests.head(camera_url, timeout=2)
                                        if response.status_code in [200, 302]:
                                            print(f"✅ {camera_name}: {camera_url} (online)")
                                        else:
                                            print(f"⏳ {camera_name}: {camera_url} (will retry connection)")
                                    except:
                                        print(f"⏳ {camera_name}: {camera_url} (waiting for connection)")
                    else:
                        if not silent:
                            print("ℹ️ No enabled cameras in main database")
            except Exception as e:
                if not silent:
                    print(f"⚠️ Error loading from main database: {e}")
        
        # No fallback - return empty if no cameras discovered
        if not cameras and not silent:
            print("⚠️ No cameras detected. Please add cameras manually or use the discovery service.")
            print("📡 To scan: POST http://localhost:5000/api/camera/scan")
        
        if not silent:
            print(f"✅ Total cameras ready: {len(cameras)}")
        return cameras
    
    def _initialize_activity_detection(self):
        """Initialize activity detection for suspicious behavior monitoring"""
        print("\n🎯 Initializing Suspicious Activity Detection...")
        
        for camera_name in self.camera_urls.keys():
            # Create person tracker for each camera
            self.person_trackers[camera_name] = PersonTracker(
                tracker_type='KCF',  # Faster than CSRT for real-time
                max_tracks=20,
                track_timeout=5.0
            )
            
            # Create activity analyzer for each camera
            self.activity_analyzers[camera_name] = SuspiciousActivityAnalyzer(
                loitering_threshold=30.0,      # 30 seconds for loitering
                abandoned_object_threshold=60.0,  # 60 seconds for abandoned objects
                speed_threshold=15.0,          # pixels/second for running detection (15 px/s based on observed speeds)
                crowd_threshold=5               # 5+ people for crowd
            )
            
            # Add default detection zones (whole frame as monitored zone)
            # You can customize these zones based on your camera views
            default_zone = DetectionZone(
                name=f"{camera_name}_main_area",
                points=[(0, 0), (1920, 0), (1920, 1080), (0, 1080)],  # Full frame
                zone_type="monitored",
                activity_types=[
                    ActivityType.LOITERING,
                    ActivityType.ZONE_INTRUSION,
                    ActivityType.RUNNING,
                    ActivityType.ABANDONED_OBJECT,
                    ActivityType.WEAPON_DETECTED
                ]
            )
            self.activity_analyzers[camera_name].add_detection_zone(default_zone)
            
            print(f"  ✅ {camera_name}: Tracker + Activity Analyzer initialized")
        
        print("✅ Activity Detection System Ready")
        print("   📍 Monitored Activities:")
        print("      • Loitering (30+ seconds)")
        print("      • Zone Intrusion (unauthorized access)")
        print("      • Running (fast movement)")
        print("      • Abandoned Objects (60+ seconds)")
        print("      • Weapon Detection (firearms, knives)")
    
    def setup_flask_routes(self):
        """Setup web interface for multi-camera surveillance"""
        
        @self.app.route('/')
        def dashboard():
            """Multi-camera surveillance dashboard"""
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>🔍 Multi-Camera AI Surveillance</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .stats { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
        .stat-box { background: white; padding: 15px; border-radius: 8px; flex: 1; min-width: 150px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .cameras-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .camera-box { background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .live-feed { width: 100%; max-width: 380px; border: 3px solid #3498db; border-radius: 8px; }
        .camera-status { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .status-online { color: #27ae60; font-weight: bold; }
        .status-offline { color: #e74c3c; font-weight: bold; }
        .activity-panel { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .activity-log { max-height: 300px; overflow-y: auto; }
        .alert { background: #e74c3c; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .warning { background: #f39c12; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .normal { background: #27ae60; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .info { background: #3498db; color: white; padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px; }
        .btn { background: #3498db; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; margin: 5px; font-size: 16px; }
        .btn:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; }
        .btn-success { background: #27ae60; }
        .camera-stats { background: #ecf0f1; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 12px; }
        .detection-count { font-size: 14px; color: #2c3e50; margin: 5px 0; }
    </style>
    <script>
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-cameras').textContent = data.total_cameras;
                    document.getElementById('active-cameras').textContent = data.active_cameras;
                    document.getElementById('total-detections').textContent = data.total_detections;
                    document.getElementById('total-alerts').textContent = data.total_alerts;
                    
                    // Update camera stats
                    Object.keys(data.camera_stats).forEach(cameraName => {
                        const stats = data.camera_stats[cameraName];
                        const statsElement = document.getElementById(`stats-${cameraName}`);
                        if (statsElement) {
                            statsElement.innerHTML = `
                                <div class="detection-count">Objects: ${stats.detections}</div>
                                <div class="detection-count">Persons: ${stats.persons}</div>
                                <div class="detection-count">FPS: ${stats.fps}</div>
                            `;
                        }
                    });
                });
            
            fetch('/api/activities')
                .then(response => response.json())
                .then(data => {
                    const logDiv = document.getElementById('activity-log');
                    logDiv.innerHTML = '';
                    data.activities.slice(-20).reverse().forEach(activity => {
                        const div = document.createElement('div');
                        div.className = activity.is_alert ? 'alert' : (activity.is_warning ? 'warning' : (activity.is_info ? 'info' : 'normal'));
                        div.innerHTML = `<strong>${activity.time}</strong> [${activity.camera}] ${activity.description}`;
                        logDiv.appendChild(div);
                    });
                });
        }
        
        function startAllSurveillance() {
            fetch('/api/start_all', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function stopAllSurveillance() {
            fetch('/api/stop_all', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function startCamera(cameraName) {
            fetch(`/api/start/${cameraName}`, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        function stopCamera(cameraName) {
            fetch(`/api/stop/${cameraName}`, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshData();
                });
        }
        
        setInterval(refreshData, 2000);
        refreshData();
    </script>
</head>
<body>
    <div class="header">
        <h1>🔍 Multi-Camera AI Surveillance System</h1>
        <p>Unified Surveillance Across All IP Cameras</p>
        <button class="btn btn-success" onclick="startAllSurveillance()">▶️ Start All Cameras</button>
        <button class="btn btn-danger" onclick="stopAllSurveillance()">⏹️ Stop All Cameras</button>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>📹 Total Cameras</h3>
            <h2 id="total-cameras">{{ camera_count }}</h2>
        </div>
        <div class="stat-box">
            <h3>🟢 Active Cameras</h3>
            <h2 id="active-cameras">0</h2>
        </div>
        <div class="stat-box">
            <h3>🎯 Total Detections</h3>
            <h2 id="total-detections">0</h2>
        </div>
        <div class="stat-box">
            <h3>⚠️ Total Alerts</h3>
            <h2 id="total-alerts">0</h2>
        </div>
    </div>
    
    <div class="cameras-grid">
        {% for camera_name, camera_info in cameras.items() %}
        <div class="camera-box">
            <div class="camera-status">
                <h3>📷 {{ camera_name }}</h3>
                <span class="status-online">🟢 {{ camera_info.status.upper() }}</span>
            </div>
            <img src="/video_feed/{{ camera_name }}" class="live-feed" alt="Live AI Feed">
            <div class="camera-stats">
                <strong>URL:</strong> {{ camera_info.base_url }}<br>
                <strong>Resolution:</strong> {{ camera_info.resolution[1] }}x{{ camera_info.resolution[0] }}
                <div id="stats-{{ camera_name }}">
                    <div class="detection-count">AI Processing Ready</div>
                </div>
            </div>
            <button class="btn btn-success" onclick="startCamera('{{ camera_name }}')">▶️ Start</button>
            <button class="btn btn-danger" onclick="stopCamera('{{ camera_name }}')">⏹️ Stop</button>
        </div>
        {% endfor %}
    </div>
    
    <div class="activity-panel">
        <h3>📊 Live Multi-Camera Activity Log</h3>
        <div class="activity-log" id="activity-log">
            <div class="info"><strong>System</strong> Multi-camera surveillance ready...</div>
        </div>
    </div>
</body>
</html>
            ''', cameras=self.camera_urls, camera_count=len(self.camera_urls))
        
        @self.app.route('/api/cameras')
        def api_cameras():
            """Get list of all cameras with status for dashboard"""
            cameras = []
            for camera_name, camera_url in self.camera_urls.items():
                # Check if camera is currently active/online
                is_online = camera_name in self.active_cameras
                
                cameras.append({
                    'id': camera_name,
                    'name': camera_name.replace('_', ' ').title(),
                    'location': 'Farm Security Zone',
                    'status': 'online' if is_online else 'offline',
                    'url': camera_url,
                    'type': 'farm'
                })
            
            return jsonify(cameras)
        
        @self.app.route('/api/status')
        def api_status():
            """Get system status"""
            total_detections = sum(self.detection_stats.get(cam, {}).get('total_detections', 0) for cam in self.active_cameras)
            
            camera_stats = {}
            for camera_name in self.camera_urls.keys():
                if camera_name in self.latest_frames:
                    frame_data = self.latest_frames[camera_name]
                    camera_stats[camera_name] = {
                        'detections': len(frame_data.get('detections', [])),
                        'persons': len(frame_data.get('persons', [])),
                        'fps': self.detection_stats.get(camera_name, {}).get('fps', 0)
                    }
                else:
                    camera_stats[camera_name] = {'detections': 0, 'persons': 0, 'fps': 0}
            
            return jsonify({
                'total_cameras': len(self.camera_urls),
                'active_cameras': len(self.active_cameras),
                'total_detections': total_detections,
                'total_alerts': self.alert_count,
                'camera_stats': camera_stats
            })
        
        @self.app.route('/api/activities')
        def api_activities():
            """Get recent activities from all cameras"""
            return jsonify({'activities': self.activity_logs[-50:]})
        
        @self.app.route('/api/start_all', methods=['POST'])
        def api_start_all():
            """Start surveillance on all cameras"""
            try:
                self.start_all_surveillance()
                return jsonify({'success': True, 'message': f'Started AI surveillance on all {len(self.camera_urls)} cameras!'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/stop_all', methods=['POST'])
        def api_stop_all():
            """Stop all surveillance"""
            try:
                self.stop_all_surveillance()
                return jsonify({'success': True, 'message': 'Stopped surveillance on all cameras'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/email/status', methods=['GET'])
        def api_email_status():
            """Get email service configuration status"""
            try:
                status = self.alert_manager.get_alert_stats()
                return jsonify({
                    'success': True,
                    'email_status': status['email_service_status'],
                    'alert_stats': {
                        'total_alerts': status['total_alerts'],
                        'alerts_by_type': status['alerts_by_type'],
                        'alerts_by_severity': status['alerts_by_severity']
                    }
                })
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/email/test', methods=['POST'])
        def api_test_email():
            """Send test email to verify SendGrid configuration"""
            try:
                success = self.alert_manager.test_email_system()
                if success:
                    return jsonify({
                        'success': True, 
                        'message': '✅ Test email sent successfully! Check your inbox.',
                        'service': 'SendGrid'
                    })
                else:
                    return jsonify({
                        'success': False, 
                        'message': '❌ Failed to send test email. Check your SendGrid configuration.',
                        'service': 'SendGrid'
                    })
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/alerts/recent', methods=['GET'])
        def api_recent_alerts():
            """Get recent alert history"""
            try:
                stats = self.alert_manager.get_alert_stats()
                return jsonify({
                    'success': True,
                    'recent_alerts': stats['recent_alerts'],
                    'total_count': stats['total_alerts']
                })
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/alerts/send-email', methods=['POST'])
        def api_send_alert_email():
            """Send alert email to selected recipients"""
            try:
                data = request.get_json()
                
                # Extract data from request
                alert_id = data.get('alert_id')
                recipients = data.get('recipients', [])  # List of recipient names
                alert_data = data.get('alert_data', {})
                
                if not recipients:
                    return jsonify({
                        'success': False, 
                        'message': 'No recipients specified'
                    })
                
                # Map recipient names to email addresses
                recipient_emails = []
                recipient_mapping = {
                    'Manager Prajwal': os.getenv('MANAGER_PRAJWAL_EMAIL', 'praveenkumarnaik14@gmail.com'),
                    'Farmer Basava': os.getenv('FARMER_BASAVA_EMAIL', 'praveenkumarnaik14@gmail.com'),
                    'Owner Rajasekhar': os.getenv('OWNER_RAJASEKHAR_EMAIL', 'praveenkumarnaik14@gmail.com')
                }
                
                for recipient_name in recipients:
                    if recipient_name in recipient_mapping:
                        recipient_emails.append(recipient_mapping[recipient_name])
                
                # Determine alert type based on alert data
                alert_type = alert_data.get('type', 'intruder')
                camera_name = alert_data.get('camera', 'Unknown Camera')
                location = alert_data.get('location', 'Unknown Location')
                severity = alert_data.get('severity', 'high')
                confidence = alert_data.get('confidence', 0)
                detected_person = alert_data.get('person', 'Unknown')
                
                # Prepare alert details
                alert_details = {
                    'alert_type': alert_type,
                    'severity': severity,
                    'location': location,
                    'camera_name': camera_name,
                    'confidence': confidence,
                    'detected_person': detected_person,
                    'timestamp': alert_data.get('timestamp', '')
                }
                
                # Get alert image path if available
                image_path = None
                if 'image' in alert_data and alert_data['image']:
                    # If image is provided as base64 or path
                    image_path = alert_data['image']
                
                # Send email using EmailAlertService
                print(f"\n📧 Sending alert email to: {', '.join(recipient_emails)}")
                print(f"   Alert Type: {alert_type}")
                print(f"   Location: {location}")
                print(f"   Detected: {detected_person}")
                
                # Prepare email data for SendGrid service
                from app.services.email_service import EmailAlertService
                email_service = EmailAlertService()
                
                # Override recipients with selected ones
                email_service.recipients = recipient_emails
                
                # Prepare alert data for email
                email_alert_data = {
                    'type': alert_type,
                    'severity': severity,
                    'location': location,
                    'camera': camera_name,
                    'confidence': confidence,
                    'person': detected_person,
                    'timestamp': alert_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    'image_path': image_path
                }
                
                success = email_service.send_alert(email_alert_data)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'✅ Email sent successfully to {len(recipient_emails)} recipient(s)',
                        'recipients': recipient_emails,
                        'alert_type': alert_type
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '❌ Failed to send email. Check SendGrid configuration.'
                    })
                    
            except Exception as e:
                print(f"❌ Error sending alert email: {e}")
                return jsonify({
                    'success': False, 
                    'message': f'Error: {str(e)}'
                })
        
        @self.app.route('/api/start/<camera_name>', methods=['POST'])
        def api_start_camera(camera_name):
            """Start surveillance on specific camera"""
            try:
                if camera_name in self.camera_urls:
                    self.start_camera_surveillance(camera_name)
                    return jsonify({'success': True, 'message': f'Started surveillance on {camera_name}'})
                else:
                    return jsonify({'success': False, 'message': 'Camera not found'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/api/stop/<camera_name>', methods=['POST'])
        def api_stop_camera(camera_name):
            """Stop surveillance on specific camera"""
            try:
                if camera_name in self.active_cameras:
                    self.stop_camera_surveillance(camera_name)
                    return jsonify({'success': True, 'message': f'Stopped surveillance on {camera_name}'})
                else:
                    return jsonify({'success': False, 'message': 'Camera not active'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        
        @self.app.route('/video_feed/<camera_name>')
        def video_feed(camera_name):
            """Live video feed with AI annotations"""
            return Response(
                self.generate_frames(camera_name),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
    
    def generate_frames(self, camera_name):
        """Generate annotated video frames for specific camera"""
        while camera_name in self.active_cameras:
            try:
                if camera_name in self.latest_frames:
                    frame_data = self.latest_frames[camera_name]
                    annotated_frame = frame_data.get('annotated_frame')
                    
                    if annotated_frame is not None:
                        # Resize frame for faster streaming (reduce to 640x360 for web)
                        height, width = annotated_frame.shape[:2]
                        if width > 640:
                            scale = 640 / width
                            new_width = 640
                            new_height = int(height * scale)
                            annotated_frame = cv2.resize(annotated_frame, (new_width, new_height))
                        
                        # Lower JPEG quality for faster transmission (60 instead of 80)
                        ret, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                        if ret:
                            frame = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
                time.sleep(0.05)  # ~20 FPS for smoother playback
                
            except Exception as e:
                print(f"Frame generation error for {camera_name}: {e}")
                time.sleep(1)
    
    def process_camera_feed(self, camera_name, camera_info):
        """Process individual camera with AI surveillance"""
        # Handle both string URL and dict format
        if isinstance(camera_info, str):
            camera_url = camera_info
            ai_mode = 'both'  # Default mode
        else:
            camera_url = camera_info['url']
            ai_mode = camera_info.get('ai_mode', 'both')  # Get AI mode from camera config
            
        print(f"🎯 Starting AI surveillance for {camera_name}: {camera_url}")
        print(f"   🤖 AI Mode: {ai_mode.upper()}")
        if ai_mode == 'face_recognition' or ai_mode == 'lbph':  # Support legacy 'lbph' config
            print("   👤 Face Recognition ONLY (MobileNetV2) - Alert on unknown persons")
        elif ai_mode == 'yolov9':
            print("   ⚠️ Activity Detection ONLY - Monitor suspicious behavior")
        else:
            print("   🛡️ Full Protection - Face recognition (MobileNetV2) + Activity detection")
        
        cap = cv2.VideoCapture(camera_url)
        frame_count = 0
        last_fps_time = time.time()
        fps_counter = 0
        
        # Initialize stats with AI mode
        self.detection_stats[camera_name] = {
            'total_detections': 0,
            'fps': 0,
            'start_time': time.time(),
            'ai_mode': ai_mode
        }
        
        while camera_name in self.active_cameras:
            try:
                ret, frame = cap.read()
                if not ret:
                    print(f"Failed to read from {camera_name}, reconnecting...")
                    cap.release()
                    time.sleep(2)
                    # Attempt to reconnect
                    cap = cv2.VideoCapture(camera_url)
                    if not cap.isOpened():
                        print(f"Reconnection failed for {camera_name}, will retry...")
                        time.sleep(3)
                    continue
                
                frame_count += 1
                fps_counter += 1
                
                # Calculate FPS
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    self.detection_stats[camera_name]['fps'] = fps_counter
                    fps_counter = 0
                    last_fps_time = current_time
                
                # AI Processing (optimized timing)
                processed_data = self.process_frame_ai(frame, camera_name, frame_count)
                
                # Update stats
                if 'detections' in processed_data:
                    self.detection_stats[camera_name]['total_detections'] += len(processed_data['detections'])
                
                # Store latest frame data
                self.latest_frames[camera_name] = processed_data
                
                # Log activities
                self.log_activities(processed_data, camera_name)
                
                # ULTRA increased sleep for maximum performance balance (3 FPS AI processing)
                time.sleep(0.33)  # ~3 FPS for AI processing to eliminate lag spikes
                
            except Exception as e:
                print(f"Camera error {camera_name}: {e}")
                time.sleep(2)
        
        cap.release()
        print(f"🛑 Stopped surveillance for {camera_name}")
    
    def process_frame_ai(self, frame, camera_name, frame_count):
        """AI processing pipeline for each camera - Performance Optimized"""
        
        # Reload AI mode from database every 30 frames (to pick up config changes without restart)
        if frame_count % 30 == 0:
            try:
                from database.models import camera_model
                camera_doc = camera_model.find_by_name(camera_name)
                if camera_doc:
                    new_ai_mode = camera_doc.get('ai_mode', 'both')
                    if camera_name in self.detection_stats:
                        old_mode = self.detection_stats[camera_name].get('ai_mode', 'both')
                        if new_ai_mode != old_mode:
                            self.detection_stats[camera_name]['ai_mode'] = new_ai_mode
                            print(f"🔄 [{camera_name}] AI Mode updated: {old_mode} → {new_ai_mode}")
                
                # ALSO update activity analyzer thresholds to pick up code changes
                if camera_name in self.activity_analyzers:
                    analyzer = self.activity_analyzers[camera_name]
                    if analyzer.speed_threshold != 15.0:
                        old_threshold = analyzer.speed_threshold
                        analyzer.speed_threshold = 15.0
                        print(f"🔄 [{camera_name}] Speed threshold updated: {old_threshold} → 15.0 px/s")
            except Exception as e:
                pass  # Silently continue if reload fails
        
        # Get AI mode for this camera
        ai_mode = self.detection_stats.get(camera_name, {}).get('ai_mode', 'both')
        
        # Performance optimization: Process every Nth frame based on configuration
        if frame_count % self.FRAME_SKIP_INTERVAL != 0:
            # Return cached detection data for skipped frames
            if camera_name in self.latest_frames:
                cached_data = self.latest_frames[camera_name].copy()
                cached_data['annotated_frame'] = self.create_annotated_frame(
                    frame, cached_data.get('detections', []), 
                    cached_data.get('activities', []), camera_name
                )
                return cached_data
        
        # Resize frame for ULTRA fast processing (reduce resolution even more)
        height, width = frame.shape[:2]
        small_frame = cv2.resize(frame, (int(width * 0.3), int(height * 0.3)))
        
        # === YOLOv9 Object Detection (only if ai_mode is 'yolov9' or 'both') ===
        detections = []
        persons = []
        weapons = []
        bags = []
        
        if ai_mode in ['yolov9', 'both']:
            # Object Detection on much smaller frame
            print(f"{'='*60}")
            print(f"🤖 [{camera_name}] YOLOv9 Detection Running...")
            detections = self.detector.detect(small_frame)
            print(f"{'='*60}")
            
            # Scale detection coordinates back to original frame size (adjusted for 0.3 scale)
            for detection in detections:
                bbox = detection['bbox']
                detection['bbox'] = [int(bbox[0] * 3.33), int(bbox[1] * 3.33), 
                                   int(bbox[2] * 3.33), int(bbox[3] * 3.33)]
            
            persons = self.detector.filter_persons(detections)
            weapons = self.detector.filter_weapons(detections)
            bags = self.detector.filter_bags(detections)
        
        # Initialize activities list
        activities = []
        
        # === Activity Analysis (only if ai_mode is 'yolov9' or 'both') ===
        current_time = time.time()
        
        if ai_mode in ['yolov9', 'both']:
            # Update person tracker with detected persons
            tracker = self.person_trackers.get(camera_name)
            activity_analyzer = self.activity_analyzers.get(camera_name)
            
            if tracker and activity_analyzer:
                # Always update tracker with current frame and detections (even if empty)
                # This ensures position_history is maintained when detector temporarily misses persons
                track_states = tracker.update(frame, persons)

                # Analyze tracks for suspicious activities (analyzer will handle empty/partial tracks)
                suspicious_activities = activity_analyzer.analyze_frame(
                    detections=detections,
                    tracks=track_states,
                    current_time=current_time
                )
                
                # Process detected suspicious activities
                for sus_activity in suspicious_activities:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    activity_type = sus_activity.activity_type.value
                    
                    # Save snapshot for suspicious activity
                    snapshot_filename = f"{activity_type}_{camera_name}_{timestamp}.jpg"
                    snapshot_path = os.path.join(SNAPSHOTS_DIR, snapshot_filename)
                    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
                    cv2.imwrite(snapshot_path, frame)
                    
                    # Map activity type to severity
                    severity_map = {
                        'loitering': 'medium',
                        'zone_intrusion': 'high',
                        'running': 'low',
                        'fighting': 'high',
                        'weapon_detected': 'critical',
                        'abandoned_object': 'medium',
                        'crowd_formation': 'medium'
                    }
                    
                    activity = {
                        'type': activity_type,
                        'description': sus_activity.description,
                        'severity': severity_map.get(activity_type, 'medium'),
                        'bbox': None
                    }
                    activities.append(activity)
                    
                    # Send alerts for specific activity types
                    if activity_type == 'loitering':
                        self.alert_manager.send_suspicious_activity_alert(
                            activity_type='loitering',
                            camera_id=camera_name,
                            confidence=sus_activity.confidence,
                            image_path=snapshot_path
                        )
                        self.alert_count += 1
                        print(f"⚠️ LOITERING [Camera_{camera_name}]: {sus_activity.description}")
                        print(f"📸 Snapshot saved: {snapshot_path}")
                        
                    elif activity_type == 'zone_intrusion':
                        self.alert_manager.send_suspicious_activity_alert(
                            activity_type='zone_intrusion',
                            camera_id=camera_name,
                            confidence=sus_activity.confidence,
                            image_path=snapshot_path
                        )
                        self.alert_count += 1
                        print(f"🚨 ZONE INTRUSION [Camera_{camera_name}]: {sus_activity.description}")
                        print(f"📸 Snapshot saved: {snapshot_path}")
                        
                    elif activity_type == 'running':
                        # Send alert to database but not email (low priority activity)
                        self.alert_manager.send_suspicious_activity_alert(
                            activity_type='running',
                            camera_id=camera_name,
                            confidence=sus_activity.confidence,
                            image_path=snapshot_path
                        )
                        self.alert_count += 1
                        print(f"🏃 RUNNING [Camera_{camera_name}]: {sus_activity.description}")
                        print(f"📸 Snapshot saved: {snapshot_path}")
                        
                    elif activity_type == 'fighting':
                        self.alert_manager.send_suspicious_activity_alert(
                            activity_type='fighting',
                            camera_id=camera_name,
                            confidence=sus_activity.confidence,
                            image_path=snapshot_path
                        )
                        self.alert_count += 1
                        print(f"🚨 FIGHTING [Camera_{camera_name}]: {sus_activity.description}")
                        print(f"📸 Snapshot saved: {snapshot_path}")
        
        # === END: Activity Analysis ===
        
        # === Weapon Detection (only if ai_mode is 'yolov9' or 'both') ===
        person_count = len(persons)
        
        if ai_mode in ['yolov9', 'both'] and weapons:
            # Save weapon detection snapshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_filename = f"weapon_{camera_name}_{timestamp}.jpg"
            snapshot_path = os.path.join(SNAPSHOTS_DIR, snapshot_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
            
            # Save the full frame as snapshot
            cv2.imwrite(snapshot_path, frame)
            
            activity = {
                'type': 'weapon',
                'description': f'WEAPON DETECTED: {weapons[0]["class_name"]}',
                'severity': 'critical',
                'bbox': weapons[0]['bbox']
            }
            activities.append(activity)
            
            # Send immediate weapon detection alert with snapshot
            self.alert_manager.send_weapon_detection_alert(
                weapon_type=weapons[0]["class_name"],
                camera_id=camera_name,
                confidence=weapons[0]['confidence'],
                image_path=snapshot_path
            )
            self.alert_count += 1
            print(f"🚨 CRITICAL ALERT [Camera_{camera_name}]: WEAPON DETECTED: {weapons[0]['class_name']}")
            print(f"📸 Weapon snapshot saved: {snapshot_path}")
        
        # === Face Recognition (MobileNetV2 with Unknown Calibration) ===
        authorized_persons_present = False  # Track if authorized persons are detected
        if ai_mode in ['lbph', 'face_recognition', 'both'] and self.face_recognizer.is_trained:
            # Initialize frame counter for this camera if not exists
            if camera_name not in self.frame_counters:
                self.frame_counters[camera_name] = 0
            
            self.frame_counters[camera_name] += 1
            
            # Run face recognition when person is detected OR every Nth frame (based on configuration)
            run_face_recognition = False
            if person_count > 0:
                run_face_recognition = True
            elif self.frame_counters[camera_name] % self.FRAME_SKIP_INTERVAL == 0:
                run_face_recognition = True
            
            if run_face_recognition:
                print(f"{'='*60}")
                print(f"🎥 [{camera_name}] Frame counter: {self.frame_counters[camera_name]}")
                print(f"🔍 Running face detection on frame {self.frame_counters[camera_name]}")
                print(f"🔍 Frame dimensions: {frame.shape}")
                
                # Use MobileNetV2 face recognition with Unknown calibration
                face_names, face_locations, verification_results = self.face_recognizer.recognize_faces_in_frame(frame)
                
                # Convert to expected format (dictionary with bbox, name, confidence, authorization)
                face_results = []
                for i, (name, bbox, is_authorized) in enumerate(zip(face_names, face_locations, verification_results)):
                    # bbox is (top, right, bottom, left) - convert to (x, y, w, h)
                    top, right, bottom, left = bbox
                    x, y, w, h = left, top, right - left, bottom - top
                    
                    face_results.append({
                        'person_name': name,
                        'confidence': 1.0 if is_authorized else 0.5,  # MobileNetV2 doesn't return confidence separately
                        'authorization_status': 'authorized' if is_authorized else 'intruder',
                        'bbox': (x, y, w, h)
                    })
                
                # Debug: Show face recognition results
                print(f"👤 Face Detection for {camera_name}: {len(face_results)} faces detected")
                if len(face_results) > 0:
                    print(f"👤 Face Recognition Results for {camera_name}:")
                    for i, face_result in enumerate(face_results):
                        print(f"   Face {i+1}: {face_result['person_name']} (confidence: {face_result['confidence']:.2f}, status: {face_result['authorization_status']})")
                
                # Check for intruders (unknown faces) - ALWAYS ALERT for unauthorized faces
                authorized_faces = []
                intruder_faces = []
                
                for face_result in face_results:
                    if face_result['authorization_status'] == 'authorized':
                        authorized_faces.append(face_result['person_name'])
                    elif face_result['authorization_status'] == 'intruder':
                        intruder_faces.append(face_result)
                
                # SECURITY FIX: ALWAYS alert for intruders, even if authorized persons are present
                # This prevents unauthorized persons from sneaking in with authorized personnel
                if len(intruder_faces) > 0:
                    # Save intruder snapshot with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    snapshot_filename = f"intruder_{camera_name}_{timestamp}.jpg"
                    snapshot_path = os.path.join(SNAPSHOTS_DIR, snapshot_filename)
                    
                    # Create directory if it doesn't exist
                    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
                    
                    # Save the full frame as snapshot
                    cv2.imwrite(snapshot_path, frame)
                    
                    # Send intruder alert with snapshot (HIGH priority)
                    # Alert message includes whether authorized persons are also present
                    alert_message = f"INTRUDER DETECTED: {len(intruder_faces)} unauthorized person(s) detected"
                    if len(authorized_faces) > 0:
                        alert_message += f" (Authorized personnel also present: {', '.join(set(authorized_faces))})"
                    
                    # Get average confidence of intruder detections
                    avg_confidence = sum(face['confidence'] for face in intruder_faces) / len(intruder_faces) if intruder_faces else 0.0
                    
                    self.alert_manager.send_intruder_alert(
                        person_name="unknown",
                        camera_id=camera_name,
                        confidence=avg_confidence,
                        image_path=snapshot_path
                    )
                    
                    activity = {
                        'type': 'intruder',
                        'description': alert_message,
                        'severity': 'high',
                        'bbox': None
                    }
                    activities.append(activity)
                    self.alert_count += 1
                    
                    print(f"🚨 ALERT [Camera_{camera_name}]: {alert_message}")
                    print(f"📸 Snapshot saved: {snapshot_path}")
                
                # Show authorized faces confirmation
                if len(authorized_faces) > 0:
                    authorized_persons_present = True  # Set flag for later use
                    
                    # Remember ALL authorized persons detected for this camera
                    self.last_authorized_person[camera_name] = {
                        'names': authorized_faces,  # Remember ALL authorized persons (manager_prajwal, owner_rajasekhar, farmer_Basava)
                        'timestamp': datetime.now(),
                        'frames_since_seen': 0
                    }
                    
                    print(f"✅ AUTHORIZED [Camera_{camera_name}]: {', '.join(authorized_faces)} - Access granted")
                    if len(intruder_faces) > 0:
                        print(f"⚠️  SECURITY WARNING: {len(intruder_faces)} INTRUDER(S) detected alongside authorized personnel - ALERT SENT")
                    else:
                        print(f"ℹ️  INFO: Only authorized personnel detected - no alerts")
                elif len(intruder_faces) > 0:
                    # Check if intruder might be authorized person with poor frame quality
                    likely_same_person = False
                    
                    if camera_name in self.last_authorized_person:
                        # If we recently saw authorized person AND intruder confidence is close to threshold
                        # it might just be a poor quality frame of the same authorized person
                        last_auth = self.last_authorized_person[camera_name]
                        for intruder in intruder_faces:
                            # If confidence is within 5 points of threshold (65-70), might be same person
                            if intruder['confidence'] <= 70:  # Close to threshold
                                if last_auth['frames_since_seen'] <= 3:  # Seen very recently (within 3 frames)
                                    likely_same_person = True
                                    last_auth['frames_since_seen'] += 1
                                    persons_str = ', '.join(last_auth['names'])
                                    print(f"⚠️  WARNING: Poor quality frame detected (confidence: {intruder['confidence']:.2f}), likely {persons_str} - grace period (frame {last_auth['frames_since_seen']}/3)")
                                    break
                    
                    if not likely_same_person:
                        print(f"🚨 INTRUDERS ONLY: No authorized personnel detected - intruder alert sent")
                        # Clear last authorized person memory (real intruder detected)
                        if camera_name in self.last_authorized_person:
                            del self.last_authorized_person[camera_name]
                elif person_count > 0:
                    # Person detected but no faces found - check if we recently saw authorized person
                    recently_authorized = False
                    has_previous_memory = camera_name in self.last_authorized_person
                    
                    if has_previous_memory:
                        last_auth = self.last_authorized_person[camera_name]
                        last_auth['frames_since_seen'] += 1
                        
                        # If authorized person seen within last 10 frames (~5 seconds), don't alert
                        if last_auth['frames_since_seen'] <= self.max_frames_without_face:
                            recently_authorized = True
                            # Show ALL authorized persons who were recently seen
                            persons_str = ', '.join(last_auth['names'])
                            print(f"ℹ️  INFO: {persons_str} face(s) temporarily not visible (frame {last_auth['frames_since_seen']}/{self.max_frames_without_face}) - no alert")
                        else:
                            # Too many frames without seeing face, forget this person
                            print(f"🚨 INTRUDER: Person detected but face not visible for {self.max_frames_without_face}+ frames - potential intruder")
                            del self.last_authorized_person[camera_name]
                            
                            # Send intruder alert (person was authorized but face hidden too long)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            snapshot_filename = f"intruder_{camera_name}_{timestamp}.jpg"
                            snapshot_path = os.path.join(SNAPSHOTS_DIR, snapshot_filename)
                            
                            # Create directory if it doesn't exist
                            os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
                            
                            # Save the full frame as snapshot
                            cv2.imwrite(snapshot_path, frame)
                            
                            # Send intruder alert (face not visible = suspicious)
                            self.alert_manager.send_intruder_alert(
                                person_name="hidden_face",
                                camera_id=camera_name,
                                confidence=0.0,
                                image_path=snapshot_path
                            )
                    else:
                        # No previous memory - face detection will handle this on next frame
                        # Don't alert immediately, give face detection a chance to work
                        print(f"ℹ️  INFO: Person detected, waiting for face detection (no previous authorization data)")
                
                # Close face recognition section (only when face detection actually ran)
                print(f"{'='*60}")
        
        # Crowd detection (always alert for large groups regardless of authorization)
        if person_count > 3:
            # Save crowd snapshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_filename = f"crowd_alert_{camera_name}_{timestamp}.jpg"
            snapshot_path = os.path.join(SNAPSHOTS_DIR, snapshot_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
            
            # Save the full frame as snapshot
            cv2.imwrite(snapshot_path, frame)
            
            activity = {
                'type': 'crowd',
                'description': f'CROWD ALERT: {person_count} persons detected',
                'severity': 'medium',
                'bbox': None
            }
            activities.append(activity)
            self.alert_count += 1
            
            # Send crowd alert email
            try:
                self.alert_manager.send_suspicious_activity_alert(
                    activity_type='crowd_formation',
                    camera_id=camera_name,
                    confidence=0.95,
                    image_path=snapshot_path,
                    details={'person_count': person_count}
                )
                print(f"📧 Crowd alert email sent: {person_count} persons detected")
            except Exception as e:
                print(f"❌ Failed to send crowd alert email: {e}")
        
        if person_count == 0 and len(bags) > 0:
            # Save abandoned object snapshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_filename = f"abandoned_object_{camera_name}_{timestamp}.jpg"
            snapshot_path = os.path.join(SNAPSHOTS_DIR, snapshot_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
            
            # Save the full frame as snapshot
            cv2.imwrite(snapshot_path, frame)
            
            activity = {
                'type': 'abandoned_object',
                'description': f'ABANDONED OBJECT: Unattended bag/item detected',
                'severity': 'medium',
                'bbox': bags[0]['bbox']
            }
            activities.append(activity)
            
            # Send suspicious activity alert with snapshot
            self.alert_manager.send_suspicious_activity_alert(
                activity_type='abandoned_object',
                camera_id=camera_name,
                confidence=bags[0]['confidence'],
                image_path=snapshot_path
            )
            self.alert_count += 1
            print(f"⚠️ WARNING [Camera_{camera_name}]: ABANDONED OBJECT: Unattended bag/item detected")
            print(f"📸 Object snapshot saved: {snapshot_path}")
        
        # Multi-camera correlation
        if len(detections) > 10:
            activities.append({
                'type': 'high_activity',
                'description': f'HIGH ACTIVITY: {len(detections)} objects in view',
                'severity': 'low',
                'bbox': None
            })
        
        # Create annotated frame
        annotated_frame = self.create_annotated_frame(frame, detections, activities, camera_name)
        
        # Add blank line after each camera's processing
        print()
        
        return {
            'original_frame': frame,
            'annotated_frame': annotated_frame,
            'detections': detections,
            'persons': persons,
            'weapons': weapons,
            'bags': bags,
            'activities': activities,
            'timestamp': time.time()
        }
    
    def create_annotated_frame(self, frame, detections, activities, camera_name):
        """Create frame with AI annotations"""
        annotated = frame.copy()
        
        # Draw detections
        for detection in detections:
            bbox = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # Color coding
            if class_name == 'person':
                color = (0, 255, 0)  # Green
            elif detection['class_id'] in [34, 43, 76]:  # Weapons
                color = (0, 0, 255)  # Red
            elif class_name in ['backpack', 'handbag', 'suitcase']:
                color = (255, 165, 0)  # Orange
            else:
                color = (255, 255, 0)  # Yellow
            
            # Draw bounding box
            cv2.rectangle(annotated, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Draw label
            label = f"{class_name} {confidence:.2f}"
            cv2.putText(annotated, label, (bbox[0], bbox[1]-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw activity alerts
        y_offset = 30
        for activity in activities:
            if activity['severity'] == 'critical':
                color = (0, 0, 255)  # Red
                prefix = "CRITICAL"
            elif activity['severity'] == 'medium':
                color = (0, 165, 255)  # Orange
                prefix = "ALERT"
            else:
                color = (255, 255, 0)  # Yellow
                prefix = "INFO"
            
            alert_text = f"{prefix}: {activity['description']}"
            cv2.putText(annotated, alert_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_offset += 25
        
        # Camera info overlay
        info_text = f"{camera_name} | Objects: {len(detections)} | {datetime.now().strftime('%H:%M:%S')}"
        cv2.putText(annotated, info_text, (10, annotated.shape[0]-15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated
    
    def log_activities(self, processed_data, camera_name):
        """Log activities from all cameras"""
        activities = processed_data.get('activities', [])
        detections = processed_data.get('detections', [])
        
        # Log detection summary every 30 seconds
        if len(detections) > 0 and int(time.time()) % 30 == 0:
            persons_count = len(processed_data.get('persons', []))
            log_entry = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'camera': camera_name,
                'description': f"Monitoring: {len(detections)} objects, {persons_count} persons",
                'is_alert': False,
                'is_warning': False,
                'is_info': True
            }
            self.activity_logs.append(log_entry)
        
        # Log specific activities
        for activity in activities:
            log_entry = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'camera': camera_name,
                'description': activity['description'],
                'severity': activity['severity'],
                'is_alert': activity['severity'] in ['high', 'critical'],
                'is_warning': activity['severity'] == 'medium',
                'is_info': activity['severity'] == 'low'
            }
            
            self.activity_logs.append(log_entry)
            
            if log_entry['is_alert']:
                self.alert_count += 1
                print(f"🚨 ALERT [{camera_name}]: {activity['description']}")
            elif log_entry['is_warning']:
                print(f"⚠️ WARNING [{camera_name}]: {activity['description']}")
        
        # Keep recent logs
        if len(self.activity_logs) > 500:
            self.activity_logs = self.activity_logs[-500:]
    
    def start_camera_surveillance(self, camera_name):
        """Start surveillance on specific camera"""
        if camera_name in self.active_cameras:
            print(f"⚠️ {camera_name} already active")
            return
        
        camera_info = self.camera_urls[camera_name]
        self.active_cameras[camera_name] = True
        
        thread = threading.Thread(
            target=self.process_camera_feed,
            args=(camera_name, camera_info),
            daemon=True
        )
        thread.start()
        print(f"✅ Started surveillance on {camera_name}")
    
    def stop_camera_surveillance(self, camera_name):
        """Stop surveillance on specific camera"""
        if camera_name in self.active_cameras:
            del self.active_cameras[camera_name]
            if camera_name in self.latest_frames:
                del self.latest_frames[camera_name]
            print(f"🛑 Stopped surveillance on {camera_name}")
    
    def start_all_surveillance(self):
        """Start surveillance on all detected cameras"""
        print("🚀 Starting AI surveillance on ALL cameras...")
        
        for camera_name in self.camera_urls.keys():
            self.start_camera_surveillance(camera_name)
        
        print(f"🎯 Multi-camera surveillance active on {len(self.active_cameras)} cameras")
        
        # Start automatic camera discovery
        self.start_camera_discovery()
    
    def start_camera_discovery(self):
        """Start background thread to automatically detect new cameras"""
        if not self.discovery_running:
            self.discovery_running = True
            self.discovery_thread = threading.Thread(
                target=self._camera_discovery_loop,
                daemon=True
            )
            self.discovery_thread.start()
            print(f"🔍 Auto-discovery started: Checking for new cameras every {self.camera_discovery_interval} seconds")
    
    def stop_all_surveillance(self):
        """Stop surveillance on all cameras"""
        print("🛑 Stopping all camera surveillance...")
        
        # Stop auto-discovery first
        self.stop_camera_discovery()
        
        camera_names = list(self.active_cameras.keys())
        for camera_name in camera_names:
            self.stop_camera_surveillance(camera_name)
        print("✅ All camera surveillance stopped")
    
    def _camera_discovery_loop(self):
        """Background loop to check for new cameras"""
        while self.discovery_running:
            try:
                time.sleep(self.camera_discovery_interval)
                
                # Get current camera list from database (silent mode to reduce spam)
                new_cameras = self.auto_detect_cameras(silent=True)
                
                # Check for new cameras not in current list
                for camera_name, camera_info in new_cameras.items():
                    if camera_name not in self.camera_urls:
                        # New camera detected!
                        print(f"\n🆕 NEW CAMERA DETECTED: {camera_name}")
                        self.camera_urls[camera_name] = camera_info
                        
                        # Get AI mode
                        ai_mode = camera_info.get('ai_mode', 'both') if isinstance(camera_info, dict) else 'both'
                        
                        # Initialize tracker and activity analyzer for new camera
                        self.person_trackers[camera_name] = PersonTracker(
                            tracker_type='KCF',
                            max_tracks=20,
                            track_timeout=5.0
                        )
                        self.activity_analyzers[camera_name] = SuspiciousActivityAnalyzer(
                            loitering_threshold=30.0,
                            abandoned_object_threshold=60.0,
                            speed_threshold=150.0,
                            crowd_threshold=5
                        )
                        
                        # Add default detection zone
                        default_zone = DetectionZone(
                            name=f"{camera_name}_main_area",
                            points=[(0, 0), (1920, 0), (1920, 1080), (0, 1080)],
                            zone_type="monitored",
                            activity_types=[
                                ActivityType.LOITERING,
                                ActivityType.ZONE_INTRUSION,
                                ActivityType.RUNNING,
                                ActivityType.ABANDONED_OBJECT,
                                ActivityType.WEAPON_DETECTED
                            ]
                        )
                        self.activity_analyzers[camera_name].add_detection_zone(default_zone)
                        
                        # Store AI mode in detection stats
                        self.detection_stats[camera_name] = {
                            'ai_mode': ai_mode,
                            'detections': 0,
                            'alerts': 0
                        }
                        
                        # Start surveillance on new camera
                        self.start_camera_surveillance(camera_name)
                        print(f"✅ Started surveillance on new camera: {camera_name}")
                        print(f"   🤖 AI Mode: {ai_mode.upper()}")
                
                # Check for removed cameras
                for camera_name in list(self.camera_urls.keys()):
                    if camera_name not in new_cameras:
                        print(f"\n🔴 CAMERA REMOVED: {camera_name}")
                        self.stop_camera_surveillance(camera_name)
                        del self.camera_urls[camera_name]
                        
            except Exception as e:
                print(f"⚠️ Camera discovery error: {e}")
                
    def stop_camera_discovery(self):
        """Stop automatic camera discovery"""
        self.discovery_running = False
        if self.discovery_thread:
            self.discovery_thread.join(timeout=2)
        print("🛑 Auto-discovery stopped")
    
    def run(self, host='0.0.0.0', port=8001):
        """Run the multi-camera surveillance system"""
        print(f"🌐 Multi-Camera Surveillance Dashboard: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔍 MULTI-CAMERA AI SURVEILLANCE SYSTEM - STARTING...")
    print("=" * 70)
    
    # Create multi-camera surveillance system
    surveillance = MultiCameraAISurveillance()
    
    print("\n" + "=" * 70)
    print("✅ SYSTEM READY")
    print("=" * 70)
    print("📊 System Configuration:")
    print(f"   📹 Cameras Detected: {len(surveillance.camera_urls)}")
    print(f"   🤖 AI Detection: YOLOv9 + MobileNetV2 Face Recognition")
    print(f"   🚨 Email Alerts: {'✅ Enabled' if surveillance.alert_manager.email_service.enabled else '❌ Disabled'}")
    print(f"   🎯 Activity Detection: Loitering | Intrusion | Running | Objects")
    print(f"   ⚙️  Frame Processing: Every {surveillance.FRAME_SKIP_INTERVAL} frames")
    print("=" * 70)
    
    try:
        # Auto-start surveillance on all cameras
        print("\n🚀 Starting surveillance on all cameras...")
        surveillance.start_all_surveillance()
        print(f"✅ {len(surveillance.active_cameras)} camera(s) active")
        
        # Launch web dashboard
        print(f"\n🌐 Web Dashboard: http://0.0.0.0:8001")
        print("=" * 70)
        surveillance.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down multi-camera surveillance...")
        surveillance.stop_all_surveillance()
        print("✅ System shutdown complete")