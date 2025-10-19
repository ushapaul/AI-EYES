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
    if request.method == 'GET':
        return jsonify({
            'mode': 'farm',
            'email_alerts': True,
            'detection_sensitivity': 0.7,
            'recording_enabled': True,
            'notification_emails': ['admin@yourdomain.com']
        })
    
    elif request.method == 'POST':
        settings = request.get_json()
        # Here you would save settings to database or config file
        return jsonify({'message': 'Settings updated successfully'})