"""
Person Tracking Module
Track detected persons across frames using OpenCV trackers and assign unique IDs
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class PersonTracker:
    """
    Track multiple persons across video frames using OpenCV trackers
    Maintains unique track IDs and person state information
    """
    
    def __init__(self, 
                 tracker_type: str = 'CSRT',
                 max_tracks: int = 50,
                 track_timeout: float = 5.0,
                 min_track_length: int = 5):
        """
        Initialize person tracker
        
        Args:
            tracker_type: Type of OpenCV tracker ('CSRT', 'KCF', 'BOOSTING', 'MIL', 'TLD', 'MEDIANFLOW')
            max_tracks: Maximum number of simultaneous tracks
            track_timeout: Time in seconds before dropping inactive tracks
            min_track_length: Minimum number of frames to confirm a track
        """
        self.tracker_type = tracker_type
        self.max_tracks = max_tracks
        self.track_timeout = track_timeout
        self.min_track_length = min_track_length
        
        # Track management
        self.active_tracks = {}  # track_id -> tracker object
        self.track_states = {}   # track_id -> track state dict
        self.next_track_id = 1
        
        # Matching parameters
        self.iou_threshold = 0.5
        self.distance_threshold = 100
        
    def _create_tracker(self) -> Optional[cv2.Tracker]:
        """
        Create OpenCV tracker instance
        
        Returns:
            Tracker object or None if failed
        """
        try:
            if self.tracker_type == 'CSRT':
                return cv2.TrackerCSRT_create()
            elif self.tracker_type == 'KCF':
                return cv2.TrackerKCF_create()
            elif self.tracker_type == 'BOOSTING':
                return cv2.legacy.TrackerBoosting_create()
            elif self.tracker_type == 'MIL':
                return cv2.legacy.TrackerMIL_create()
            elif self.tracker_type == 'TLD':
                return cv2.legacy.TrackerTLD_create()
            elif self.tracker_type == 'MEDIANFLOW':
                return cv2.legacy.TrackerMedianFlow_create()
            else:
                logger.warning(f"Unknown tracker type: {self.tracker_type}, using CSRT")
                return cv2.TrackerCSRT_create()
        except Exception as e:
            logger.error(f"Failed to create tracker: {e}")
            return None
    
    def _calculate_iou(self, box1: List[int], box2: List[int]) -> float:
        """
        Calculate Intersection over Union (IoU) of two bounding boxes
        
        Args:
            box1: [x1, y1, x2, y2]
            box2: [x1, y1, x2, y2]
            
        Returns:
            IoU score between 0 and 1
        """
        # Convert to (x, y, w, h) format
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Calculate intersection
        xi1 = max(x1_1, x1_2)
        yi1 = max(y1_1, y1_2)
        xi2 = min(x2_1, x2_2)
        yi2 = min(y2_1, y2_2)
        
        if xi1 >= xi2 or yi1 >= yi2:
            return 0.0
        
        intersection = (xi2 - xi1) * (yi2 - yi1)
        
        # Calculate areas
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        # Calculate union
        union = area1 + area2 - intersection
        
        if union <= 0:
            return 0.0
        
        return intersection / union
    
    def _calculate_distance(self, center1: Tuple[int, int], center2: Tuple[int, int]) -> float:
        """
        Calculate Euclidean distance between two points
        
        Args:
            center1: (x, y) coordinates
            center2: (x, y) coordinates
            
        Returns:
            Euclidean distance
        """
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def _match_detections_to_tracks(self, detections: List[Dict]) -> Dict[int, int]:
        """
        Match new detections to existing tracks
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Dictionary mapping track_id to detection_index
        """
        if not self.active_tracks or not detections:
            return {}
        
        # Get current track positions
        track_positions = {}
        for track_id, state in self.track_states.items():
            if track_id in self.active_tracks:
                track_positions[track_id] = state['bbox']
        
        # Calculate IoU matrix
        matches = {}
        used_detections = set()
        
        for track_id, track_bbox in track_positions.items():
            best_iou = 0
            best_detection_idx = -1
            
            for det_idx, detection in enumerate(detections):
                if det_idx in used_detections:
                    continue
                
                det_bbox = detection['bbox']
                iou = self._calculate_iou(track_bbox, det_bbox)
                
                if iou > self.iou_threshold and iou > best_iou:
                    best_iou = iou
                    best_detection_idx = det_idx
            
            if best_detection_idx >= 0:
                matches[track_id] = best_detection_idx
                used_detections.add(best_detection_idx)
        
        return matches
    
    def update(self, frame: np.ndarray, detections: List[Dict]) -> Dict[int, Dict]:
        """
        Update tracker with new frame and detections
        
        Args:
            frame: Current frame
            detections: List of person detections
            
        Returns:
            Dictionary of active tracks with states
        """
        current_time = time.time()
        
        # Update existing trackers
        active_track_ids = list(self.active_tracks.keys())
        for track_id in active_track_ids:
            tracker = self.active_tracks[track_id]
            success, bbox = tracker.update(frame)
            
            if success:
                # Convert bbox format (x, y, w, h) to (x1, y1, x2, y2)
                x, y, w, h = bbox
                bbox_xyxy = [int(x), int(y), int(x + w), int(y + h)]
                
                # Update track state
                self.track_states[track_id]['bbox'] = bbox_xyxy
                self.track_states[track_id]['last_update'] = current_time
                self.track_states[track_id]['center'] = (int(x + w/2), int(y + h/2))
                self.track_states[track_id]['frame_count'] += 1
                
                # Update track history for activity analysis
                if 'position_history' not in self.track_states[track_id]:
                    self.track_states[track_id]['position_history'] = []
                
                self.track_states[track_id]['position_history'].append({
                    'timestamp': current_time,
                    'center': (int(x + w/2), int(y + h/2)),
                    'bbox': bbox_xyxy
                })
                
                # Keep only recent history (last 10 seconds)
                history = self.track_states[track_id]['position_history']
                self.track_states[track_id]['position_history'] = [
                    h for h in history if current_time - h['timestamp'] <= 10.0
                ]
                
            else:
                # Track failed, mark for removal
                self._remove_track(track_id)
        
        # Match detections to existing tracks
        matches = self._match_detections_to_tracks(detections)
        
        # Update matched tracks with detection information
        for track_id, det_idx in matches.items():
            detection = detections[det_idx]
            if track_id in self.track_states:
                self.track_states[track_id]['detection'] = detection
                self.track_states[track_id]['confidence'] = detection['confidence']
        
        # Create new tracks for unmatched detections
        matched_detection_indices = set(matches.values())
        for det_idx, detection in enumerate(detections):
            if det_idx not in matched_detection_indices and len(self.active_tracks) < self.max_tracks:
                self._create_new_track(frame, detection, current_time)
        
        # Remove timed out tracks
        self._cleanup_old_tracks(current_time)
        
        # Return only confirmed tracks
        confirmed_tracks = {}
        for track_id, state in self.track_states.items():
            if state['frame_count'] >= self.min_track_length:
                confirmed_tracks[track_id] = state.copy()
        
        return confirmed_tracks
    
    def _create_new_track(self, frame: np.ndarray, detection: Dict, timestamp: float):
        """
        Create new track for unmatched detection
        
        Args:
            frame: Current frame
            detection: Detection dictionary
            timestamp: Current timestamp
        """
        tracker = self._create_tracker()
        if tracker is None:
            return
        
        # Convert bbox format (x1, y1, x2, y2) to (x, y, w, h)
        x1, y1, x2, y2 = detection['bbox']
        bbox_xywh = (x1, y1, x2 - x1, y2 - y1)
        
        # Initialize tracker
        success = tracker.init(frame, bbox_xywh)
        if not success:
            logger.warning("Failed to initialize new tracker")
            return
        
        track_id = self.next_track_id
        self.next_track_id += 1
        
        # Store tracker and state
        self.active_tracks[track_id] = tracker
        self.track_states[track_id] = {
            'track_id': track_id,
            'bbox': detection['bbox'],
            'center': ((x1 + x2) // 2, (y1 + y2) // 2),
            'detection': detection,
            'confidence': detection['confidence'],
            'created_time': timestamp,
            'last_update': timestamp,
            'frame_count': 1,
            'position_history': [{
                'timestamp': timestamp,
                'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                'bbox': detection['bbox']
            }],
            'face_crops': [],  # Store face crops for recognition
            'identity': 'unknown',  # Will be updated by face recognition
            'authorization_status': 'pending'  # pending, authorized, intruder
        }
        
        logger.info(f"Created new track {track_id}")
    
    def _remove_track(self, track_id: int):
        """
        Remove track from active tracking
        
        Args:
            track_id: ID of track to remove
        """
        if track_id in self.active_tracks:
            del self.active_tracks[track_id]
        
        if track_id in self.track_states:
            logger.info(f"Removed track {track_id} after {self.track_states[track_id]['frame_count']} frames")
            del self.track_states[track_id]
    
    def _cleanup_old_tracks(self, current_time: float):
        """
        Remove tracks that haven't been updated recently
        
        Args:
            current_time: Current timestamp
        """
        expired_tracks = []
        for track_id, state in self.track_states.items():
            if current_time - state['last_update'] > self.track_timeout:
                expired_tracks.append(track_id)
        
        for track_id in expired_tracks:
            self._remove_track(track_id)
    
    def get_track_by_id(self, track_id: int) -> Optional[Dict]:
        """
        Get track state by ID
        
        Args:
            track_id: Track ID
            
        Returns:
            Track state dictionary or None
        """
        return self.track_states.get(track_id)
    
    def get_all_tracks(self) -> Dict[int, Dict]:
        """
        Get all active track states
        
        Returns:
            Dictionary of all track states
        """
        return self.track_states.copy()
    
    def get_track_count(self) -> int:
        """
        Get number of active tracks
        
        Returns:
            Number of active tracks
        """
        return len(self.active_tracks)
    
    def draw_tracks(self, frame: np.ndarray, tracks: Dict[int, Dict] = None) -> np.ndarray:
        """
        Draw tracking information on frame
        
        Args:
            frame: Input frame
            tracks: Track states (uses all tracks if None)
            
        Returns:
            Frame with tracking visualization
        """
        if tracks is None:
            tracks = self.track_states
        
        output_frame = frame.copy()
        
        for track_id, state in tracks.items():
            bbox = state['bbox']
            center = state['center']
            identity = state.get('identity', 'unknown')
            auth_status = state.get('authorization_status', 'pending')
            
            # Color based on authorization status
            colors = {
                'authorized': (0, 255, 0),    # Green
                'intruder': (0, 0, 255),      # Red
                'pending': (0, 255, 255),     # Yellow
                'unknown': (128, 128, 128)    # Gray
            }
            color = colors.get(auth_status, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(output_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Draw track ID and identity
            label = f"ID:{track_id} {identity} ({auth_status})"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(output_frame,
                         (bbox[0], bbox[1] - label_size[1] - 10),
                         (bbox[0] + label_size[0], bbox[1]),
                         color, -1)
            cv2.putText(output_frame, label,
                       (bbox[0], bbox[1] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw center point and trajectory
            cv2.circle(output_frame, center, 3, color, -1)
            
            # Draw trajectory if available
            if 'position_history' in state and len(state['position_history']) > 1:
                points = [h['center'] for h in state['position_history']]
                for i in range(1, len(points)):
                    cv2.line(output_frame, points[i-1], points[i], color, 2)
        
        return output_frame

if __name__ == "__main__":
    # Test the tracker
    tracker = PersonTracker()
    
    # Test with webcam (requires YOLOv9 detector for actual persons)
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Mock detections for testing (replace with actual YOLO detections)
        mock_detections = [
            {
                'bbox': [100, 100, 200, 300],
                'confidence': 0.8,
                'class_id': 0,
                'class_name': 'person'
            }
        ]
        
        tracks = tracker.update(frame, mock_detections)
        output_frame = tracker.draw_tracks(frame, tracks)
        
        cv2.imshow('Person Tracking', output_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()