"""
Improved MobileNetV2 Training with Unknown Person Detection
Adds negative examples (random faces) to help detect intruders
"""

import sys
from pathlib import Path
import cv2
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import mediapipe as mp

def main():
    print("=" * 80)
    print("TRAINING MOBILENETV2 WITH UNKNOWN PERSON DETECTION")
    print("=" * 80)
    print()
    
    # Initialize MobileNetV2
    print("1. Loading MobileNetV2 base model...")
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3),
        pooling='avg'
    )
    base_model.trainable = False
    print("✅ MobileNetV2 loaded")
    
    # Initialize MediaPipe
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=0.7
    )
    
    def extract_features(face_image):
        """Extract features from face"""
        try:
            if face_image.shape[0] < 50 or face_image.shape[1] < 50:
                return None
            
            face_resized = cv2.resize(face_image, (224, 224), interpolation=cv2.INTER_LANCZOS4)
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            face_array = np.expand_dims(face_rgb, axis=0)
            face_preprocessed = preprocess_input(face_array)
            features = base_model.predict(face_preprocessed, verbose=0)
            return features.flatten()
        except:
            return None
    
    def detect_faces(image):
        """Detect faces using MediaPipe"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_image)
        
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
    
    # Load known faces
    print("\n2. Loading authorized persons...")
    current_dir = Path(__file__).parent
    known_faces_dir = current_dir / "data" / "known_faces"
    
    # Verify path exists
    if not known_faces_dir.exists():
        print(f"❌ ERROR: Known faces directory not found: {known_faces_dir}")
        print(f"   Current dir: {current_dir}")
        return
    
    all_features = []
    all_labels = []
    
    for person_dir in known_faces_dir.iterdir():
        if not person_dir.is_dir():
            continue
        
        person_name = person_dir.name
        
        # Skip Unknown folder in this loop (process it separately)
        if person_name == "Unknown":
            continue
            
        print(f"   Processing: {person_name}")
        count = 0
        
        # Process both JPG and PNG files
        image_files = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.png")) + list(person_dir.glob("*.jpeg"))
        
        if len(image_files) == 0:
            print(f"      ⚠️ No images found in {person_name}")
            continue
        
        for img_file in image_files:
            img = cv2.imread(str(img_file))
            if img is None:
                continue
            
            face_locations = detect_faces(img)
            
            if len(face_locations) > 0:
                top, right, bottom, left = face_locations[0]
                face_image = img[top:bottom, left:right]
                
                # Original
                features = extract_features(face_image)
                if features is not None:
                    all_features.append(features)
                    all_labels.append(person_name)
                    count += 1
                
                # Augmentation: flip
                face_flipped = cv2.flip(face_image, 1)
                features = extract_features(face_flipped)
                if features is not None:
                    all_features.append(features)
                    all_labels.append(person_name)
                    count += 1
                
                # Augmentation: brightness
                face_bright = cv2.convertScaleAbs(face_image, alpha=1.2, beta=10)
                features = extract_features(face_bright)
                if features is not None:
                    all_features.append(features)
                    all_labels.append(person_name)
                    count += 1
        
        print(f"      ✅ {count} samples")
    
    print(f"\n✅ Total authorized samples: {len(all_features)}")
    
    if len(all_features) == 0:
        print("❌ ERROR: No training data loaded!")
        print("   Check if images exist in data/known_faces/ folders")
        return
    
    # No synthetic unknowns! Use real unknown faces from data/known_faces/Unknown
    print("\n3. Adding 'Unknown' class (real unknown faces)...")
    unknown_dir = known_faces_dir / "Unknown"
    unknown_count = 0
    if unknown_dir.exists() and unknown_dir.is_dir():
        # Process both JPG and PNG files
        unknown_files = list(unknown_dir.glob("*.jpg")) + list(unknown_dir.glob("*.png")) + list(unknown_dir.glob("*.jpeg"))
        print(f"   Found {len(unknown_files)} unknown images")
        
        for img_file in unknown_files:
            img = cv2.imread(str(img_file))
            if img is None:
                continue
            face_locations = detect_faces(img)
            if len(face_locations) > 0:
                top, right, bottom, left = face_locations[0]
                face_image = img[top:bottom, left:right]
                # Original
                features = extract_features(face_image)
                if features is not None:
                    all_features.append(features)
                    all_labels.append("Unknown")
                    unknown_count += 1
                # Augmentation: flip
                face_flipped = cv2.flip(face_image, 1)
                features = extract_features(face_flipped)
                if features is not None:
                    all_features.append(features)
                    all_labels.append("Unknown")
                    unknown_count += 1
                # Augmentation: brightness
                face_bright = cv2.convertScaleAbs(face_image, alpha=1.2, beta=10)
                features = extract_features(face_bright)
                if features is not None:
                    all_features.append(features)
                    all_labels.append("Unknown")
                    unknown_count += 1
        print(f"   ✅ Added {unknown_count} real unknown samples")
    else:
        print("   ⚠️  No real unknown faces found in data/known_faces/Unknown!")
        print("   ⚠️  Model will be trained WITHOUT unknown class detection")
    
    # Verify we have enough data
    if len(all_features) < 20:
        print(f"\n❌ ERROR: Insufficient training data ({len(all_features)} samples)")
        print("   Need at least 20 samples total for training")
        return
    
    # Convert to arrays
    X = np.array(all_features)
    y = np.array(all_labels)
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"\n4. Dataset summary:")
    for label in label_encoder.classes_:
        count = np.sum(y == label)
        print(f"   {label}: {count} samples")
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Build classifier with 4 classes (3 persons + Unknown)
    num_classes = len(label_encoder.classes_)
    feature_dim = X.shape[1]
    
    classifier_model = Sequential([
        Dense(256, activation='relu', input_shape=(feature_dim,)),
        Dropout(0.5),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])
    
    classifier_model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"\n5. Training classifier ({len(X_train)} training, {len(X_val)} validation)...")
    
    history = classifier_model.fit(
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
    train_loss, train_acc = classifier_model.evaluate(X_train, y_train, verbose=0)
    val_loss, val_acc = classifier_model.evaluate(X_val, y_val, verbose=0)
    
    print("\n✅ Training completed!")
    print(f"   Training accuracy: {train_acc:.4f}")
    print(f"   Validation accuracy: {val_acc:.4f}")
    
    # Save model
    ai_models_path = current_dir / "ai_models" / "face_recognition"
    output_path = str(ai_models_path / "mobilenet_face_model_v2")
    
    classifier_model.save(f"{output_path}_classifier.h5")
    print(f"\n💾 Classifier saved: {output_path}_classifier.h5")
    
    with open(f"{output_path}_data.pkl", 'wb') as f:
        pickle.dump({
            'label_encoder': label_encoder,
            'authorized_persons': [p for p in label_encoder.classes_ if p != "Unknown"]
        }, f)
    print(f"💾 Data saved: {output_path}_data.pkl")
    
    print("\n" + "=" * 80)
    print("✅ TRAINING COMPLETE!")
    print("=" * 80)
    print(f"Classes: {', '.join(label_encoder.classes_)}")
    print(f"Authorized persons: {', '.join([p for p in label_encoder.classes_ if p != 'Unknown'])}")
    print(f"\n📊 Final Statistics:")
    print(f"   Total training samples: {len(X_train)}")
    print(f"   Total validation samples: {len(X_val)}")
    print(f"   Training accuracy: {train_acc*100:.2f}%")
    print(f"   Validation accuracy: {val_acc*100:.2f}%")
    print(f"\n🎯 Model Performance:")
    if val_acc >= 0.95:
        print("   ✅ Excellent - Ready for production!")
    elif val_acc >= 0.90:
        print("   ✅ Very Good - Suitable for use")
    elif val_acc >= 0.85:
        print("   ⚠️  Good - May need more training data")
    elif val_acc >= 0.80:
        print("   ⚠️  Fair - Consider adding more diverse images")
    else:
        print("   ❌ Poor - Add more training data with variety")
    print(f"\n💾 Model saved to: {ai_models_path}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Test model: python test_mobilenet.py")
    print(f"   2. Run surveillance: python multi_camera_surveillance.py")

if __name__ == "__main__":
    main()
