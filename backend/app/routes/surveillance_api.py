"""
Surveillance API Routes
Flask routes for surveillance system integration
"""

from flask import Blueprint, request, jsonify, send_file
import cv2
import numpy as np
import base64
import io
import time
import threading
from typing import Dict, List, Optional
import logging

from surveillance.surveillance_manager import SurveillanceManager
from surveillance.activity_analyzer import DetectionZone, ActivityType, SuspiciousActivity
from surveillance.alert_manager import AlertManager
from database.models import camera_model, alert_model, log_model
from storage.manager import storage_manager

logger = logging.getLogger(__name__)

# Create blueprint
surveillance_bp = Blueprint('surveillance', __name__)

# Global surveillance managers (one per camera)
surveillance_managers: Dict[str, SurveillanceManager] = {}
alert_manager: Optional[AlertManager] = None

def init_alert_manager():
    """Initialize alert manager"""
    global alert_manager
    if alert_manager is None:
        alert_manager = AlertManager(
            email_user="your-email@gmail.com",  # Configure from environment
            email_password="your-app-password",  # Configure from environment
            alert_emails=["security@company.com"]  # Configure from environment
        )
        
        # Set callbacks
        alert_manager.set_database_callback(log_alert_to_database)
        alert_manager.start()
        logger.info("Alert manager initialized")

def log_alert_to_database(alert_data: Dict):
    """Log alert to database"""
    try:
        # Create alert record
        alert_record = {
            'type': alert_data['activity_type'],
            'severity': alert_data['threat_level'],
            'location': alert_data['zone_name'],
            'description': alert_data['description'],
            'confidence': alert_data['confidence'],
            'camera_id': alert_data['camera_id'],
            'image_path': alert_data.get('snapshot_path', ''),
            'metadata': {
                'track_id': alert_data['track_id'],
                'evidence': alert_data['evidence'],
                'coordinates': alert_data['location']
            }
        }
        
        alert_model.create(alert_record)
        
        # Create log entry
        log_entry = {
            'event': f"Suspicious Activity: {alert_data['activity_type']}",
            'location': alert_data['zone_name'],
            'confidence': alert_data['confidence'],
            'action': 'alert_generated',
            'metadata': alert_data
        }
        
        log_model.create(log_entry)
        
        logger.info(f"Alert logged to database: {alert_data['alert_id']}")
        
    except Exception as e:
        logger.error(f"Database logging failed: {e}")

@surveillance_bp.route('/surveillance/status', methods=['GET'])
def get_surveillance_status():
    """Get surveillance system status"""
    try:
        # Get all cameras
        cameras = camera_model.find_all()
        
        status = {
            'active_cameras': len([cam for cam in cameras if cam.get('enabled', True)]),
            'surveillance_active': len(surveillance_managers) > 0,
            'managers': {}
        }
        
        # Get status for each active manager
        for camera_id, manager in surveillance_managers.items():
            stats = manager.get_statistics()
            status['managers'][camera_id] = {
                'running': manager.is_running,
                'fps': stats.get('processing_fps', 0),
                'frames_processed': stats.get('frames_processed', 0),
                'active_tracks': stats.get('active_tracks', 0),
                'recent_activities': stats.get('recent_activities', 0)
            }
        
        # Alert manager status
        if alert_manager:
            alert_stats = alert_manager.get_statistics()
            status['alert_manager'] = {
                'running': alert_manager.is_running,
                'total_alerts': alert_stats['total_alerts'],
                'emails_sent': alert_stats['emails_sent']
            }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Surveillance status error: {e}")
        return jsonify({'error': str(e)}), 500

@surveillance_bp.route('/surveillance/start/<camera_id>', methods=['POST'])
def start_surveillance(camera_id: str):
    """Start surveillance for specific camera"""
    try:
        # Initialize alert manager if needed
        init_alert_manager()
        
        # Get camera details
        camera = camera_model.find_by_id(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        # Check if already running
        if camera_id in surveillance_managers:
            return jsonify({'error': 'Surveillance already running for this camera'}), 400
        
        # Create surveillance manager
        manager = SurveillanceManager(
            camera_url=camera['url'],
            output_dir=f"surveillance_output/{camera_id}",
            known_faces_dir="data/known_faces"
        )
        
        # Set up activity callback
        def on_activity(activity: SuspiciousActivity):
            try:
                # Get current frame for snapshot
                result = manager.get_latest_result()
                frame = result.get('output_frame') if result else None
                
                # Process alert
                alert_manager.process_activity(activity, frame)
                
            except Exception as e:
                logger.error(f"Activity callback error: {e}")
        
        manager.set_activity_callback(on_activity)
        
        # Add default detection zones (can be customized later)
        default_zones = get_default_detection_zones(camera)
        for zone in default_zones:
            manager.add_detection_zone(zone)
        
        # Start surveillance
        if manager.start_surveillance():
            surveillance_managers[camera_id] = manager
            
            # Log start event
            log_model.create({
                'event': 'Surveillance Started',
                'location': camera['location'],
                'confidence': 1.0,
                'action': 'system_start',
                'metadata': {'camera_id': camera_id}
            })
            
            return jsonify({
                'success': True,
                'message': f'Surveillance started for camera {camera_id}',
                'camera_name': camera['name']
            })
        else:
            return jsonify({'error': 'Failed to start surveillance'}), 500
            
    except Exception as e:
        logger.error(f"Start surveillance error: {e}")
        return jsonify({'error': str(e)}), 500

@surveillance_bp.route('/surveillance/stop/<camera_id>', methods=['POST'])
def stop_surveillance(camera_id: str):
    """Stop surveillance for specific camera"""
    try:
        if camera_id not in surveillance_managers:
            return jsonify({'error': 'Surveillance not running for this camera'}), 400
        
        # Stop manager
        manager = surveillance_managers[camera_id]
        manager.stop_surveillance()
        
        # Remove from active managers
        del surveillance_managers[camera_id]
        
        # Log stop event
        camera = camera_model.find_by_id(camera_id)
        log_model.create({
            'event': 'Surveillance Stopped',
            'location': camera['location'] if camera else 'Unknown',
            'confidence': 1.0,
            'action': 'system_stop',
            'metadata': {'camera_id': camera_id}
        })
        
        return jsonify({
            'success': True,
            'message': f'Surveillance stopped for camera {camera_id}'
        })
        
    except Exception as e:
        logger.error(f"Stop surveillance error: {e}")
        return jsonify({'error': str(e)}), 500

@surveillance_bp.route('/surveillance/live_frame/<camera_id>', methods=['GET'])
def get_live_frame(camera_id: str):
    """Get latest processed frame from surveillance"""
    try:
        if camera_id not in surveillance_managers:
            return jsonify({'error': 'Surveillance not running for this camera'}), 404
        
        manager = surveillance_managers[camera_id]
        result = manager.get_latest_result()
        
        if not result or 'output_frame' not in result:
            return jsonify({'error': 'No frame available'}), 404
        
        frame = result['output_frame']
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Return as base64 or direct image
        return_format = request.args.get('format', 'image')
        
        if return_format == 'base64':
            frame_b64 = base64.b64encode(frame_bytes).decode('utf-8')
            return jsonify({
                'frame': frame_b64,
                'timestamp': result['timestamp'],
                'stats': {
                    'detections': len(result.get('detections', [])),
                    'tracks': len(result.get('tracks', {})),
                    'activities': len(result.get('activities', []))
                }
            })
        else:
            return send_file(
                io.BytesIO(frame_bytes),
                mimetype='image/jpeg',
                as_attachment=False
            )
            
    except Exception as e:
        logger.error(f"Live frame error: {e}")
        return jsonify({'error': str(e)}), 500

@surveillance_bp.route('/surveillance/detection_zones/<camera_id>', methods=['GET', 'POST'])
def manage_detection_zones(camera_id: str):
    """Manage detection zones for camera"""
    try:
        if camera_id not in surveillance_managers:
            return jsonify({'error': 'Surveillance not running for this camera'}), 404
        
        manager = surveillance_managers[camera_id]
        
        if request.method == 'GET':
            # Get current zones
            zones = []
            for zone in manager.activity_analyzer.zones:
                zones.append({
                    'name': zone.name,
                    'type': zone.zone_type,
                    'points': zone.points,
                    'activity_types': [activity.value for activity in zone.activity_types]
                })
            
            return jsonify({'zones': zones})
        
        elif request.method == 'POST':
            # Add new zone
            data = request.json
            
            # Validate required fields
            required_fields = ['name', 'type', 'points', 'activity_types']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing field: {field}'}), 400
            
            # Convert activity types
            activity_types = []
            for activity_str in data['activity_types']:
                try:
                    activity_types.append(ActivityType(activity_str))
                except ValueError:
                    return jsonify({'error': f'Invalid activity type: {activity_str}'}), 400
            
            # Create zone
            zone = DetectionZone(
                name=data['name'],
                points=data['points'],
                zone_type=data['type'],
                activity_types=activity_types
            )
            
            manager.add_detection_zone(zone)
            
            return jsonify({
                'success': True,
                'message': f'Detection zone "{data["name"]}" added'
            })
            
    except Exception as e:
        logger.error(f"Detection zones error: {e}")
        return jsonify({'error': str(e)}), 500

@surveillance_bp.route('/surveillance/activities/<camera_id>', methods=['GET'])
def get_recent_activities(camera_id: str):
    """Get recent suspicious activities for camera"""
    try:
        if camera_id not in surveillance_managers:
            return jsonify({'error': 'Surveillance not running for this camera'}), 404
        
        manager = surveillance_managers[camera_id]
        time_window = float(request.args.get('hours', 1)) * 3600  # Convert to seconds
        
        activities = manager.activity_analyzer.get_recent_activities(time_window)
        
        # Convert activities to JSON
        activity_list = []
        for activity in activities:
            activity_list.append({
                'timestamp': activity.timestamp,
                'datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(activity.timestamp)),
                'type': activity.activity_type.value,
                'threat_level': activity.threat_level.value,
                'track_id': activity.track_id,
                'description': activity.description,
                'location': activity.location,
                'zone_name': activity.zone_name,
                'confidence': activity.confidence,
                'evidence': activity.evidence
            })
        
        return jsonify({'activities': activity_list})
        
    except Exception as e:
        logger.error(f"Recent activities error: {e}")
        return jsonify({'error': str(e)}), 500

@surveillance_bp.route('/surveillance/known_faces', methods=['GET', 'POST'])
def manage_known_faces():
    """Manage known faces database"""
    try:
        if request.method == 'GET':
            # Get list of known persons
            known_persons = []
            
            # Get from any active manager
            if surveillance_managers:
                manager = next(iter(surveillance_managers.values()))
                known_persons = manager.face_recognizer.get_known_persons()
            
            return jsonify({'known_persons': known_persons})
        
        elif request.method == 'POST':
            # Add new person
            data = request.json
            
            if 'name' not in data or 'images' not in data:
                return jsonify({'error': 'Missing name or images'}), 400
            
            person_name = data['name']
            image_data_list = data['images']  # List of base64 encoded images
            
            # Decode images
            face_images = []
            for img_data in image_data_list:
                try:
                    # Remove data URL prefix if present
                    if ',' in img_data:
                        img_data = img_data.split(',')[1]
                    
                    # Decode base64
                    img_bytes = base64.b64decode(img_data)
                    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
                    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                    if image is not None:
                        face_images.append(image)
                    
                except Exception as e:
                    logger.warning(f"Failed to decode image: {e}")
                    continue
            
            if not face_images:
                return jsonify({'error': 'No valid images provided'}), 400
            
            # Add person to all active face recognizers
            success_count = 0
            for manager in surveillance_managers.values():
                if manager.face_recognizer.add_person(person_name, face_images):
                    success_count += 1
            
            if success_count > 0:
                return jsonify({
                    'success': True,
                    'message': f'Person "{person_name}" added with {len(face_images)} face samples'
                })
            else:
                return jsonify({'error': 'Failed to add person'}), 500
                
    except Exception as e:
        logger.error(f"Known faces error: {e}")
        return jsonify({'error': str(e)}), 500

@surveillance_bp.route('/surveillance/test_alert', methods=['POST'])
def send_test_alert():
    """Send test alert email"""
    try:
        init_alert_manager()
        
        if alert_manager and alert_manager.send_test_alert():
            return jsonify({
                'success': True,
                'message': 'Test alert sent successfully'
            })
        else:
            return jsonify({'error': 'Failed to send test alert'}), 500
            
    except Exception as e:
        logger.error(f"Test alert error: {e}")
        return jsonify({'error': str(e)}), 500

def get_default_detection_zones(camera: Dict) -> List[DetectionZone]:
    """
    Get default detection zones for a camera
    
    Args:
        camera: Camera dictionary
        
    Returns:
        List of default detection zones
    """
    # Create a default monitored zone covering most of the frame
    # These would typically be configured based on camera placement
    
    default_zone = DetectionZone(
        name=f"{camera['name']} Main Area",
        points=[(50, 50), (1230, 50), (1230, 670), (50, 670)],  # Assuming 1280x720 resolution
        zone_type="monitored",
        activity_types=[
            ActivityType.LOITERING,
            ActivityType.UNAUTHORIZED_PERSON,
            ActivityType.WEAPON_DETECTED,
            ActivityType.ABANDONED_OBJECT
        ]
    )
    
    return [default_zone]

# Cleanup function for when the app shuts down
def cleanup_surveillance():
    """Clean up surveillance managers"""
    global surveillance_managers, alert_manager
    
    # Stop all surveillance managers
    for camera_id, manager in surveillance_managers.items():
        try:
            manager.stop_surveillance()
            logger.info(f"Stopped surveillance for camera {camera_id}")
        except Exception as e:
            logger.error(f"Error stopping surveillance for {camera_id}: {e}")
    
    surveillance_managers.clear()
    
    # Stop alert manager
    if alert_manager:
        alert_manager.stop()
        alert_manager = None
    
    logger.info("Surveillance cleanup completed")