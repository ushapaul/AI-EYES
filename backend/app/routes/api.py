from flask import Blueprint, jsonify, request
from datetime import datetime
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'ai_models_loaded': True
    })

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    return jsonify({
        'total_cameras': 6,
        'active_cameras': 5,
        'total_alerts_today': 15,
        'detection_accuracy': 94.5,
        'uptime': '99.8%'
    })

@api_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get event logs"""
    # This would typically fetch from a database
    logs = [
        {
            'id': 1,
            'timestamp': datetime.now().isoformat(),
            'event': 'Unauthorized Person Detected',
            'location': 'Farm Gate A',
            'confidence': 95,
            'action': 'Alert Sent',
            'image_path': '/data/alerts/alert_1.jpg'
        },
        {
            'id': 2,
            'timestamp': datetime.now().isoformat(),
            'event': 'Suspicious Activity',
            'location': 'Bank ATM Area',
            'confidence': 87,
            'action': 'Monitoring',
            'image_path': '/data/alerts/alert_2.jpg'
        }
    ]
    return jsonify(logs)

@api_bp.route('/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update system settings"""
    from database.models import settings_model
    
    if request.method == 'GET':
        # Get settings from database
        category = request.args.get('category')
        settings_data = settings_model.get_settings(category)
        return jsonify(settings_data)
    
    elif request.method == 'POST':
        # Save settings to database
        data = request.get_json()
        category = data.get('category')
        settings = data.get('settings')
        
        if not category or not settings:
            return jsonify({'error': 'Missing category or settings'}), 400
        
        success = settings_model.update_settings(category, settings)
        
        if success:
            return jsonify({'message': f'{category.capitalize()} settings updated successfully'})
        else:
            return jsonify({'error': 'Failed to update settings'}), 500

@api_bp.route('/settings/<category>', methods=['PUT', 'POST'])
def update_settings_by_category(category):
    """Update specific category settings (used by frontend)"""
    from database.models import settings_model
    
    try:
        settings_data = request.get_json()
        
        # Frontend sends the settings directly, not wrapped in 'settings' key
        success = settings_model.update_settings(category, settings_data)
        
        if success:
            print(f"✅ {category.capitalize()} settings updated successfully")
            return jsonify({'success': True, 'message': f'{category.capitalize()} settings updated'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update settings'}), 500
    except Exception as e:
        print(f"❌ Error updating {category} settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500