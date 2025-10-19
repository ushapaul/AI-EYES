"""
Suspicious Activity Analyzer Module
Detects various suspicious activities including loitering, zone intrusion, 
abandoned objects, and weapon detection
"""

import cv2
import numpy as np
import time
from typing import Dict, List, Tuple, Optional, Set
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ActivityType(Enum):
    """Types of suspicious activities"""
    LOITERING = "loitering"
    ZONE_INTRUSION = "zone_intrusion" 
    ABANDONED_OBJECT = "abandoned_object"
    WEAPON_DETECTED = "weapon_detected"
    UNAUTHORIZED_PERSON = "unauthorized_person"
    CROWD_FORMATION = "crowd_formation"
    RUNNING = "running"
    FIGHTING = "fighting"

class ThreatLevel(Enum):
    """Threat levels for activities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DetectionZone:
    """Represents a detection zone in the frame"""
    name: str
    points: List[Tuple[int, int]]  # Polygon points
    zone_type: str  # "restricted", "monitored", "safe"
    activity_types: List[ActivityType]  # Activities to detect in this zone

@dataclass
class SuspiciousActivity:
    """Represents a detected suspicious activity"""
    activity_type: ActivityType
    threat_level: ThreatLevel
    track_id: int
    description: str
    timestamp: float
    location: Tuple[int, int]  # Center point
    zone_name: str
    confidence: float
    evidence: Dict  # Additional evidence (images, tracks, etc.)

class SuspiciousActivityAnalyzer:
    """
    Analyzes person tracks and detections for suspicious activities
    """
    
    def __init__(self, 
                 loitering_threshold: float = 30.0,
                 abandoned_object_threshold: float = 60.0,
                 speed_threshold: float = 5.0,
                 crowd_threshold: int = 5):
        """
        Initialize activity analyzer
        
        Args:
            loitering_threshold: Time in seconds for loitering detection
            abandoned_object_threshold: Time in seconds for abandoned object detection
            speed_threshold: Speed threshold for running detection (pixels/second)
            crowd_threshold: Number of people for crowd formation detection
        """
        self.loitering_threshold = loitering_threshold
        self.abandoned_object_threshold = abandoned_object_threshold
        self.speed_threshold = speed_threshold
        self.crowd_threshold = crowd_threshold
        
        # Detection zones
        self.zones: List[DetectionZone] = []
        
        # Activity tracking
        self.active_activities: Dict[str, SuspiciousActivity] = {}  # activity_id -> activity
        self.activity_history: List[SuspiciousActivity] = []
        
        # Object tracking for abandoned objects
        self.stationary_objects: Dict[str, Dict] = {}  # object_id -> state
        
        # Zone intrusion tracking
        self.zone_intrusions: Dict[Tuple[int, str], float] = {}  # (track_id, zone_name) -> start_time
        
    def add_detection_zone(self, zone: DetectionZone):
        """
        Add a detection zone
        
        Args:
            zone: DetectionZone object
        """
        self.zones.append(zone)
        logger.info(f"Added detection zone: {zone.name} ({zone.zone_type})")
    
    def remove_detection_zone(self, zone_name: str):
        """
        Remove a detection zone by name
        
        Args:
            zone_name: Name of zone to remove
        """
        self.zones = [z for z in self.zones if z.name != zone_name]
        logger.info(f"Removed detection zone: {zone_name}")
    
    def point_in_polygon(self, point: Tuple[int, int], polygon: List[Tuple[int, int]]) -> bool:
        """
        Check if point is inside polygon using ray casting algorithm
        
        Args:
            point: (x, y) coordinates
            polygon: List of polygon vertices
            
        Returns:
            True if point is inside polygon
        """
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def get_zone_for_point(self, point: Tuple[int, int]) -> Optional[DetectionZone]:
        """
        Get the detection zone containing a point
        
        Args:
            point: (x, y) coordinates
            
        Returns:
            DetectionZone or None if not in any zone
        """
        for zone in self.zones:
            if self.point_in_polygon(point, zone.points):
                return zone
        return None
    
    def calculate_movement_speed(self, track_state: Dict) -> float:
        """
        Calculate movement speed of a track
        
        Args:
            track_state: Track state dictionary
            
        Returns:
            Speed in pixels per second
        """
        if 'position_history' not in track_state or len(track_state['position_history']) < 2:
            return 0.0
        
        history = track_state['position_history']
        recent_positions = history[-5:]  # Last 5 positions
        
        if len(recent_positions) < 2:
            return 0.0
        
        # Calculate total distance and time
        total_distance = 0.0
        total_time = 0.0
        
        for i in range(1, len(recent_positions)):
            pos1 = recent_positions[i-1]['center']
            pos2 = recent_positions[i]['center']
            time1 = recent_positions[i-1]['timestamp']
            time2 = recent_positions[i]['timestamp']
            
            distance = np.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
            time_diff = time2 - time1
            
            total_distance += distance
            total_time += time_diff
        
        if total_time > 0:
            return total_distance / total_time
        return 0.0
    
    def detect_loitering(self, track_state: Dict, current_time: float) -> Optional[SuspiciousActivity]:
        """
        Detect loitering behavior
        
        Args:
            track_state: Track state dictionary
            current_time: Current timestamp
            
        Returns:
            SuspiciousActivity if detected, None otherwise
        """
        track_id = track_state['track_id']
        center = track_state['center']
        
        # Check if person is in a monitored zone
        zone = self.get_zone_for_point(center)
        if zone is None or ActivityType.LOITERING not in zone.activity_types:
            return None
        
        # Check time spent in current location
        if 'position_history' not in track_state:
            return None
        
        # Calculate how long person has been in roughly the same area
        recent_positions = [h for h in track_state['position_history'] 
                          if current_time - h['timestamp'] <= self.loitering_threshold]
        
        if len(recent_positions) < 2:
            return None
        
        # Check if movement is minimal (within small radius)
        loiter_radius = 50  # pixels
        start_pos = recent_positions[0]['center']
        
        is_loitering = True
        for pos_data in recent_positions[1:]:
            pos = pos_data['center']
            distance = np.sqrt((pos[0] - start_pos[0])**2 + (pos[1] - start_pos[1])**2)
            if distance > loiter_radius:
                is_loitering = False
                break
        
        if is_loitering and len(recent_positions) >= self.loitering_threshold * 2:  # Approximate frame rate
            return SuspiciousActivity(
                activity_type=ActivityType.LOITERING,
                threat_level=ThreatLevel.MEDIUM,
                track_id=track_id,
                description=f"Person loitering in {zone.name} for {self.loitering_threshold}+ seconds",
                timestamp=current_time,
                location=center,
                zone_name=zone.name,
                confidence=0.8,
                evidence={'duration': len(recent_positions) / 2, 'zone': zone.name}
            )
        
        return None
    
    def detect_zone_intrusion(self, track_state: Dict, current_time: float) -> Optional[SuspiciousActivity]:
        """
        Detect unauthorized zone intrusion
        
        Args:
            track_state: Track state dictionary
            current_time: Current timestamp
            
        Returns:
            SuspiciousActivity if detected, None otherwise
        """
        track_id = track_state['track_id']
        center = track_state['center']
        auth_status = track_state.get('authorization_status', 'unknown')
        
        # Check if person is in a restricted zone
        zone = self.get_zone_for_point(center)
        if zone is None or zone.zone_type != 'restricted':
            return None
        
        if ActivityType.ZONE_INTRUSION not in zone.activity_types:
            return None
        
        # Check authorization status
        if auth_status in ['authorized']:
            return None  # Authorized persons can be in restricted zones
        
        # Check if this is a new intrusion
        intrusion_key = (track_id, zone.name)
        if intrusion_key not in self.zone_intrusions:
            self.zone_intrusions[intrusion_key] = current_time
            
            threat_level = ThreatLevel.HIGH if auth_status == 'intruder' else ThreatLevel.MEDIUM
            
            return SuspiciousActivity(
                activity_type=ActivityType.ZONE_INTRUSION,
                threat_level=threat_level,
                track_id=track_id,
                description=f"Unauthorized person entered restricted zone: {zone.name}",
                timestamp=current_time,
                location=center,
                zone_name=zone.name,
                confidence=0.9,
                evidence={'authorization_status': auth_status, 'zone_type': zone.zone_type}
            )
        
        return None
    
    def detect_unauthorized_person(self, track_state: Dict, current_time: float) -> Optional[SuspiciousActivity]:
        """
        Detect unauthorized persons (intruders)
        
        Args:
            track_state: Track state dictionary
            current_time: Current timestamp
            
        Returns:
            SuspiciousActivity if detected, None otherwise
        """
        track_id = track_state['track_id']
        center = track_state['center']
        auth_status = track_state.get('authorization_status', 'unknown')
        identity = track_state.get('identity', 'unknown')
        
        # Only trigger for confirmed intruders
        if auth_status != 'intruder':
            return None
        
        # Check if already reported for this track
        activity_id = f"unauthorized_{track_id}"
        if activity_id in self.active_activities:
            return None
        
        zone = self.get_zone_for_point(center)
        zone_name = zone.name if zone else "unknown_area"
        
        activity = SuspiciousActivity(
            activity_type=ActivityType.UNAUTHORIZED_PERSON,
            threat_level=ThreatLevel.HIGH,
            track_id=track_id,
            description=f"Unauthorized person detected: {identity}",
            timestamp=current_time,
            location=center,
            zone_name=zone_name,
            confidence=0.95,
            evidence={'identity': identity, 'authorization_status': auth_status}
        )
        
        self.active_activities[activity_id] = activity
        return activity
    
    def detect_weapon(self, detections: List[Dict], tracks: Dict[int, Dict], current_time: float) -> List[SuspiciousActivity]:
        """
        Detect weapons in detections and associate with tracks
        
        Args:
            detections: List of object detections
            tracks: Dictionary of track states
            current_time: Current timestamp
            
        Returns:
            List of weapon-related suspicious activities
        """
        activities = []
        
        # Filter weapon detections
        weapon_classes = [34, 43, 76]  # baseball bat, knife, scissors
        weapon_detections = [det for det in detections if det['class_id'] in weapon_classes]
        
        for weapon_det in weapon_detections:
            weapon_center = (
                (weapon_det['bbox'][0] + weapon_det['bbox'][2]) // 2,
                (weapon_det['bbox'][1] + weapon_det['bbox'][3]) // 2
            )
            
            # Find closest person track
            closest_track_id = None
            min_distance = float('inf')
            
            for track_id, track_state in tracks.items():
                track_center = track_state['center']
                distance = np.sqrt((weapon_center[0] - track_center[0])**2 + 
                                 (weapon_center[1] - track_center[1])**2)
                
                if distance < min_distance and distance < 100:  # Within 100 pixels
                    min_distance = distance
                    closest_track_id = track_id
            
            if closest_track_id is not None:
                zone = self.get_zone_for_point(weapon_center)
                zone_name = zone.name if zone else "unknown_area"
                
                activity = SuspiciousActivity(
                    activity_type=ActivityType.WEAPON_DETECTED,
                    threat_level=ThreatLevel.CRITICAL,
                    track_id=closest_track_id,
                    description=f"Weapon detected: {weapon_det['class_name']}",
                    timestamp=current_time,
                    location=weapon_center,
                    zone_name=zone_name,
                    confidence=weapon_det['confidence'],
                    evidence={'weapon_type': weapon_det['class_name'], 
                             'weapon_confidence': weapon_det['confidence']}
                )
                
                activities.append(activity)
        
        return activities
    
    def detect_abandoned_objects(self, detections: List[Dict], current_time: float) -> List[SuspiciousActivity]:
        """
        Detect abandoned objects (bags, suitcases)
        
        Args:
            detections: List of object detections
            current_time: Current timestamp
            
        Returns:
            List of abandoned object activities
        """
        activities = []
        
        # Filter bag detections
        bag_classes = [24, 26, 28]  # backpack, handbag, suitcase
        bag_detections = [det for det in detections if det['class_id'] in bag_classes]
        
        for bag_det in bag_detections:
            bag_center = (
                (bag_det['bbox'][0] + bag_det['bbox'][2]) // 2,
                (bag_det['bbox'][1] + bag_det['bbox'][3]) // 2
            )
            
            # Create object ID based on location
            object_id = f"bag_{bag_center[0]}_{bag_center[1]}"
            
            # Check if object is stationary
            if object_id not in self.stationary_objects:
                self.stationary_objects[object_id] = {
                    'first_seen': current_time,
                    'last_seen': current_time,
                    'location': bag_center,
                    'detection': bag_det
                }
            else:
                # Update last seen time
                obj_state = self.stationary_objects[object_id]
                obj_state['last_seen'] = current_time
                
                # Check if object has been abandoned
                time_stationary = current_time - obj_state['first_seen']
                if time_stationary >= self.abandoned_object_threshold:
                    zone = self.get_zone_for_point(bag_center)
                    zone_name = zone.name if zone else "unknown_area"
                    
                    activity = SuspiciousActivity(
                        activity_type=ActivityType.ABANDONED_OBJECT,
                        threat_level=ThreatLevel.MEDIUM,
                        track_id=-1,  # Not associated with a specific person
                        description=f"Abandoned object detected: {bag_det['class_name']}",
                        timestamp=current_time,
                        location=bag_center,
                        zone_name=zone_name,
                        confidence=bag_det['confidence'],
                        evidence={'object_type': bag_det['class_name'],
                                'time_abandoned': time_stationary}
                    )
                    
                    activities.append(activity)
                    # Remove from tracking to avoid duplicate alerts
                    del self.stationary_objects[object_id]
        
        # Clean up old objects
        cutoff_time = current_time - self.abandoned_object_threshold * 2
        self.stationary_objects = {
            k: v for k, v in self.stationary_objects.items()
            if v['last_seen'] > cutoff_time
        }
        
        return activities
    
    def detect_running(self, track_state: Dict, current_time: float) -> Optional[SuspiciousActivity]:
        """
        Detect running behavior based on movement speed
        
        Args:
            track_state: Track state dictionary
            current_time: Current timestamp
            
        Returns:
            SuspiciousActivity if detected, None otherwise
        """
        track_id = track_state['track_id']
        center = track_state['center']
        
        speed = self.calculate_movement_speed(track_state)
        
        if speed > self.speed_threshold:
            zone = self.get_zone_for_point(center)
            zone_name = zone.name if zone else "unknown_area"
            
            return SuspiciousActivity(
                activity_type=ActivityType.RUNNING,
                threat_level=ThreatLevel.LOW,
                track_id=track_id,
                description=f"Person running at high speed: {speed:.1f} px/s",
                timestamp=current_time,
                location=center,
                zone_name=zone_name,
                confidence=0.7,
                evidence={'speed': speed, 'threshold': self.speed_threshold}
            )
        
        return None
    
    def analyze_frame(self, detections: List[Dict], tracks: Dict[int, Dict], current_time: float) -> List[SuspiciousActivity]:
        """
        Analyze frame for all types of suspicious activities
        
        Args:
            detections: List of object detections
            tracks: Dictionary of track states
            current_time: Current timestamp
            
        Returns:
            List of detected suspicious activities
        """
        activities = []
        
        # Analyze each track for person-based activities
        for track_id, track_state in tracks.items():
            # Skip tracks without enough history
            if track_state.get('frame_count', 0) < 10:
                continue
            
            # Detect loitering
            loitering = self.detect_loitering(track_state, current_time)
            if loitering:
                activities.append(loitering)
            
            # Detect zone intrusion
            intrusion = self.detect_zone_intrusion(track_state, current_time)
            if intrusion:
                activities.append(intrusion)
            
            # Detect unauthorized persons
            unauthorized = self.detect_unauthorized_person(track_state, current_time)
            if unauthorized:
                activities.append(unauthorized)
            
            # Detect running
            running = self.detect_running(track_state, current_time)
            if running:
                activities.append(running)
        
        # Detect weapon-related activities
        weapon_activities = self.detect_weapon(detections, tracks, current_time)
        activities.extend(weapon_activities)
        
        # Detect abandoned objects
        abandoned_activities = self.detect_abandoned_objects(detections, current_time)
        activities.extend(abandoned_activities)
        
        # Store activities in history
        for activity in activities:
            self.activity_history.append(activity)
        
        # Clean up old activities from history (keep last 1000)
        if len(self.activity_history) > 1000:
            self.activity_history = self.activity_history[-1000:]
        
        return activities
    
    def get_recent_activities(self, time_window: float = 300.0) -> List[SuspiciousActivity]:
        """
        Get recent suspicious activities within time window
        
        Args:
            time_window: Time window in seconds
            
        Returns:
            List of recent activities
        """
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        return [activity for activity in self.activity_history 
                if activity.timestamp > cutoff_time]
    
    def draw_zones(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw detection zones on frame
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with zones drawn
        """
        output_frame = frame.copy()
        
        zone_colors = {
            'restricted': (0, 0, 255),    # Red
            'monitored': (0, 255, 255),   # Yellow
            'safe': (0, 255, 0)           # Green
        }
        
        for zone in self.zones:
            color = zone_colors.get(zone.zone_type, (255, 255, 255))
            
            # Draw zone polygon
            points = np.array(zone.points, np.int32)
            points = points.reshape((-1, 1, 2))
            cv2.polylines(output_frame, [points], True, color, 2)
            
            # Draw zone label
            if zone.points:
                center_x = sum(p[0] for p in zone.points) // len(zone.points)
                center_y = sum(p[1] for p in zone.points) // len(zone.points)
                
                cv2.putText(output_frame, f"{zone.name} ({zone.zone_type})",
                           (center_x - 50, center_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return output_frame

if __name__ == "__main__":
    # Test the activity analyzer
    analyzer = SuspiciousActivityAnalyzer()
    
    # Add test zones
    restricted_zone = DetectionZone(
        name="Entrance",
        points=[(100, 100), (300, 100), (300, 200), (100, 200)],
        zone_type="restricted",
        activity_types=[ActivityType.ZONE_INTRUSION, ActivityType.LOITERING]
    )
    analyzer.add_detection_zone(restricted_zone)
    
    print("Activity analyzer initialized with test zone")
    print(f"Known zones: {[z.name for z in analyzer.zones]}")