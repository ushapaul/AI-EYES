"""
LBPH Face Recognition Module
Face detection and recognition system for identifying authorized vs unknown persons
"""

import cv2
import numpy as np
import os
import pickle
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LBPHFaceRecognizer:
    """
    Local Binary Pattern Histograms (LBPH) face recognizer
    Detects faces and identifies known/unknown persons for security
    """
    
    def __init__(self, 
                 known_faces_dir: str = "data/known_faces",
                 confidence_threshold: float = 100.0,
                 face_cascade_path: str = None):
        """
        Initialize LBPH face recognizer
        
        Args:
            known_faces_dir: Directory containing known face images
            confidence_threshold: Confidence threshold for recognition (lower = more strict)
            face_cascade_path: Path to Haar cascade file
        """
        self.known_faces_dir = Path(known_faces_dir)
        self.confidence_threshold = confidence_threshold
        
        # Initialize face detector
        if face_cascade_path and os.path.exists(face_cascade_path):
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        else:
            # Use default OpenCV Haar cascade
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        
        # Initialize LBPH recognizer
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Face database
        self.face_labels = {}  # label_id -> person_name
        self.label_counter = 0
        self.is_trained = False
        
        # Model persistence
        self.model_path = self.known_faces_dir.parent / "lbph_model.yml"
        self.labels_path = self.known_faces_dir.parent / "face_labels.pkl"
        
        # Load existing model if available
        self.load_model()
        
        # If no model exists, train from known faces directory
        if not self.is_trained:
            self.train_from_directory()
    
    def detect_faces(self, frame: np.ndarray, scale_factor: float = 1.02, min_neighbors: int = 2) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame using Haar cascade
        
        Args:
            frame: Input BGR frame
            scale_factor: Scale factor for face detection
            min_neighbors: Minimum neighbors for face detection
            
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with VERY strict parameters to reduce false detections
            # Higher scaleFactor and minNeighbors = fewer false positives
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,  # Increased from 1.1 (less sensitive, fewer false detections)
                minNeighbors=8,   # Increased from 5 (requires more evidence)
                minSize=(60, 60),  # Increased from (15,15) (ignore small faces/noise)
                maxSize=(400, 400),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            return [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []
    
    def extract_face_crop(self, frame: np.ndarray, face_bbox: Tuple[int, int, int, int], padding: int = 20) -> Optional[np.ndarray]:
        """
        Extract face crop from frame
        
        Args:
            frame: Input frame
            face_bbox: Face bounding box (x, y, w, h)
            padding: Padding around face
            
        Returns:
            Face crop image or None
        """
        try:
            x, y, w, h = face_bbox
            
            # Add padding
            x_start = max(0, x - padding)
            y_start = max(0, y - padding)
            x_end = min(frame.shape[1], x + w + padding)
            y_end = min(frame.shape[0], y + h + padding)
            
            # Extract face crop
            face_crop = frame[y_start:y_end, x_start:x_end]
            
            # Resize to standard size
            if face_crop.size > 0:
                face_crop = cv2.resize(face_crop, (150, 150))
                return face_crop
            
            return None
            
        except Exception as e:
            logger.error(f"Face crop extraction failed: {e}")
            return None
    
    def recognize_face(self, face_crop: np.ndarray) -> Tuple[str, float]:
        """
        Recognize face using trained LBPH model
        
        Args:
            face_crop: Face crop image
            
        Returns:
            Tuple of (person_name, confidence_score)
        """
        if not self.is_trained:
            return "unknown", 0.0
        
        try:
            # Convert to grayscale if needed
            if len(face_crop.shape) == 3:
                gray_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            else:
                gray_face = face_crop
            
            # Predict
            label_id, confidence = self.recognizer.predict(gray_face)
            
            # Check if confidence is within threshold
            if confidence <= self.confidence_threshold:
                person_name = self.face_labels.get(label_id, "unknown")
                return person_name, confidence
            else:
                return "unknown", confidence
                
        except Exception as e:
            logger.error(f"Face recognition failed: {e}")
            return "unknown", 0.0
    
    def process_frame_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect and recognize all faces in frame
        
        Args:
            frame: Input frame
            
        Returns:
            List of face detection results
        """
        faces = self.detect_faces(frame)
        results = []
        
        for face_bbox in faces:
            x, y, w, h = face_bbox
            
            # Validate face size - reject tiny or unrealistic detections
            if w < 50 or h < 50:  # Minimum realistic face size
                continue
            if w > 400 or h > 400:  # Maximum realistic face size
                continue
            if w/h > 2 or h/w > 2:  # Reject non-square-ish detections (likely false positives)
                continue
            
            # Extract face crop
            face_crop = self.extract_face_crop(frame, face_bbox)
            if face_crop is None:
                continue
            
            # Recognize face
            person_name, confidence = self.recognize_face(face_crop)
            
            # Determine authorization status
            if person_name == "unknown":
                auth_status = "intruder"
                threat_level = "high"
            else:
                auth_status = "authorized"
                threat_level = "low"
            
            result = {
                'bbox': [x, y, x + w, y + h],  # Convert to (x1, y1, x2, y2)
                'face_bbox': face_bbox,  # Original (x, y, w, h)
                'person_name': person_name,
                'confidence': confidence,
                'authorization_status': auth_status,
                'threat_level': threat_level,
                'face_crop': face_crop
            }
            
            results.append(result)
        
        return results
    
    def train_from_directory(self) -> bool:
        """
        Train LBPH model from known faces directory
        Directory structure: known_faces/person_name/image_files
        
        Returns:
            True if training successful
        """
        try:
            if not self.known_faces_dir.exists():
                logger.warning(f"Known faces directory not found: {self.known_faces_dir}")
                return False
            
            faces = []
            labels = []
            
            # Scan directory for person folders
            for person_dir in self.known_faces_dir.iterdir():
                if not person_dir.is_dir():
                    continue
                
                person_name = person_dir.name
                
                # Skip empty directories or README files
                if person_name.startswith('.') or person_name.lower() == 'readme':
                    continue
                
                # Assign label ID
                if person_name not in self.face_labels.values():
                    self.face_labels[self.label_counter] = person_name
                    current_label = self.label_counter
                    self.label_counter += 1
                else:
                    # Find existing label
                    current_label = next(k for k, v in self.face_labels.items() if v == person_name)
                
                # Process images in person directory
                image_files = []
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                    image_files.extend(person_dir.glob(ext))
                    image_files.extend(person_dir.glob(ext.upper()))
                
                person_face_count = 0
                for image_path in image_files:
                    try:
                        # Load image
                        image = cv2.imread(str(image_path))
                        if image is None:
                            logger.warning(f"Image not loaded: {image_path}")
                            continue
                        
                        # Detect faces in image
                        detected_faces = self.detect_faces(image)
                        if not detected_faces:
                            logger.warning(f"No faces detected in: {image_path}")
                        for face_bbox in detected_faces:
                            # Extract face crop
                            face_crop = self.extract_face_crop(image, face_bbox)
                            if face_crop is None:
                                logger.warning(f"Face crop failed for: {image_path}")
                                continue
                            
                            # Convert to grayscale
                            gray_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
                            
                            faces.append(gray_face)
                            labels.append(current_label)
                            person_face_count += 1
                    
                    except Exception as e:
                        logger.warning(f"Failed to process image {image_path}: {e}")
                        continue
                
                logger.info(f"Loaded {person_face_count} face samples for {person_name}")
            
            if len(faces) == 0:
                logger.warning("No face samples found for training")
                return False
            
            # Train LBPH recognizer
            logger.info(f"Training LBPH model with {len(faces)} face samples")
            self.recognizer.train(faces, np.array(labels))
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            logger.info(f"Training completed. Recognized persons: {list(self.face_labels.values())}")
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False
    
    def add_person(self, person_name: str, face_images: List[np.ndarray]) -> bool:
        """
        Add new person to recognition database
        
        Args:
            person_name: Name of the person
            face_images: List of face crop images
            
        Returns:
            True if successful
        """
        try:
            # Create person directory
            person_dir = self.known_faces_dir / person_name
            person_dir.mkdir(parents=True, exist_ok=True)
            
            # Save face images
            for i, face_image in enumerate(face_images):
                image_path = person_dir / f"{person_name}_{i:03d}.jpg"
                cv2.imwrite(str(image_path), face_image)
            
            # Retrain model
            return self.train_from_directory()
            
        except Exception as e:
            logger.error(f"Failed to add person {person_name}: {e}")
            return False
    
    def save_model(self):
        """Save trained model and labels to disk"""
        try:
            if self.is_trained:
                # Save LBPH model
                self.recognizer.save(str(self.model_path))
                
                # Save labels
                with open(self.labels_path, 'wb') as f:
                    pickle.dump(self.face_labels, f)
                
                logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self) -> bool:
        """
        Load trained model and labels from disk
        
        Returns:
            True if successful
        """
        try:
            if self.model_path.exists() and self.labels_path.exists():
                # Load LBPH model
                self.recognizer.read(str(self.model_path))
                
                # Load labels
                with open(self.labels_path, 'rb') as f:
                    self.face_labels = pickle.load(f)
                
                self.label_counter = max(self.face_labels.keys()) + 1 if self.face_labels else 0
                self.is_trained = True
                
                logger.info(f"Model loaded from {self.model_path}")
                logger.info(f"Known persons: {list(self.face_labels.values())}")
                return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
        
        return False
    
    def get_known_persons(self) -> List[str]:
        """
        Get list of known person names
        
        Returns:
            List of person names
        """
        return list(self.face_labels.values())
    
    def draw_face_results(self, frame: np.ndarray, face_results: List[Dict]) -> np.ndarray:
        """
        Draw face detection and recognition results on frame
        
        Args:
            frame: Input frame
            face_results: List of face detection results
            
        Returns:
            Frame with face annotations
        """
        output_frame = frame.copy()
        
        for result in face_results:
            bbox = result['bbox']
            person_name = result['person_name']
            confidence = result['confidence']
            auth_status = result['authorization_status']
            
            # Color based on authorization
            colors = {
                'authorized': (0, 255, 0),    # Green
                'intruder': (0, 0, 255),      # Red
                'unknown': (0, 255, 255)      # Yellow
            }
            color = colors.get(auth_status, (128, 128, 128))
            
            # Draw face bounding box
            cv2.rectangle(output_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Draw label
            if person_name == "unknown":
                label = f"INTRUDER (conf: {confidence:.1f})"
            else:
                label = f"{person_name} (conf: {confidence:.1f})"
            
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(output_frame,
                         (bbox[0], bbox[1] - label_size[1] - 10),
                         (bbox[0] + label_size[0], bbox[1]),
                         color, -1)
            cv2.putText(output_frame, label,
                       (bbox[0], bbox[1] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return output_frame

if __name__ == "__main__":
    # Test the face recognizer
    recognizer = LBPHFaceRecognizer()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process faces
        face_results = recognizer.process_frame_faces(frame)
        output_frame = recognizer.draw_face_results(frame, face_results)
        
        cv2.imshow('Face Recognition', output_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()