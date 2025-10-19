"""
Face Recognition using MobileNetV2 (works without ImageNet issues)
Smaller model perfect for small datasets
"""

import cv2
import numpy as np
import pickle
import os
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import mediapipe as mp

class MobileNetFaceRecognitionSystem:
    def __init__(self):
        print("Loading MobileNetV2 model...")
        
        # Load MobileNetV2 (much smaller than EfficientNetB7)
        self.base_model = MobileNetV2(
            weights='imagenet',  # This WORKS (no TensorFlow bug)
            include_top=False,
            input_shape=(224, 224, 3),
            pooling='avg'
        )
        self.base_model.trainable = False
        
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.7
        )
        
        self.classifier_model = None
        self.label_encoder = None
        self.authorized_persons = []
        
        # Auto-load trained model if it exists
        model_path = Path(__file__).parent / "mobilenet_face_model_v2"
        if model_path.with_suffix('.h5').exists() or (Path(str(model_path) + "_classifier.h5")).exists():
            print("📂 Found trained model, loading...")
            self.load_model(str(model_path))
        else:
            print("⚠️ No trained model found. Please train the model first.")
        
        print("✅ MobileNetV2 model loaded successfully!")
    
    @property
    def is_trained(self):
        """Check if the model is trained and ready to use"""
        return self.classifier_model is not None and self.label_encoder is not None
    
    def get_authorized_persons(self):
        """Get list of authorized person names"""
        return self.authorized_persons.copy()
    
    def extract_face_features(self, face_image):
        """Extract features from a face image"""
        try:
            if face_image.shape[0] < 50 or face_image.shape[1] < 50:
                return None
            
            # Resize
            face_resized = cv2.resize(face_image, (224, 224), interpolation=cv2.INTER_LANCZOS4)
            
            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            
            # Preprocess for MobileNetV2
            face_array = np.expand_dims(face_rgb, axis=0)
            face_preprocessed = preprocess_input(face_array)
            
            # Extract features
            features = self.base_model.predict(face_preprocessed, verbose=0)
            return features.flatten()
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def detect_faces(self, image):
        """Detect faces using MediaPipe"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_image)
        
        face_locations = []
        if results.detections:
            h, w, _ = image.shape
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                top = max(0, y)
                right = min(w, x + width)
                bottom = min(h, y + height)
                left = max(0, x)
                
                face_locations.append((top, right, bottom, left))
        
        return face_locations
    
    def train_with_authorized_faces(self, authorized_faces_path: str):
        """Train the classifier"""
        print("\n=== Training Mode ===")
        print("Loading and processing authorized faces with MobileNetV2...")
        
        all_features = []
        all_labels = []
        
        path = Path(authorized_faces_path)
        
        for person_dir in path.iterdir():
            if not person_dir.is_dir():
                continue
            
            person_name = person_dir.name
            print(f"Processing faces for: {person_name}")
            features_for_person = []
            
            for image_file in person_dir.glob("*.jpg"):
                img = cv2.imread(str(image_file))
                if img is None:
                    continue
                
                face_locations = self.detect_faces(img)
                
                if len(face_locations) > 0:
                    top, right, bottom, left = face_locations[0]
                    face_image = img[top:bottom, left:right]
                    
                    # Original
                    features = self.extract_face_features(face_image)
                    if features is not None:
                        all_features.append(features)
                        all_labels.append(person_name)
                        features_for_person.append(features)
                    
                    # Augmentation: horizontal flip
                    face_flipped = cv2.flip(face_image, 1)
                    features = self.extract_face_features(face_flipped)
                    if features is not None:
                        all_features.append(features)
                        all_labels.append(person_name)
                        features_for_person.append(features)
                    
                    # Augmentation: slight brightness change
                    face_bright = cv2.convertScaleAbs(face_image, alpha=1.2, beta=10)
                    features = self.extract_face_features(face_bright)
                    if features is not None:
                        all_features.append(features)
                        all_labels.append(person_name)
                        features_for_person.append(features)
            
            print(f"  - Total features for {person_name}: {len(features_for_person)}")
        
        if len(all_features) < 10:
            print("❌ Not enough training data!")
            return False
        
        # Convert to arrays
        X = np.array(all_features)
        y = np.array(all_labels)
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        self.authorized_persons = list(self.label_encoder.classes_)
        
        print(f"\nDataset summary:")
        for label in self.authorized_persons:
            count = np.sum(y == label)
            print(f"  {label}: {count} samples")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Build classifier
        num_classes = len(self.authorized_persons)
        feature_dim = X.shape[1]
        
        self.classifier_model = Sequential([
            Dense(256, activation='relu', input_shape=(feature_dim,)),
            Dropout(0.5),
            Dense(128, activation='relu'),
            Dropout(0.3),
            Dense(num_classes, activation='softmax')
        ])
        
        self.classifier_model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print(f"\nTraining classifier with {len(X_train)} training samples and {len(X_val)} validation samples...")
        
        # Train
        history = self.classifier_model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=100,
            batch_size=16,
            callbacks=[
                EarlyStopping(patience=15, restore_best_weights=True),
                ReduceLROnPlateau(patience=5)
            ],
            verbose=1
        )
        
        # Evaluate
        train_loss, train_acc = self.classifier_model.evaluate(X_train, y_train, verbose=0)
        val_loss, val_acc = self.classifier_model.evaluate(X_val, y_val, verbose=0)
        
        print("\nTraining completed!")
        print(f"Training accuracy: {train_acc:.4f}")
        print(f"Validation accuracy: {val_acc:.4f}")
        print(f"Authorized persons: {', '.join(self.authorized_persons)}")
        
        return True
    
    def save_model(self, model_path: str):
        """Save the trained model"""
        self.classifier_model.save(f"{model_path}_classifier.h5")  # type: ignore
        print(f"Classifier model saved to {model_path}_classifier.h5")
        
        with open(f"{model_path}_data.pkl", 'wb') as f:
            pickle.dump({
                'label_encoder': self.label_encoder,
                'authorized_persons': self.authorized_persons
            }, f)
        print(f"Model data saved to {model_path}_data.pkl")
        
        return True
    
    def load_model(self, model_path: str):
        """Load trained model"""
        from tensorflow.keras.models import load_model
        
        try:
            self.classifier_model = load_model(f"{model_path}_classifier.h5")
            print(f"Classifier model loaded from {model_path}_classifier.h5")
            
            with open(f"{model_path}_data.pkl", 'rb') as f:
                data = pickle.load(f)
                self.label_encoder = data['label_encoder']
                self.authorized_persons = data['authorized_persons']
            
            print("Model data loaded successfully!")
            print(f"Authorized persons: {', '.join(self.authorized_persons)}")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def recognize_faces_in_frame(self, frame):
        """Recognize faces in a frame"""
        face_locations = self.detect_faces(frame)
        face_names = []
        verification_results = []
        
        for (top, right, bottom, left) in face_locations:
            face_image = frame[top:bottom, left:right]
            features = self.extract_face_features(face_image)
            
            if features is None:
                face_names.append("Unknown")
                verification_results.append(False)
                continue
            
            features_reshaped = features.reshape(1, -1)
            raw_predictions = self.classifier_model.predict(features_reshaped, verbose=0)[0]  # type: ignore
            
            # CALIBRATION: Penalize Unknown class due to training imbalance
            # Unknown had 100+ samples vs ~30 per known person, causing model bias
            calibrated_predictions = raw_predictions.copy()
            
            # Find Unknown class index
            all_classes = self.label_encoder.classes_  # type: ignore
            unknown_idx = np.where(all_classes == 'Unknown')[0][0]
            
            # AGGRESSIVE PENALTY: Square the Unknown confidence to strongly penalize it
            # This reduces 99% → 98%, 90% → 81%, 80% → 64%, 70% → 49%
            calibrated_predictions[unknown_idx] = calibrated_predictions[unknown_idx] ** 2
            
            # Re-normalize probabilities to sum to 1.0
            calibrated_predictions = calibrated_predictions / np.sum(calibrated_predictions)
            
            predictions = calibrated_predictions
            
            max_prob_index = np.argmax(predictions)
            max_probability = predictions[max_prob_index]
            
            # Get second highest probability to check confidence gap
            sorted_probs = np.sort(predictions)[::-1]
            second_prob = sorted_probs[1] if len(sorted_probs) > 1 else 0
            confidence_gap = max_probability - second_prob
            
            print(f"Debug: RAW Unknown={raw_predictions[unknown_idx]:.3f} → CALIBRATED={predictions[unknown_idx]:.3f}")
            print(f"Debug: max confidence {max_probability:.3f}, 2nd: {second_prob:.3f}, gap: {confidence_gap:.3f}")
            
            predicted_label = self.label_encoder.inverse_transform([max_prob_index])[0]  # type: ignore
            print(f"Debug: Predicted class: {predicted_label}")
            
            # Improved criteria for stable recognition:
            # For authorized persons (not Unknown): need higher confidence
            # For Unknown: can accept lower confidence
            
            if predicted_label == "Unknown":
                # Unknown detection: Accept if confidence >= 85% OR gap >= 60%
                # This prevents false "Unknown" when showing known persons
                if max_probability >= 0.85 or confidence_gap >= 0.60:
                    face_names.append("Unknown")
                    verification_results.append(False)  # Not authorized
                    print(f"🚨 UNAUTHORIZED: Unknown (conf: {max_probability:.3f}, gap: {confidence_gap:.3f})")
                else:
                    # Confidence too low for Unknown - reject as Unknown
                    face_names.append("Unknown")
                    verification_results.append(False)
                    print(f"🚨 REJECTED as Unknown: Low confidence")
            else:
                # Authorized person detection: More lenient thresholds
                # Accept if confidence >= 50% AND gap >= 15%
                if max_probability >= 0.50 and confidence_gap >= 0.15:
                    face_names.append(predicted_label)
                    verification_results.append(True)
                    print(f"✅ AUTHORIZED: {predicted_label} (conf: {max_probability:.3f}, gap: {confidence_gap:.3f})")
                else:
                    # Confidence too low - mark as Unknown
                    print(f"🚨 REJECTED: {predicted_label} - confidence {max_probability:.3f} or gap {confidence_gap:.3f} too low")
                    face_names.append("Unknown")
                    verification_results.append(False)
        
        return face_names, face_locations, verification_results
