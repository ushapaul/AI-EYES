import cv2
import requests
import numpy as np
from urllib.parse import urlparse
import socket

def test_camera_connection(camera_url):
    """Test if camera URL is accessible"""
    try:
        if camera_url.startswith('http'):
            # Test HTTP camera (IP Webcam)
            response = requests.get(camera_url, timeout=5)
            return response.status_code == 200
        else:
            # Test local camera
            cap = cv2.VideoCapture(int(camera_url) if camera_url.isdigit() else camera_url)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                return ret
            return False
    except Exception as e:
        print(f"Camera connection test failed: {e}")
        return False

def get_ip_webcam_stream_url(ip, port=8080):
    """Generate IP Webcam stream URL"""
    return f"http://{ip}:{port}/video"

def detect_available_cameras():
    """Detect available local cameras"""
    available_cameras = []
    
    # Check first 5 camera indices
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append({
                    'id': i,
                    'name': f'Camera {i}',
                    'type': 'local',
                    'url': str(i)
                })
            cap.release()
    
    return available_cameras

def scan_network_cameras(network_range="192.168.1"):
    """Scan network for IP webcam devices"""
    ip_cameras = []
    
    # Common IP webcam ports
    common_ports = [8080, 8081, 554, 80]
    
    for i in range(1, 255):
        ip = f"{network_range}.{i}"
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    # Port is open, test if it's a camera
                    camera_url = f"http://{ip}:{port}/video"
                    if test_camera_connection(camera_url):
                        ip_cameras.append({
                            'ip': ip,
                            'port': port,
                            'url': camera_url,
                            'name': f'IP Camera {ip}:{port}'
                        })
                        break  # Found camera on this IP, no need to check other ports
                        
            except Exception:
                continue
    
    return ip_cameras

def resize_frame(frame, max_width=640, max_height=480):
    """Resize frame while maintaining aspect ratio"""
    height, width = frame.shape[:2]
    
    # Calculate scaling factor
    scale_w = max_width / width
    scale_h = max_height / height
    scale = min(scale_w, scale_h)
    
    if scale < 1:
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(frame, (new_width, new_height))
    
    return frame

def add_timestamp_overlay(frame, timestamp=None):
    """Add timestamp overlay to frame"""
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add semi-transparent background for text
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (300, 40), (0, 0, 0), -1)
    frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
    
    # Add timestamp text
    cv2.putText(frame, timestamp, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return frame

def add_detection_overlay(frame, detections, detection_type='face'):
    """Add detection overlays to frame"""
    overlay_frame = frame.copy()
    
    if detection_type == 'face':
        # Face detection overlays
        for detection in detections.get('known_faces', []):
            bbox = detection['bbox']
            name = detection['name']
            confidence = detection['confidence']
            
            # Green box for known faces
            cv2.rectangle(overlay_frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)
            cv2.putText(overlay_frame, f"{name} ({confidence:.1f}%)", 
                       (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        if detections.get('unknown_faces', 0) > 0:
            # Add warning overlay for unknown faces
            cv2.putText(overlay_frame, f"⚠️ UNKNOWN PERSON DETECTED", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    elif detection_type == 'activity':
        # Activity detection overlays
        for detection in detections.get('detections', []):
            bbox = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            
            # Color based on object type
            if class_name == 'person':
                color = (0, 255, 0)  # Green
            elif class_name in ['knife', 'gun', 'pistol', 'rifle']:
                color = (0, 0, 255)  # Red for weapons
            else:
                color = (255, 255, 0)  # Yellow
            
            cv2.rectangle(overlay_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            cv2.putText(overlay_frame, f"{class_name}: {confidence:.2f}", 
                       (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        if detections.get('weapon_detected', False):
            cv2.putText(overlay_frame, "🚨 WEAPON DETECTED", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    return overlay_frame

def save_detection_image(frame, alert_data, output_dir):
    """Save detection image with annotations"""
    import os
    from datetime import datetime
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"alert_{alert_data.get('camera_id', 'unknown')}_{timestamp}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    # Add alert information overlay
    overlay_frame = frame.copy()
    
    # Add alert header
    cv2.rectangle(overlay_frame, (10, 10), (frame.shape[1] - 10, 100), (0, 0, 0), -1)
    cv2.rectangle(overlay_frame, (10, 10), (frame.shape[1] - 10, 100), (0, 0, 255), 2)
    
    cv2.putText(overlay_frame, "SECURITY ALERT", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(overlay_frame, f"Type: {alert_data.get('type', 'Unknown')}", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(overlay_frame, f"Confidence: {alert_data.get('confidence', 0):.1f}%", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(overlay_frame, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Save image
    cv2.imwrite(filepath, overlay_frame)
    
    return filepath

def validate_email(email):
    """Validate email address format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_camera_config():
    """Generate camera configuration template"""
    return {
        "cameras": [
            {
                "id": 1,
                "name": "Farm Gate A",
                "location": "Main Entrance",
                "url": "http://192.168.1.100:8080/video",
                "type": "farm",
                "ai_model": "face_recognition",
                "recording_enabled": True,
                "alert_enabled": True
            },
            {
                "id": 2,
                "name": "Bank Main Hall",
                "location": "Customer Area",
                "url": "http://192.168.1.101:8080/video", 
                "type": "bank",
                "ai_model": "suspicious_activity",
                "recording_enabled": True,
                "alert_enabled": True
            }
        ],
        "settings": {
            "detection_confidence": 0.7,
            "face_recognition_threshold": 0.6,
            "suspicious_activity_threshold": 0.7,
            "email_alerts": True,
            "recording_duration": 30,
            "max_storage_days": 30
        }
    }