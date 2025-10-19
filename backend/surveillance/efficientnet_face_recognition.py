"""
MobileNetV2 Face Recognition Module - Wrapper for AI Eyes Surveillance System
Integrates MobileNetV2 model for accurate face recognition

Works with ImageNet weights and small datasets
"""

import cv2
import numpy as np
import os
import sys
from typing import Optional
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import the MobileNetV2 model
try:
    # Add ai_models directory to path
    current_dir = Path(__file__).parent.parent
    ai_models_path = current_dir / "ai_models" / "face_recognition"
    sys.path.insert(0, str(ai_models_path))
    
    from mobilenet_face_recognition import MobileNetFaceRecognitionSystem
    MOBILENET_AVAILABLE = True
    logger.info("✅ Using MobileNetV2 with MediaPipe face detection")
        
except ImportError as e:
    logger.warning(f"⚠️ MobileNetV2 model import failed: {e}")
    logger.warning("⚠️ Face recognition will not be available")
    MOBILENET_AVAILABLE = False

class EfficientNetFaceRecognizer:
    """
    Wrapper for EfficientNet B7 Face Recognition
    Provides consistent API for the surveillance system
    """
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 confidence_threshold: float = 0.50):
        """
        Initialize EfficientNet face recognizer
        
        Args:
            model_path: Path to the trained model (without extension)
            confidence_threshold: Confidence threshold for recognition (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.is_trained = False
        
        if not MOBILENET_AVAILABLE:
            logger.error("❌ MobileNetV2 system not available!")
            logger.error("💡 Solution: Install required packages (tensorflow, mediapipe)")
            return
        
        # Initialize the MobileNetV2 system
        logger.info("Initializing MobileNetV2 Face Recognition System...")
        self.recognizer_system = MobileNetFaceRecognitionSystem()
        
        # Set default model path if not provided
        if model_path is None:
            ai_models_dir = Path(__file__).parent.parent / "ai_models" / "face_recognition"
            model_path = str(ai_models_dir / "mobilenet_face_model_v2")  # Use v2 with Unknown class
        
        self.model_path = model_path
        self.is_trained = False
        
        # Try to load existing model
        if self.load_model(model_path):
            self.is_trained = True
            logger.info("✅ MobileNetV2 model loaded successfully")
        else:
            logger.warning("⚠️ No trained MobileNetV2 model found")
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load the trained EfficientNet model
        
        Args:
            model_path: Path to model files (without extension)
            
        Returns:
            True if model loaded successfully
        """
        try:
            if model_path is None:
                model_path = self.model_path
            
            success = self.recognizer_system.load_model(model_path)
            if success:
                self.is_trained = True
                logger.info(f"MobileNetV2 model loaded from: {model_path}")
                logger.info(f"Authorized persons: {', '.join(self.recognizer_system.authorized_persons)}")
            return success
            
        except Exception as e:
            logger.error(f"Error loading MobileNetV2 model: {e}")
            return False
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame using MediaPipe (integrated in MobileNetV2 system)
        
        Args:
            frame: Input BGR frame
            
        Returns:
            List of face bounding boxes (x, y, w, h) - converted from (top, right, bottom, left)
        """
        try:
            # Use the MobileNetV2 system's face detection
            face_locations = self.recognizer_system.detect_faces(frame)
            
            # Convert from (top, right, bottom, left) to (x, y, w, h)
            converted_boxes = []
            for (top, right, bottom, left) in face_locations:
                x = left
                y = top
                w = right - left
                h = bottom - top
                converted_boxes.append((x, y, w, h))
            
            return converted_boxes
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []
    
    def recognize_faces(self, frame: np.ndarray, face_bboxes: Optional[List[Tuple[int, int, int, int]]] = None) -> List[Dict]:
        """
        Recognize faces in frame
        
        Args:
            frame: Input BGR frame
            face_bboxes: Optional pre-detected face bounding boxes (x, y, w, h)
            
        Returns:
            List of recognition results with format:
            {
                'name': str,
                'confidence': float,
                'bbox': (x, y, w, h),
                'is_authorized': bool
            }
        """
        if not self.is_trained:
            logger.warning("Model not trained, cannot recognize faces")
            return []
        
        try:
            # Use MobileNetV2's recognition
            face_names, face_locations, verification_results = self.recognizer_system.recognize_faces_in_frame(frame)
            
            # Format results
            results = []
            for i, (name, (top, right, bottom, left), is_authorized) in enumerate(zip(face_names, face_locations, verification_results)):
                # Convert bbox to (x, y, w, h)
                x = left
                y = top
                w = right - left
                h = bottom - top
                
                result = {
                    'name': name,
                    'confidence': 0.75 if is_authorized else 0.25,  # Approximate confidence
                    'bbox': (x, y, w, h),
                    'is_authorized': bool(is_authorized)
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Face recognition failed: {e}")
            return []
    
    def recognize_single_face(self, frame: np.ndarray, face_bbox: Tuple[int, int, int, int]) -> Optional[Dict]:
        """
        Recognize a single face from a bounding box
        
        Args:
            frame: Input BGR frame
            face_bbox: Face bounding box (x, y, w, h)
            
        Returns:
            Recognition result or None
        """
        try:
            x, y, w, h = face_bbox
            
            # Extract face region
            face_image = frame[y:y+h, x:x+w]
            
            if face_image.size == 0:
                return None
            
            # Create a temporary frame with just this face
            temp_frame = frame.copy()
            
            # Get features
            features = self.recognizer_system.extract_face_features(face_image)
            if features is None:
                return {
                    'name': 'Unknown',
                    'confidence': 0.0,
                    'bbox': face_bbox,
                    'is_authorized': False
                }
            
            # Predict
            features_reshaped = features.reshape(1, -1)
            predictions = self.recognizer_system.classifier_model.predict(features_reshaped, verbose=0)  # type: ignore
            
            max_prob_index = np.argmax(predictions[0])
            max_probability = predictions[0][max_prob_index]
            
            if max_probability >= self.confidence_threshold:
                predicted_label = self.recognizer_system.label_encoder.inverse_transform([max_prob_index])[0]  # type: ignore
                return {
                    'name': predicted_label,
                    'confidence': float(max_probability),
                    'bbox': face_bbox,
                    'is_authorized': True
                }
            else:
                return {
                    'name': 'Unknown',
                    'confidence': float(max_probability),
                    'bbox': face_bbox,
                    'is_authorized': False
                }
                
        except Exception as e:
            logger.error(f"Single face recognition failed: {e}")
            return None
    
    def get_authorized_persons(self) -> List[str]:
        """Get list of authorized person names"""
        if self.is_trained:
            return self.recognizer_system.authorized_persons
        return []
    
    def draw_face_recognition(self, frame: np.ndarray, results: List[Dict]) -> np.ndarray:
        """
        Draw face recognition results on frame
        
        Args:
            frame: Input frame
            results: Recognition results from recognize_faces()
            
        Returns:
            Frame with drawn annotations
        """
        annotated_frame = frame.copy()
        
        for result in results:
            name = result['name']
            bbox = result['bbox']
            is_authorized = result['is_authorized']
            confidence = result.get('confidence', 0.0)
            
            x, y, w, h = bbox
            
            # Choose color
            color = (0, 255, 0) if is_authorized else (0, 0, 255)  # Green/Red
            
            # Draw rectangle
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label with confidence
            label = f"{name} ({confidence:.0%})" if is_authorized else "Unauthorized"
            
            # Draw background for text
            cv2.rectangle(annotated_frame, (x, y - 25), (x + w, y), color, cv2.FILLED)
            cv2.putText(annotated_frame, label, (x + 6, y - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return annotated_frame

    def __str__(self):
        """String representation"""
        if self.is_trained:
            return f"MobileNetV2 FaceRecognizer (Trained, {len(self.get_authorized_persons())} persons)"
        return "MobileNetV2 FaceRecognizer (Not Trained)"
