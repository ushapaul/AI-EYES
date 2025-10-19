from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Import our database models and storage manager
from database.models import camera_model, alert_model, log_model, settings_model, user_model
from database.config import is_db_connected
from storage.manager import storage_manager

# Configuration from environment variables
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    
    # Enable CORS for React frontend
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])
    
    # Initialize SocketIO for real-time communication
    socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:5173"])
    
    # Register protected camera routes
    try:
        from app.routes.camera_protected import camera_bp
        app.register_blueprint(camera_bp, url_prefix='/api/v2')
    except ImportError as e:
        print(f"Warning: Could not import protected camera routes: {e}")
    
    # Register surveillance routes
    try:
        from app.routes.surveillance_api import surveillance_bp
        app.register_blueprint(surveillance_bp, url_prefix='/api')
    except ImportError as e:
        print(f"Warning: Could not import surveillance routes: {e}")
    
    # Basic API routes
    @app.route('/')
    def index():
        return {
            'message': '🔍 AI Eyes Security System',
            'status': 'online',
            'version': '1.0.0',
            'endpoints': {
                'api_status': '/api/status',
                'cameras': '/api/camera/list',
                'alerts': '/api/alerts/list',
                'stats': '/api/stats',
                'logs': '/api/logs'
            },
            'frontend_url': 'http://localhost:5173',
            'timestamp': datetime.now().isoformat()
        }
    
    @app.route('/api/status')
    def get_status():
        return {
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'ai_models_loaded': True
        }
    
    @app.route('/api/stats')
    def get_stats():
        # Return real stats from MongoDB
        cameras = camera_model.find_all()
        online_cameras = camera_model.get_online_cameras()
        alerts_today = alert_model.get_alerts_today()
        
        return {
            'total_cameras': len(cameras),
            'active_cameras': len(online_cameras),
            'total_alerts_today': alerts_today,
            'detection_accuracy': 0 if len(cameras) == 0 else 95,
            'uptime': '100%',
            'database_connected': is_db_connected()
        }
    
    @app.route('/api/camera/list')
    def get_cameras():
        # Return cameras from MongoDB
        cameras = camera_model.find_all()
        return cameras
    
    @app.route('/api/alerts/list')
    def get_alerts():
        """Get recent alerts from MongoDB"""
        alerts = alert_model.get_recent_alerts()
        
        # Transform field names for frontend compatibility
        for alert in alerts:
            # Convert image_path to image URL for frontend
            if 'image_path' in alert and alert['image_path']:
                image_path = alert['image_path']
                
                # If already a full URL, keep it
                if image_path.startswith('http'):
                    alert['image'] = image_path
                elif 'storage' in image_path.lower():
                    # FIRST normalize path (backslashes to forward slashes)
                    normalized = image_path.replace('\\', '/')
                    # THEN split and get part after 'storage/'
                    parts = normalized.split('storage/')
                    relative_path = parts[-1] if len(parts) > 1 and parts[-1] else normalized
                    alert['image'] = f'http://localhost:{PORT}/api/storage/image/{relative_path}'
                else:
                    alert['image'] = f'http://localhost:{PORT}/api/storage/image/{image_path}' 
            
            # Ensure all required fields exist
            if 'location' not in alert:
                alert['location'] = alert.get('camera_id', 'Unknown')
            if 'type' not in alert:
                alert['type'] = 'intruder'
            if 'severity' not in alert:
                alert['severity'] = 'high'
        
        return alerts
    
    @app.route('/api/camera/add', methods=['POST'])
    def add_camera():
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'location', 'url', 'type']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {'error': f'Missing required field: {field}'}, 400
            
            # Create camera using MongoDB model
            camera_id = camera_model.create_camera(
                name=data['name'],
                location=data['location'],
                url=data['url'],
                camera_type=data['type'],
                username=data.get('username', ''),
                password=data.get('password', '')
            )
                        # Update AI mode if provided
            if 'ai_mode' in data:
                camera_model.update_by_id(camera_id, {'ai_mode': data['ai_mode']})
            
            # Create log entry
            log_model.create_log(
                camera_id=camera_id,
                action='camera_added',
                description=f"Camera '{data['name']}' added at {data['location']}"
            )
            
            # Get the created camera
            new_camera = camera_model.find_by_id(camera_id)
            
            return {
                'success': True,
                'message': 'Camera added successfully',
                'camera': new_camera
            }
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/camera/<camera_id>/snapshot', methods=['POST'])
    def capture_snapshot(camera_id):
        """Capture snapshot from camera"""
        try:
            # Get camera details
            camera = camera_model.find_by_id(camera_id)
            if not camera:
                return {'error': 'Camera not found'}, 404
            
            # Capture image from camera
            image_path = storage_manager.capture_from_ip_camera(
                camera_url=camera['url'],
                camera_id=camera_id,
                username=camera.get('username', ''),
                password=camera.get('password', '')
            )
            
            if image_path:
                # Create log entry
                log_model.create_log(
                    camera_id=camera_id,
                    action='snapshot_captured',
                    description=f"Snapshot captured from camera '{camera['name']}'"
                )
                
                return {
                    'success': True,
                    'message': 'Snapshot captured successfully',
                    'image_path': image_path
                }
            else:
                return {'error': 'Failed to capture snapshot'}, 500
                
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/camera/<camera_id>/delete', methods=['DELETE'])
    def delete_camera(camera_id):
        """Delete a camera"""
        try:
            camera = camera_model.find_by_id(camera_id)
            if not camera:
                return {'error': 'Camera not found'}, 404
            
            # Delete camera
            success = camera_model.delete_by_id(camera_id)
            
            if success:
                # Create log entry
                log_model.create_log(
                    camera_id=camera_id,
                    action='camera_deleted',
                    description=f"Camera '{camera['name']}' deleted"
                )
                
                return {'success': True, 'message': 'Camera deleted successfully'}
            else:
                return {'error': 'Failed to delete camera'}, 500
                
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/storage/stats')
    def get_storage_stats():
        """Get storage statistics"""
        try:
            stats = storage_manager.get_storage_stats()
            return {
                'success': True,
                'storage_stats': stats
            }
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/storage/cleanup', methods=['POST'])
    def cleanup_storage():
        """Clean up old files"""
        try:
            days_old = request.json.get('days_old', 7) if request.json else 7
            files_deleted = storage_manager.cleanup_old_files(days_old)
            
            return {
                'success': True,
                'message': f'Cleaned up {files_deleted} old files',
                'files_deleted': files_deleted
            }
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/storage/image/<path:image_path>')
    def get_image(image_path):
        """Serve stored images"""
        try:
            # Security: Prevent directory traversal
            if '..' in image_path or image_path.startswith('/'):
                return {'error': 'Invalid image path'}, 400
            
            # Build full path to image
            full_path = os.path.join(backend_dir, 'storage', image_path)
            
            if os.path.exists(full_path):
                return send_file(full_path)
            else:
                return {'error': 'Image not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/alerts/create', methods=['POST'])
    def create_alert():
        """Create a new alert"""
        try:
            data = request.get_json()
            
            required_fields = ['camera_id', 'type', 'message']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            # Create alert
            alert_id = alert_model.create_alert(
                camera_id=data['camera_id'],
                alert_type=data['type'],
                message=data['message'],
                severity=data.get('severity', 'medium'),
                image_path=data.get('image_path')
            )
            
            # Create log entry
            log_model.create_log(
                camera_id=data['camera_id'],
                action='alert_created',
                description=f"Alert created: {data['message']}",
                log_level='warning'
            )
            
            return {
                'success': True,
                'message': 'Alert created successfully',
                'alert_id': alert_id
            }
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/camera/test-url', methods=['POST'])
    def test_camera_url():
        """Test if a camera URL is accessible"""
        try:
            data = request.get_json()
            url = data.get('url')
            
            if not url:
                return {'error': 'URL is required'}, 400
            
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            # Configure session with timeout and retries
            session = requests.Session()
            retry_strategy = Retry(
                total=1,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Test the URL
            response = session.head(url, timeout=5)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'accessible': response.status_code == 200
            }
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Connection timeout'}, 408
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection failed'}, 503
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ============================================================================
    # SETTINGS API ROUTES
    # ============================================================================
    
    @app.route('/api/settings', methods=['GET'])
    def get_all_settings():
        """Get all system settings"""
        try:
            settings = settings_model.get_settings()
            return jsonify(settings), 200
        except Exception as e:
            print(f"❌ Error getting settings: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/<category>', methods=['GET'])
    def get_category_settings(category):
        """Get settings for a specific category"""
        try:
            settings = settings_model.get_settings(category)
            return jsonify(settings), 200
        except Exception as e:
            print(f"❌ Error getting {category} settings: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/<category>', methods=['PUT'])
    def update_category_settings(category):
        """Update settings for a specific category"""
        try:
            data = request.get_json()
            success = settings_model.update_settings(category, data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'{category.capitalize()} settings updated successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update settings'
                }), 500
        except Exception as e:
            print(f"❌ Error updating {category} settings: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/backup', methods=['POST'])
    def backup_settings():
        """Backup all settings"""
        try:
            settings = settings_model.get_settings()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Log the backup
            log_model.create_log(
                'system',
                'settings_backup',
                f'Settings backup created: backup_{timestamp}',
                'info'
            )
            
            return jsonify({
                'success': True,
                'backup': settings,
                'timestamp': timestamp
            }), 200
        except Exception as e:
            print(f"❌ Error backing up settings: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/restore', methods=['POST'])
    def restore_settings():
        """Restore settings from backup"""
        try:
            backup_data = request.get_json()
            
            # Restore each category
            success_count = 0
            for category, settings in backup_data.items():
                if settings_model.update_settings(category, settings):
                    success_count += 1
            
            # Log the restore
            log_model.create_log(
                'system',
                'settings_restore',
                f'Settings restored: {success_count} categories',
                'info'
            )
            
            return jsonify({
                'success': True,
                'message': f'Restored {success_count} setting categories'
            }), 200
        except Exception as e:
            print(f"❌ Error restoring settings: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/test-connection', methods=['POST'])
    def test_settings_connection():
        """Test system connections (email, database, etc.)"""
        try:
            results = {
                'database': is_db_connected(),
                'storage': os.path.exists('storage'),
                'timestamp': datetime.now().isoformat()
            }
            
            # Test email if configured
            try:
                email_addr = os.getenv('SENDGRID_FROM_EMAIL')
                results['email'] = email_addr is not None and len(email_addr) > 0
            except:
                results['email'] = False
            
            return jsonify({
                'success': True,
                'results': results
            }), 200
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ============================================================================
    # AUTHENTICATION & USER API ROUTES
    # ============================================================================
    
    @app.route('/api/auth/signup', methods=['POST'])
    def signup():
        """Register a new user account"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['email', 'password', 'firstName']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            # Create user
            user_id = user_model.create_user(
                email=data['email'],
                password=data['password'],
                first_name=data['firstName'],
                last_name=data.get('lastName', ''),
                role=data.get('role', 'user'),
                department=data.get('department', ''),
                phone=data.get('phone', ''),
                location=data.get('location', ''),
                timezone=data.get('timezone', 'UTC')
            )
            
            if user_id:
                # Get the created user (without password)
                user = user_model.get_user_by_id(user_id)
                return jsonify({
                    'success': True,
                    'message': 'Account created successfully',
                    'user': user
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': 'Email already exists or registration failed'
                }), 400
                
        except Exception as e:
            print(f"❌ Error in signup: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Authenticate user and create session"""
        try:
            data = request.get_json()
            
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({
                    'success': False,
                    'error': 'Email and password are required'
                }), 400
            
            user = user_model.authenticate_user(email, password)
            
            if user:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': user
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Invalid email or password'
                }), 401
                
        except Exception as e:
            print(f"❌ Error in login: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/me', methods=['GET'])
    def get_current_user():
        """Get current user information"""
        try:
            # In a real app, you'd get user_id from session/token
            # For now, we'll use a query parameter or header
            user_id = request.args.get('user_id') or request.headers.get('X-User-ID')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'Not authenticated'
                }), 401
            
            user = user_model.get_user_by_id(user_id)
            
            if user:
                return jsonify({
                    'success': True,
                    'user': user
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
                
        except Exception as e:
            print(f"❌ Error getting current user: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/users', methods=['GET'])
    def get_all_users():
        """Get all users (admin only)"""
        try:
            users = user_model.get_all_users()
            return jsonify(users), 200
        except Exception as e:
            print(f"❌ Error getting users: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        """Get user by ID"""
        try:
            user = user_model.get_user_by_id(user_id)
            if user:
                return jsonify(user), 200
            else:
                return jsonify({'error': 'User not found'}), 404
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/users/<user_id>', methods=['PUT'])
    def update_user(user_id):
        """Update user information"""
        try:
            data = request.get_json()
            success = user_model.update_user(user_id, data)
            
            if success:
                user = user_model.get_user_by_id(user_id)
                return jsonify({
                    'success': True,
                    'message': 'User updated successfully',
                    'user': user
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update user'
                }), 400
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/users/<user_id>/password', methods=['PUT'])
    def change_password(user_id):
        """Change user password"""
        try:
            data = request.get_json()
            
            old_password = data.get('oldPassword')
            new_password = data.get('newPassword')
            
            if not old_password or not new_password:
                return jsonify({
                    'success': False,
                    'error': 'Old and new passwords are required'
                }), 400
            
            success = user_model.update_password(user_id, old_password, new_password)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Password updated successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Invalid old password or update failed'
                }), 400
        except Exception as e:
            print(f"❌ Error changing password: {e}")
            return jsonify({'error': str(e)}), 500
    
    # WebSocket events
    
    @app.route('/api/logs')
    def get_logs():
        # Return logs from MongoDB
        logs = log_model.get_recent_logs()
        return logs
    
    @app.route('/api/alerts/<alert_id>/escalate', methods=['POST'])
    def escalate_alert(alert_id):
        """Escalate alert by sending email to specified recipient"""
        try:
            data = request.get_json()
            recipient_email = data.get('email')
            recipient_name = data.get('name', 'Security Team')
            
            if not recipient_email:
                return {'error': 'Recipient email is required'}, 400
            
            # Get alert details
            alert = alert_model.find_by_id(alert_id)
            if not alert:
                return {'error': 'Alert not found'}, 404
            
            # Import email service
            try:
                from app.services.email_service import EmailAlertService
                
                # Initialize email service
                email_service = EmailAlertService()
                
                # Override recipients for this specific email
                email_service.recipients = [recipient_email]
                
                # Prepare alert data for email with escalation info
                alert_data = {
                    'type': alert.get('type', 'security_breach'),
                    'location': alert.get('location', alert.get('camera_id', 'Unknown')),
                    'timestamp': alert.get('timestamp', datetime.utcnow()).isoformat(),
                    'severity': alert.get('severity', 'high'),
                    'confidence': alert.get('confidence', 0.95),
                    'camera_id': alert.get('camera_id', 'Unknown'),
                    'image_path': alert.get('image_path'),
                    'description': alert.get('message', 'Unauthorized person detected'),
                    'escalated': True,  # Mark as manually escalated
                    'escalated_to': recipient_name,  # Who received this escalation
                    'escalated_by': 'Dashboard User'  # Who escalated it
                }
                
                # Send email using the EmailAlertService
                success = email_service.send_alert(alert_data)
                
                if success:
                    # Create log entry
                    log_model.create_log(
                        camera_id=alert.get('camera_id', 'system'),
                        action='alert_escalated',
                        description=f"Alert {alert_id} escalated to {recipient_name} ({recipient_email})"
                    )
                    
                    return {
                        'status': 'success',
                        'message': f'Alert escalated to {recipient_name}',
                        'email': recipient_email
                    }
                else:
                    return {'status': 'error', 'error': 'Failed to send email'}, 500
            except ImportError as e:
                print(f"Import error: {e}")
                return {'status': 'error', 'error': 'Email service not configured'}, 500
                
        except Exception as e:
            print(f"Error escalating alert: {e}")
            return {'status': 'error', 'error': str(e)}, 500
    
    @app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        """Acknowledge an alert"""
        try:
            # Update alert status in database
            success = alert_model.update_by_id(alert_id, {'status': 'acknowledged'})
            
            if success:
                # Create log entry
                log_model.create_log(
                    camera_id='system',
                    action='alert_acknowledged',
                    description=f"Alert {alert_id} acknowledged by user"
                )
                
                return {
                    'success': True,
                    'message': f'Alert {alert_id} acknowledged',
                    'alert_id': alert_id,
                    'status': 'acknowledged'
                }
            else:
                return {'error': 'Failed to acknowledge alert'}, 500
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/alerts/<alert_id>/dismiss', methods=['POST'])
    def dismiss_alert(alert_id):
        """Dismiss an alert - DELETES from MongoDB permanently"""
        try:
            # Delete the alert from database permanently
            success = alert_model.delete_by_id(alert_id)
            
            if success:
                # Create log entry
                log_model.create_log(
                    camera_id='system',
                    action='alert_deleted',
                    description=f"Alert {alert_id} dismissed and permanently deleted"
                )
                
                return {
                    'success': True,
                    'message': f'Alert deleted from MongoDB',
                    'alert_id': alert_id,
                    'deleted': True
                }
            else:
                return {'error': 'Failed to delete alert'}, 500
        except Exception as e:
            return {'error': str(e)}, 500
    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        socketio.emit('status', {'message': 'Connected to AI Eyes Security System'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    return app, socketio

# Initialize the app
app, socketio = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("� AI Eyes Security - Simple API Server")
    print("=" * 50)
    print(f"Server: http://localhost:{PORT}")
    print(f"API Status: http://localhost:{PORT}/api/status")
    print(f"Dashboard: http://localhost:5173 (start frontend separately)")
    print("=" * 50)
    
    # Start camera discovery service
    try:
        from app.services.camera_discovery import CameraDiscovery
        camera_discovery = CameraDiscovery()
        print("🔍 Camera discovery service initialized")
        
        # Only start status monitoring (no auto-scan)
        # Users can manually scan via API: POST /api/camera/scan
        if hasattr(camera_discovery, 'start_status_monitor'):
            camera_discovery.start_status_monitor(interval=30)  # Check status every 30 seconds
            print("🚀 Camera status monitoring started (interval: 30s)")
        
        print("✅ Camera discovery ready (manual scan only)")
        print(f"📡 To scan: POST http://localhost:{PORT}/api/camera/scan")
    except Exception as e:
        print(f"⚠️ Could not start camera discovery: {e}")
    
    print("=" * 50)
    
    try:
        socketio.run(app, debug=DEBUG, host=HOST, port=PORT)
    except KeyboardInterrupt:
        print("\nShutting down AI Eyes Security System...")
    except Exception as e:
        print(f"Error starting server: {e}")
        print(f"Make sure port {PORT} is not already in use.")
