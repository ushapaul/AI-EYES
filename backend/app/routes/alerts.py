from flask import Blueprint, jsonify, request
from datetime import datetime
import json

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/list', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    alerts = [
        {
            'id': 1,
            'type': 'intruder',
            'location': 'Farm Gate A',
            'timestamp': datetime.now().isoformat(),
            'severity': 'high',
            'confidence': 95,
            'image_path': '/data/alerts/intruder_1.jpg',
            'description': 'Unknown person detected at farm entrance',
            'status': 'active'
        },
        {
            'id': 2,
            'type': 'suspicious_activity',
            'location': 'Bank Main Hall',
            'timestamp': datetime.now().isoformat(),
            'severity': 'medium',
            'confidence': 87,
            'image_path': '/data/alerts/suspicious_2.jpg',
            'description': 'Suspicious behavior detected in banking area',
            'status': 'investigating'
        }
    ]
    return jsonify(alerts)

@alerts_bp.route('/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    # Here you would update the alert status in database
    return jsonify({
        'message': 'Alert acknowledged',
        'alert_id': alert_id,
        'acknowledged_at': datetime.now().isoformat()
    })

@alerts_bp.route('/<int:alert_id>/dismiss', methods=['POST'])
def dismiss_alert(alert_id):
    """Dismiss an alert"""
    # Here you would update the alert status in database
    return jsonify({
        'message': 'Alert dismissed',
        'alert_id': alert_id,
        'dismissed_at': datetime.now().isoformat()
    })

@alerts_bp.route('/summary', methods=['GET'])
def get_alert_summary():
    """Get alerts summary for dashboard"""
    return jsonify({
        'total_today': 15,
        'high_priority': 3,
        'medium_priority': 8,
        'low_priority': 4,
        'acknowledged': 10,
        'active': 5
    })

@alerts_bp.route('/recent', methods=['GET'])
def get_recent_alerts():
    """Get recent alerts for notifications"""
    limit = request.args.get('limit', 10, type=int)
    
    recent_alerts = [
        {
            'id': 1,
            'type': 'intruder',
            'location': 'Farm Gate A',
            'timestamp': datetime.now().isoformat(),
            'severity': 'high'
        },
        {
            'id': 2,
            'type': 'suspicious_activity',
            'location': 'Bank ATM Area',
            'timestamp': datetime.now().isoformat(),
            'severity': 'medium'
        }
    ]
    
    return jsonify(recent_alerts[:limit])