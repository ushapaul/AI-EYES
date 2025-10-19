"""
Enhanced Camera Management Routes with Authentication
Provides secure CRUD operations for camera management
"""
from flask import Blueprint, request, jsonify
from database.models import camera_model, log_model
from app.utils.auth import require_auth, require_admin_password, generate_jwt_token, verify_admin_password
from storage.manager import storage_manager
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

camera_bp = Blueprint('camera_protected', __name__)

# Authentication endpoints
@camera_bp.route('/auth/login', methods=['POST'])
def login():
    """Login endpoint to get JWT token"""
    try:
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({
                'error': 'Password required',
                'message': 'Admin password must be provided'
            }), 400
        
        password = data['password']
        if verify_admin_password(password):
            token = generate_jwt_token('admin')
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'expires_hours': 24
            })
        else:
            return jsonify({
                'error': 'Invalid credentials',
                'message': 'Incorrect admin password'
            }), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Protected Camera CRUD Operations

@camera_bp.route('/cameras', methods=['GET'])
def get_all_cameras():
    """Get all cameras (public endpoint)"""
    try:
        cameras = camera_model.find_all()
        return jsonify({
            'success': True,
            'cameras': cameras,
            'count': len(cameras)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@camera_bp.route('/cameras/<camera_id>', methods=['GET'])
def get_camera(camera_id):
    """Get specific camera by ID (public endpoint)"""
    try:
        camera = camera_model.find_by_id(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        return jsonify({
            'success': True,
            'camera': camera
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@camera_bp.route('/cameras', methods=['POST'])
@require_admin_password
def create_camera():
    """Create new camera (requires admin password)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'location', 'url', 'type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'required_fields': required_fields
                }), 400
        
        # Create camera using MongoDB model
        camera_id = camera_model.create_camera(
            name=data['name'],
            location=data['location'],
            url=data['url'],
            camera_type=data['type'],
            username=data.get('username', ''),
            password=data.get('password', ''),
            enabled=data.get('enabled', True)
        )
        
        # Create log entry
        log_model.create_log(
            camera_id=camera_id,
            action='camera_created',
            description=f"Camera '{data['name']}' created at {data['location']}",
            log_level='info'
        )
        
        # Get the created camera
        new_camera = camera_model.find_by_id(camera_id)
        
        return jsonify({
            'success': True,
            'message': 'Camera created successfully',
            'camera': new_camera,
            'camera_id': camera_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@camera_bp.route('/cameras/<camera_id>', methods=['PUT'])
@require_admin_password
def update_camera(camera_id):
    """Update camera (requires admin password)"""
    try:
        # Check if camera exists
        existing_camera = camera_model.find_by_id(camera_id)
        if not existing_camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        data = request.get_json()
        
        # Update camera
        update_data = {}
        updatable_fields = ['name', 'location', 'url', 'type', 'username', 'password', 'enabled']
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({
                'error': 'No valid fields to update',
                'updatable_fields': updatable_fields
            }), 400
        
        success = camera_model.update_camera(camera_id, update_data)
        
        if success:
            # Create log entry
            log_model.create_log(
                camera_id=camera_id,
                action='camera_updated',
                description=f"Camera '{existing_camera['name']}' updated",
                log_level='info'
            )
            
            # Get updated camera
            updated_camera = camera_model.find_by_id(camera_id)
            
            return jsonify({
                'success': True,
                'message': 'Camera updated successfully',
                'camera': updated_camera
            })
        else:
            return jsonify({'error': 'Failed to update camera'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@camera_bp.route('/cameras/<camera_id>', methods=['DELETE'])
@require_admin_password
def delete_camera(camera_id):
    """Delete camera (requires admin password)"""
    try:
        # Check if camera exists
        camera = camera_model.find_by_id(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        # Delete camera
        success = camera_model.delete_by_id(camera_id)
        
        if success:
            # Create log entry
            log_model.create_log(
                camera_id=camera_id,
                action='camera_deleted',
                description=f"Camera '{camera['name']}' deleted",
                log_level='warning'
            )
            
            return jsonify({
                'success': True,
                'message': f"Camera '{camera['name']}' deleted successfully"
            })
        else:
            return jsonify({'error': 'Failed to delete camera'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Camera Operations (require authentication)

@camera_bp.route('/cameras/<camera_id>/snapshot', methods=['POST'])
@require_auth
def capture_snapshot(camera_id):
    """Capture snapshot from camera (requires authentication)"""
    try:
        # Get camera details
        camera = camera_model.find_by_id(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        if not camera.get('enabled', True):
            return jsonify({'error': 'Camera is disabled'}), 400
        
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
            
            return jsonify({
                'success': True,
                'message': 'Snapshot captured successfully',
                'image_path': image_path,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'error': 'Failed to capture snapshot',
                'message': 'Check camera URL and credentials'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@camera_bp.route('/cameras/<camera_id>/enable', methods=['POST'])
@require_admin_password
def enable_camera(camera_id):
    """Enable camera (requires admin password)"""
    try:
        camera = camera_model.find_by_id(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        success = camera_model.update_camera(camera_id, {'enabled': True})
        
        if success:
            log_model.create_log(
                camera_id=camera_id,
                action='camera_enabled',
                description=f"Camera '{camera['name']}' enabled"
            )
            
            return jsonify({
                'success': True,
                'message': f"Camera '{camera['name']}' enabled"
            })
        else:
            return jsonify({'error': 'Failed to enable camera'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@camera_bp.route('/cameras/<camera_id>/disable', methods=['POST'])
@require_admin_password
def disable_camera(camera_id):
    """Disable camera (requires admin password)"""
    try:
        camera = camera_model.find_by_id(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        success = camera_model.update_camera(camera_id, {'enabled': False})
        
        if success:
            log_model.create_log(
                camera_id=camera_id,
                action='camera_disabled',
                description=f"Camera '{camera['name']}' disabled"
            )
            
            return jsonify({
                'success': True,
                'message': f"Camera '{camera['name']}' disabled"
            })
        else:
            return jsonify({'error': 'Failed to disable camera'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@camera_bp.route('/cameras/bulk-action', methods=['POST'])
@require_admin_password
def bulk_camera_action():
    """Perform bulk actions on multiple cameras (requires admin password)"""
    try:
        data = request.get_json()
        camera_ids = data.get('camera_ids', [])
        action = data.get('action')
        
        if not camera_ids or not action:
            return jsonify({
                'error': 'Missing required fields',
                'required': ['camera_ids', 'action'],
                'available_actions': ['enable', 'disable', 'delete']
            }), 400
        
        results = []
        
        for camera_id in camera_ids:
            try:
                camera = camera_model.find_by_id(camera_id)
                if not camera:
                    results.append({
                        'camera_id': camera_id,
                        'success': False,
                        'error': 'Camera not found'
                    })
                    continue
                
                if action == 'enable':
                    success = camera_model.update_camera(camera_id, {'enabled': True})
                    message = 'enabled'
                elif action == 'disable':
                    success = camera_model.update_camera(camera_id, {'enabled': False})
                    message = 'disabled'
                elif action == 'delete':
                    success = camera_model.delete_by_id(camera_id)
                    message = 'deleted'
                else:
                    results.append({
                        'camera_id': camera_id,
                        'success': False,
                        'error': 'Invalid action'
                    })
                    continue
                
                if success:
                    log_model.create_log(
                        camera_id=camera_id,
                        action=f'camera_{action}',
                        description=f"Camera '{camera['name']}' {message} via bulk action"
                    )
                    
                    results.append({
                        'camera_id': camera_id,
                        'success': True,
                        'message': f"Camera {message}"
                    })
                else:
                    results.append({
                        'camera_id': camera_id,
                        'success': False,
                        'error': f'Failed to {action} camera'
                    })
                    
            except Exception as e:
                results.append({
                    'camera_id': camera_id,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'message': f'Bulk {action} operation completed',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500