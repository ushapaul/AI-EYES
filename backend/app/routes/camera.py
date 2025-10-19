from flask import Blueprint, jsonify, request, Response
import cv2
import json

# Create camera service instance with error handling
try:
    from app.services.camera_service import CameraService
    camera_service = CameraService()
except ImportError:
    print("Warning: CameraService not available")
    camera_service = None

# Import camera discovery service
try:
    from app.services.camera_discovery import camera_discovery
except ImportError:
    print("Warning: CameraDiscovery not available")
    camera_discovery = None

camera_bp = Blueprint('camera', __name__)

@camera_bp.route('/list', methods=['GET'])
def get_cameras():
    """Get list of all discovered cameras with real-time status"""
    try:
        # First, try to get cameras from discovery service
        if camera_discovery:
            cameras = camera_discovery.get_cameras()
            
            # Format cameras for frontend
            formatted_cameras = []
            for cam in cameras:
                formatted_cameras.append({
                    'id': cam['id'],
                    'name': cam['name'],
                    'ip': cam['ip'],
                    'port': cam['port'],
                    'url': cam['url'],
                    'type': cam['type'],
                    'status': cam['status'],
                    'last_seen': cam.get('last_seen', ''),
                    'discovered_at': cam.get('discovered_at', ''),
                    'manual': cam.get('manual', False)
                })
            
            print(f"📹 Returning {len(formatted_cameras)} discovered cameras")
            return jsonify(formatted_cameras)
        
        # Fallback: Try to get cameras from surveillance system (port 5002)
        import requests
        response = requests.get('http://localhost:5002/api/cameras', timeout=2)
        if response.status_code == 200:
            return jsonify(response.json())
            
    except Exception as e:
        print(f"Could not fetch cameras: {e}")
    
    # Final fallback: Return empty list
    return jsonify([])

@camera_bp.route('/stream/<int:camera_id>')
def video_stream(camera_id):
    """Stream video from specific camera"""
    def generate():
        # This would connect to actual camera stream
        # For now, we'll simulate with placeholder
        while True:
            # Get frame from camera service
            frame = camera_service.get_frame(camera_id)
            if frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@camera_bp.route('/<int:camera_id>/snapshot', methods=['POST'])
def take_snapshot(camera_id):
    """Take a snapshot from specific camera"""
    success = camera_service.take_snapshot(camera_id)
    if success:
        return jsonify({'message': 'Snapshot saved successfully', 'camera_id': camera_id})
    else:
        return jsonify({'error': 'Failed to take snapshot'}), 500

@camera_bp.route('/<int:camera_id>/record', methods=['POST'])
def toggle_recording(camera_id):
    """Start/stop recording for specific camera"""
    action = request.json.get('action', 'start')
    success = camera_service.toggle_recording(camera_id, action == 'start')
    
    if success:
        return jsonify({
            'message': f'Recording {"started" if action == "start" else "stopped"}',
            'camera_id': camera_id,
            'recording': action == 'start'
        })
    else:
        return jsonify({'error': 'Failed to toggle recording'}), 500

@camera_bp.route('/add', methods=['POST'])
def add_camera():
    """Manually add a camera to the system"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'url' not in data:
        return jsonify({'error': 'Missing required fields (name, url)'}), 400
    
    if camera_discovery:
        camera = camera_discovery.add_manual_camera(
            name=data['name'],
            url=data['url'],
            camera_type=data.get('type', 'manual')
        )
        
        if camera:
            return jsonify({
                'message': 'Camera added successfully',
                'camera': camera
            })
    
    return jsonify({'error': 'Failed to add camera'}), 500

@camera_bp.route('/remove/<camera_id>', methods=['DELETE'])
def remove_camera(camera_id):
    """Remove a camera from the system"""
    if camera_discovery:
        camera_discovery.remove_camera(camera_id)
        return jsonify({'message': 'Camera removed successfully'})
    
    return jsonify({'error': 'Camera discovery not available'}), 500

@camera_bp.route('/scan', methods=['POST'])
def scan_network():
    """Trigger network scan for cameras"""
    if camera_discovery:
        # Start scan in background
        import threading
        thread = threading.Thread(target=camera_discovery.scan_network)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Network scan started',
            'status': 'scanning'
        })
    
    return jsonify({'error': 'Camera discovery not available'}), 500

@camera_bp.route('/status', methods=['GET'])
def get_camera_status():
    """Get camera discovery service status"""
    if camera_discovery:
        cameras = camera_discovery.get_cameras()
        online_count = len([c for c in cameras if c['status'] == 'online'])
        offline_count = len([c for c in cameras if c['status'] == 'offline'])
        
        return jsonify({
            'total_cameras': len(cameras),
            'online': online_count,
            'offline': offline_count,
            'scanning': camera_discovery.scanning
        })
    
    return jsonify({
        'total_cameras': 0,
        'online': 0,
        'offline': 0,
        'scanning': False
    })
