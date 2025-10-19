"""
Surveillance Manager Module
Coordinates all surveillance components for real-time monitoring
"""

import cv2
import numpy as np
import time
import threading
import queue
from typing import Dict, List, Optional, Callable
import logging
from pathlib import Path

from .detector import YOLOv9Detector
from .tracker import PersonTracker
from .face_recognition import LBPHFaceRecognizer
from .activity_analyzer import SuspiciousActivityAnalyzer, SuspiciousActivity, DetectionZone, ActivityType

logger = logging.getLogger(__name__)

class SurveillanceManager:
    """
    Main surveillance manager that coordinates detection, tracking, 
    face recognition, and activity analysis
    """
    
    def __init__(self,
                 camera_url: Optional[str] = None,
                 camera_id: int = 0,
                 output_dir: str = "surveillance_output",
                 model_path: Optional[str] = None,
                 known_faces_dir: str = "data/known_faces"):
        """
        Initialize surveillance manager
        
        Args:
            camera_url: IP camera URL or None for webcam
            camera_id: Camera ID for webcam
            output_dir: Directory for saving outputs
            model_path: Path to YOLO model
            known_faces_dir: Directory with known face images
        """
        self.camera_url = camera_url
        self.camera_id = camera_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.detector = YOLOv9Detector(model_path=model_path)
        self.tracker = PersonTracker()
        self.face_recognizer = LBPHFaceRecognizer(known_faces_dir=known_faces_dir)
        self.activity_analyzer = SuspiciousActivityAnalyzer()
        
        # Camera and streaming
        self.cap = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.result_queue = queue.Queue(maxsize=100)
        
        # Processing statistics
        self.stats = {
            'frames_processed': 0,
            'persons_detected': 0,
            'faces_recognized': 0,
            'activities_detected': 0,
            'processing_fps': 0.0,
            'start_time': 0.0
        }
        
        # Callbacks for events
        self.activity_callback: Optional[Callable[[SuspiciousActivity], None]] = None
        self.frame_callback: Optional[Callable[[np.ndarray], None]] = None
        
        # Processing threads
        self.capture_thread = None
        self.process_thread = None
        
    def set_activity_callback(self, callback: Callable[[SuspiciousActivity], None]):
        """
        Set callback function for suspicious activities
        
        Args:
            callback: Function to call when activity is detected
        """
        self.activity_callback = callback
    
    def set_frame_callback(self, callback: Callable[[np.ndarray], None]):
        """
        Set callback function for processed frames
        
        Args:
            callback: Function to call with processed frames
        """
        self.frame_callback = callback
    
    def add_detection_zone(self, zone: DetectionZone):
        """
        Add detection zone for activity analysis
        
        Args:
            zone: DetectionZone object
        """
        self.activity_analyzer.add_detection_zone(zone)
    
    def start_surveillance(self) -> bool:
        """
        Start surveillance system
        
        Returns:
            True if started successfully
        """
        try:
            # Initialize camera
            if self.camera_url:
                self.cap = cv2.VideoCapture(self.camera_url)
            else:
                self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error("Failed to open camera")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_running = True
            self.stats['start_time'] = time.time()
            
            # Start processing threads
            self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
            self.process_thread = threading.Thread(target=self._process_frames, daemon=True)
            
            self.capture_thread.start()
            self.process_thread.start()
            
            logger.info("Surveillance system started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start surveillance: {e}")
            return False
    
    def stop_surveillance(self):
        """Stop surveillance system"""
        self.is_running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        if self.process_thread:
            self.process_thread.join(timeout=2)
        
        if self.cap:
            self.cap.release()
        
        logger.info("Surveillance system stopped")
    
    def _capture_frames(self):
        """Capture frames from camera in separate thread"""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                
                # Add timestamp
                timestamp = time.time()
                
                # Put frame in queue (non-blocking)
                try:
                    self.frame_queue.put((frame, timestamp), block=False)
                except queue.Full:
                    # Skip frame if queue is full
                    pass
                    
            except Exception as e:
                logger.error(f"Frame capture error: {e}")
                time.sleep(0.1)
    
    def _process_frames(self):
        """Process frames for detection, tracking, and analysis"""
        last_fps_time = time.time()
        frame_count = 0
        
        while self.is_running:
            try:
                # Get frame from queue
                try:
                    frame, timestamp = self.frame_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                start_time = time.time()
                
                # Process frame
                result = self._process_single_frame(frame, timestamp)
                
                # Update statistics
                self.stats['frames_processed'] += 1
                frame_count += 1
                
                # Calculate FPS
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    self.stats['processing_fps'] = frame_count / (current_time - last_fps_time)
                    frame_count = 0
                    last_fps_time = current_time
                
                # Put result in queue
                try:
                    self.result_queue.put(result, block=False)
                except queue.Full:
                    # Remove oldest result to make space
                    try:
                        self.result_queue.get(block=False)
                        self.result_queue.put(result, block=False)
                    except queue.Empty:
                        pass
                
                # Call frame callback if set
                if self.frame_callback and 'output_frame' in result:
                    self.frame_callback(result['output_frame'])
                
                # Process time logging
                process_time = time.time() - start_time
                if process_time > 0.1:  # Log if processing takes too long
                    logger.debug(f"Frame processing took {process_time:.3f}s")
                    
            except Exception as e:
                logger.error(f"Frame processing error: {e}")
                time.sleep(0.01)
    
    def _process_single_frame(self, frame: np.ndarray, timestamp: float) -> Dict:
        """
        Process a single frame through the complete pipeline
        
        Args:
            frame: Input frame
            timestamp: Frame timestamp
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'timestamp': timestamp,
            'frame_shape': frame.shape,
            'detections': [],
            'tracks': {},
            'face_results': [],
            'activities': [],
            'output_frame': frame.copy()
        }
        
        try:
            # 1. Object Detection
            detections = self.detector.detect(frame)
            result['detections'] = detections
            
            # Filter person detections for tracking
            person_detections = self.detector.filter_persons(detections)
            self.stats['persons_detected'] += len(person_detections)
            
            # 2. Person Tracking
            tracks = self.tracker.update(frame, person_detections)
            result['tracks'] = tracks
            
            # 3. Face Recognition for each track
            for track_id, track_state in tracks.items():
                # Extract face region from track bounding box
                bbox = track_state['bbox']
                x1, y1, x2, y2 = bbox
                
                # Expand bbox slightly for better face detection
                padding = 20
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(frame.shape[1], x2 + padding)
                y2 = min(frame.shape[0], y2 + padding)
                
                person_crop = frame[y1:y2, x1:x2]
                
                if person_crop.size > 0:
                    # Detect faces in person crop
                    face_results = self.face_recognizer.process_frame_faces(person_crop)
                    
                    if face_results:
                        # Take the best face result
                        best_face = max(face_results, key=lambda x: x['confidence'] if x['person_name'] != 'unknown' else 0)
                        
                        # Update track with face recognition results
                        tracks[track_id]['identity'] = best_face['person_name']
                        tracks[track_id]['authorization_status'] = best_face['authorization_status']
                        tracks[track_id]['face_confidence'] = best_face['confidence']
                        
                        # Adjust face bbox to global coordinates
                        face_bbox = best_face['bbox']
                        global_face_bbox = [
                            face_bbox[0] + x1,
                            face_bbox[1] + y1,
                            face_bbox[2] + x1,
                            face_bbox[3] + y1
                        ]
                        best_face['bbox'] = global_face_bbox
                        best_face['track_id'] = track_id
                        
                        result['face_results'].append(best_face)
                        self.stats['faces_recognized'] += 1
            
            # 4. Activity Analysis
            activities = self.activity_analyzer.analyze_frame(detections, tracks, timestamp)
            result['activities'] = activities
            self.stats['activities_detected'] += len(activities)
            
            # Call activity callbacks
            if self.activity_callback:
                for activity in activities:
                    try:
                        self.activity_callback(activity)
                    except Exception as e:
                        logger.error(f"Activity callback error: {e}")
            
            # 5. Create output frame with all visualizations
            output_frame = self._create_output_frame(frame, detections, tracks, result['face_results'], activities)
            result['output_frame'] = output_frame
            
        except Exception as e:
            logger.error(f"Frame processing pipeline error: {e}")
        
        return result
    
    def _create_output_frame(self, 
                           frame: np.ndarray, 
                           detections: List[Dict], 
                           tracks: Dict, 
                           face_results: List[Dict], 
                           activities: List[SuspiciousActivity]) -> np.ndarray:
        """
        Create output frame with all visualizations
        
        Args:
            frame: Original frame
            detections: Object detections
            tracks: Person tracks
            face_results: Face recognition results
            activities: Suspicious activities
            
        Returns:
            Annotated output frame
        """
        output_frame = frame.copy()
        
        try:
            # Draw detection zones
            output_frame = self.activity_analyzer.draw_zones(output_frame)
            
            # Draw object detections (non-person objects)
            non_person_detections = [det for det in detections if det['class_id'] != 0]
            output_frame = self.detector.draw_detections(output_frame, non_person_detections)
            
            # Draw person tracks
            output_frame = self.tracker.draw_tracks(output_frame, tracks)
            
            # Draw face recognition results
            output_frame = self.face_recognizer.draw_face_results(output_frame, face_results)
            
            # Draw activity alerts
            for activity in activities:
                self._draw_activity_alert(output_frame, activity)
            
            # Draw statistics overlay
            self._draw_stats_overlay(output_frame)
            
        except Exception as e:
            logger.error(f"Visualization error: {e}")
        
        return output_frame
    
    def _draw_activity_alert(self, frame: np.ndarray, activity: SuspiciousActivity):
        """
        Draw activity alert on frame
        
        Args:
            frame: Frame to draw on
            activity: Suspicious activity
        """
        x, y = activity.location
        
        # Color based on threat level
        colors = {
            'low': (0, 255, 255),      # Yellow
            'medium': (0, 165, 255),   # Orange
            'high': (0, 0, 255),       # Red
            'critical': (128, 0, 128)  # Purple
        }
        color = colors.get(activity.threat_level.value, (255, 255, 255))
        
        # Draw alert box
        alert_text = f"ALERT: {activity.activity_type.value.upper()}"
        text_size = cv2.getTextSize(alert_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        
        # Background rectangle
        cv2.rectangle(frame, 
                     (x - text_size[0]//2 - 10, y - 40),
                     (x + text_size[0]//2 + 10, y - 10),
                     color, -1)
        
        # Alert text
        cv2.putText(frame, alert_text,
                   (x - text_size[0]//2, y - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw exclamation mark
        cv2.circle(frame, (x, y), 15, color, -1)
        cv2.putText(frame, "!", (x - 5, y + 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
    
    def _draw_stats_overlay(self, frame: np.ndarray):
        """
        Draw statistics overlay on frame
        
        Args:
            frame: Frame to draw on
        """
        h, w = frame.shape[:2]
        
        # Statistics text
        stats_text = [
            f"FPS: {self.stats['processing_fps']:.1f}",
            f"Frames: {self.stats['frames_processed']}",
            f"Persons: {self.stats['persons_detected']}",
            f"Faces: {self.stats['faces_recognized']}",
            f"Activities: {self.stats['activities_detected']}",
            f"Tracks: {len(self.tracker.get_all_tracks())}"
        ]
        
        # Draw background
        y_offset = 30
        for i, text in enumerate(stats_text):
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, 
                         (w - text_size[0] - 20, y_offset + i * 25 - 20),
                         (w - 10, y_offset + i * 25 + 5),
                         (0, 0, 0), -1)
            
            cv2.putText(frame, text,
                       (w - text_size[0] - 15, y_offset + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def get_latest_result(self) -> Optional[Dict]:
        """
        Get latest processing result
        
        Returns:
            Latest result dictionary or None
        """
        try:
            return self.result_queue.get(block=False)
        except queue.Empty:
            return None
    
    def get_statistics(self) -> Dict:
        """
        Get processing statistics
        
        Returns:
            Statistics dictionary
        """
        current_time = time.time()
        uptime = current_time - self.stats['start_time'] if self.stats['start_time'] > 0 else 0
        
        stats = self.stats.copy()
        stats['uptime'] = uptime
        stats['active_tracks'] = len(self.tracker.get_all_tracks())
        stats['recent_activities'] = len(self.activity_analyzer.get_recent_activities(60))
        
        return stats
    
    def save_snapshot(self, frame: Optional[np.ndarray] = None, prefix: str = "snapshot") -> str:
        """
        Save current frame as snapshot
        
        Args:
            frame: Frame to save (uses latest if None)
            prefix: Filename prefix
            
        Returns:
            Path to saved snapshot
        """
        if frame is None:
            result = self.get_latest_result()
            if result and 'output_frame' in result:
                frame = result['output_frame']
            else:
                return ""
        
        if frame is not None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.jpg"
            filepath = self.output_dir / filename
            
            cv2.imwrite(str(filepath), frame)
            return str(filepath)
        else:
            return ""

if __name__ == "__main__":
    # Test the surveillance manager
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Eyes Surveillance System")
    parser.add_argument("--camera", type=str, help="Camera URL or ID")
    parser.add_argument("--output", type=str, default="surveillance_output", help="Output directory")
    args = parser.parse_args()
    
    # Initialize surveillance manager
    if args.camera and args.camera.isdigit():
        manager = SurveillanceManager(camera_id=int(args.camera), output_dir=args.output)
    else:
        manager = SurveillanceManager(camera_url=args.camera, output_dir=args.output)
    
    # Add test detection zone
    test_zone = DetectionZone(
        name="Main Area",
        points=[(100, 100), (500, 100), (500, 400), (100, 400)],
        zone_type="monitored",
        activity_types=[ActivityType.LOITERING, ActivityType.UNAUTHORIZED_PERSON]
    )
    manager.add_detection_zone(test_zone)
    
    # Activity callback
    def on_activity(activity: SuspiciousActivity):
        print(f"ALERT: {activity.activity_type.value} detected!")
        print(f"  Threat Level: {activity.threat_level.value}")
        print(f"  Description: {activity.description}")
        print(f"  Location: {activity.location}")
        print(f"  Zone: {activity.zone_name}")
    
    manager.set_activity_callback(on_activity)
    
    # Start surveillance
    if manager.start_surveillance():
        print("Surveillance started. Press 'q' to quit.")
        
        try:
            while True:
                result = manager.get_latest_result()
                if result and 'output_frame' in result:
                    cv2.imshow('AI Eyes Surveillance', result['output_frame'])
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Print statistics every 30 frames
                if manager.stats['frames_processed'] % 30 == 0:
                    stats = manager.get_statistics()
                    print(f"Stats: FPS={stats['processing_fps']:.1f}, "
                          f"Tracks={stats['active_tracks']}, "
                          f"Activities={stats['recent_activities']}")
        
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            manager.stop_surveillance()
            cv2.destroyAllWindows()
    else:
        print("Failed to start surveillance system")