import cv2
import threading
import time
from datetime import datetime
import numpy as np
from config.settings import *

class CameraService:
    def __init__(self):
        self.cameras = {}
        self.recording_status = {}
        self.detection_active = {}
        
    def get_frame(self, camera_id):
        """Get frame from specific camera"""
        if camera_id not in self.cameras:
            # Initialize camera connection
            self.connect_camera(camera_id)
        
        if camera_id in self.cameras:
            ret, frame = self.cameras[camera_id].read()
            if ret:
                return frame
        return None
    
    def connect_camera(self, camera_id):
        """Connect to camera by ID"""
        try:
            # For demonstration, using default camera (0) or IP webcam URL
            if camera_id == 1:
                cap = cv2.VideoCapture(0)  # Default camera
            else:
                # For IP webcam, you would use the actual IP
                cap = cv2.VideoCapture(f"http://192.168.1.{100 + camera_id}:8080/video")
            
            if cap.isOpened():
                self.cameras[camera_id] = cap
                return True
        except Exception as e:
            print(f"Error connecting to camera {camera_id}: {e}")
        return False
    
    def disconnect_camera(self, camera_id):
        """Disconnect camera"""
        if camera_id in self.cameras:
            self.cameras[camera_id].release()
            del self.cameras[camera_id]
    
    def take_snapshot(self, camera_id):
        """Take snapshot from camera"""
        frame = self.get_frame(camera_id)
        if frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{ALERTS_PATH}/snapshot_{camera_id}_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            return True
        return False
    
    def toggle_recording(self, camera_id, start_recording):
        """Start or stop recording"""
        if start_recording:
            self.recording_status[camera_id] = True
            # Start recording thread
            thread = threading.Thread(target=self._record_video, args=(camera_id,))
            thread.daemon = True
            thread.start()
        else:
            self.recording_status[camera_id] = False
        
        return True
    
    def _record_video(self, camera_id):
        """Record video from camera"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ALERTS_PATH}/recording_{camera_id}_{timestamp}.mp4"
        
        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, FPS, CAMERA_RESOLUTION)
        
        while self.recording_status.get(camera_id, False):
            frame = self.get_frame(camera_id)
            if frame is not None:
                # Resize frame to standard resolution
                frame_resized = cv2.resize(frame, CAMERA_RESOLUTION)
                out.write(frame_resized)
            time.sleep(1/FPS)
        
        out.release()
    
    def start_ai_detection(self, camera_id, mode='farm'):
        """Start AI detection for camera"""
        self.detection_active[camera_id] = True
        thread = threading.Thread(target=self._ai_detection_loop, args=(camera_id, mode))
        thread.daemon = True
        thread.start()
    
    def _ai_detection_loop(self, camera_id, mode):
        """AI detection loop"""
        from app.ai_models.face_recognition_model import FaceRecognitionModel
        from app.ai_models.suspicious_activity_model import SuspiciousActivityModel
        
        if mode == 'farm':
            detector = FaceRecognitionModel()
        else:
            detector = SuspiciousActivityModel()
        
        while self.detection_active.get(camera_id, False):
            frame = self.get_frame(camera_id)
            if frame is not None:
                # Run AI detection
                detection_result = detector.detect(frame)
                
                if detection_result['threat_detected']:
                    # Handle threat detection
                    self._handle_threat_detection(camera_id, detection_result, frame)
            
            time.sleep(0.1)  # 10 FPS for detection
    
    def _handle_threat_detection(self, camera_id, detection_result, frame):
        """Handle detected threat"""
        # Save alert image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        alert_image = f"{ALERTS_PATH}/alert_{camera_id}_{timestamp}.jpg"
        cv2.imwrite(alert_image, frame)
        
        # Create alert data
        alert_data = {
            'camera_id': camera_id,
            'type': detection_result['type'],
            'confidence': detection_result['confidence'],
            'timestamp': datetime.now().isoformat(),
            'image_path': alert_image,
            'description': detection_result['description']
        }
        
        # Send alert (this would trigger email and WebSocket notification)
        self._send_alert(alert_data)
    
    def _send_alert(self, alert_data):
        """Send alert notification"""
        # This would trigger email service and WebSocket notification
        print(f"ALERT: {alert_data['type']} detected at camera {alert_data['camera_id']}")
        
    def stop_ai_detection(self, camera_id):
        """Stop AI detection for camera"""
        self.detection_active[camera_id] = False
    
    def cleanup(self):
        """Cleanup all camera connections"""
        for camera_id in list(self.cameras.keys()):
            self.disconnect_camera(camera_id)