"""
YOLOv9 Object Detection Module
Real-time detection of persons, weapons, bags, and other objects
"""

import cv2
import numpy as np
import torch
import os
from typing import List, Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class YOLOv9Detector:
    """
    YOLOv9 object detector for surveillance applications
    Detects persons, weapons, bags, and other security-relevant objects
    """
    
    def __init__(self, 
                 model_path: str = None,
                 conf_threshold: float = 0.5,
                 nms_threshold: float = 0.4,
                 device: str = 'cpu'):
        """
        Initialize YOLOv9 detector
        
        Args:
            model_path: Path to YOLOv9 model weights
            conf_threshold: Confidence threshold for detections
            nms_threshold: Non-maximum suppression threshold
            device: Device to run inference on ('cpu' or 'cuda')
        """
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self.device = device
        
        # Security-relevant COCO class names and IDs
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]
        
        # Security-relevant classes
        self.security_classes = {
            0: 'person',      # Most important for surveillance
            24: 'backpack',   # Potential threat item
            26: 'handbag',    # Potential threat item
            28: 'suitcase',   # Potential threat item
            34: 'baseball bat',  # Potential weapon
            43: 'knife',      # Weapon
            76: 'scissors'    # Potential weapon
        }
        
        self.model = None
        self.load_model(model_path)
        
    def load_model(self, model_path: str = None):
        """
        Load YOLOv9 model
        
        Args:
            model_path: Path to model weights file
        """
        try:
            # Try to import ultralytics YOLO first
            from ultralytics import YOLO
            
            if model_path and os.path.exists(model_path):
                # Load custom model
                self.model = YOLO(model_path)
                logger.info(f"Loaded custom YOLOv9 model from {model_path}")
            else:
                # Try YOLOv9 models first, fallback to YOLOv8
                try:
                    # Look for YOLOv9 in models directory
                    model_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'models')
                    yolo9_path = os.path.join(model_dir, 'yolov9c.pt')
                    
                    if os.path.exists(yolo9_path):
                        self.model = YOLO(yolo9_path)
                        logger.info(f"Loaded YOLOv9 model from {yolo9_path}")
                    else:
                        # Use YOLOv8 as fallback (more stable)
                        self.model = YOLO('yolov8n.pt')
                        logger.info("Loaded YOLOv8n model as fallback")
                except Exception:
                    # Final fallback to torch hub
                    self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
                    logger.info("Loaded pretrained YOLOv5 model as final fallback")
            
            # Configure model
            if hasattr(self.model, 'conf'):
                self.model.conf = self.conf_threshold
            if hasattr(self.model, 'iou'):
                self.model.iou = self.nms_threshold
            
            # Set device for torch hub models
            if hasattr(self.model, 'to'):
                if self.device == 'cuda' and torch.cuda.is_available():
                    self.model = self.model.to('cuda')
                    logger.info("Using GPU for inference")
                else:
                    self.model = self.model.to('cpu')
                    logger.info("Using CPU for inference")
                
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in frame
        
        Args:
            frame: Input BGR image
            
        Returns:
            List of detection dictionaries with bbox, confidence, class_id, class_name
        """
        if self.model is None:
            logger.warning("Model not loaded")
            return []
        
        try:
            # Run inference with verbose output enabled to see detections
            results = self.model(frame, verbose=True, conf=self.conf_threshold, max_det=20)
            
            # Parse results
            detections = []
            
            # Handle different model types
            if hasattr(results, 'xyxy') and hasattr(results, 'pandas'):
                # YOLOv5 torch hub format
                result_data = results.pandas().xyxy[0]
                for _, row in result_data.iterrows():
                    class_id = int(row['class'])
                    class_name = row['name']
                    conf = float(row['confidence'])
                    
                    if conf >= self.conf_threshold:
                        detection_dict = {
                            'bbox': [int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])],
                            'confidence': conf,
                            'class_id': class_id,
                            'class_name': class_name,
                            'is_security_relevant': class_id in self.security_classes,
                            'threat_level': self._assess_threat_level(class_id, conf)
                        }
                        detections.append(detection_dict)
            else:
                # Ultralytics YOLO format
                for result in results:
                    if result.boxes is not None:
                        boxes = result.boxes
                        for i in range(len(boxes)):
                            # Get box coordinates
                            box = boxes.xyxy[i].cpu().numpy()
                            conf = float(boxes.conf[i].cpu().numpy())
                            class_id = int(boxes.cls[i].cpu().numpy())
                            
                            if conf >= self.conf_threshold:
                                class_name = self.class_names[class_id] if class_id < len(self.class_names) else 'unknown'
                                
                                detection_dict = {
                                    'bbox': [int(box[0]), int(box[1]), int(box[2]), int(box[3])],
                                    'confidence': conf,
                                    'class_id': class_id,
                                    'class_name': class_name,
                                    'is_security_relevant': class_id in self.security_classes,
                                    'threat_level': self._assess_threat_level(class_id, conf)
                                }
                                detections.append(detection_dict)
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []
    
    def _assess_threat_level(self, class_id: int, confidence: float) -> str:
        """
        Assess threat level of detected object
        
        Args:
            class_id: Object class ID
            confidence: Detection confidence
            
        Returns:
            Threat level: 'low', 'medium', 'high'
        """
        if class_id == 0:  # person
            return 'medium'  # Depends on authorization status
        elif class_id in [34, 43, 76]:  # weapons
            return 'high'
        elif class_id in [24, 26, 28]:  # bags
            return 'low'
        else:
            return 'low'
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw detection bounding boxes on frame
        
        Args:
            frame: Input frame
            detections: List of detection dictionaries
            
        Returns:
            Frame with drawn detections
        """
        output_frame = frame.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            threat_level = detection['threat_level']
            
            # Color based on threat level
            colors = {
                'low': (0, 255, 0),      # Green
                'medium': (0, 255, 255),  # Yellow
                'high': (0, 0, 255)       # Red
            }
            color = colors.get(threat_level, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(output_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(output_frame, 
                         (bbox[0], bbox[1] - label_size[1] - 10),
                         (bbox[0] + label_size[0], bbox[1]), 
                         color, -1)
            cv2.putText(output_frame, label, 
                       (bbox[0], bbox[1] - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return output_frame
    
    def filter_persons(self, detections: List[Dict]) -> List[Dict]:
        """
        Filter detections to only include persons
        
        Args:
            detections: List of all detections
            
        Returns:
            List of person detections only
        """
        return [det for det in detections if det['class_id'] == 0]
    
    def filter_weapons(self, detections: List[Dict]) -> List[Dict]:
        """
        Filter detections to only include potential weapons
        
        Args:
            detections: List of all detections
            
        Returns:
            List of weapon detections only
        """
        weapon_classes = [34, 43, 76]  # baseball bat, knife, scissors
        return [det for det in detections if det['class_id'] in weapon_classes]
    
    def filter_bags(self, detections: List[Dict]) -> List[Dict]:
        """
        Filter detections to only include bags/luggage
        
        Args:
            detections: List of all detections
            
        Returns:
            List of bag detections only
        """
        bag_classes = [24, 26, 28]  # backpack, handbag, suitcase
        return [det for det in detections if det['class_id'] in bag_classes]
    
    def assess_threat_level(self, detections: List[Dict]) -> str:
        """
        Assess overall threat level from all detections
        
        Args:
            detections: List of all detections
            
        Returns:
            Overall threat level: 'low', 'medium', 'high'
        """
        if not detections:
            return 'low'
        
        # Find highest threat level
        threat_levels = [det['threat_level'] for det in detections]
        
        if 'high' in threat_levels:
            return 'high'
        elif 'medium' in threat_levels:
            return 'medium'
        else:
            return 'low'

if __name__ == "__main__":
    # Test the detector
    detector = YOLOv9Detector()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        detections = detector.detect(frame)
        output_frame = detector.draw_detections(frame, detections)
        
        cv2.imshow('YOLOv9 Detection', output_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()