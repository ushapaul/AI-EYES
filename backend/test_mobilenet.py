"""
Test MobileNetV2 Recognition
"""

import sys
from pathlib import Path
import cv2

current_dir = Path(__file__).parent
ai_models_path = current_dir / "ai_models" / "face_recognition"
sys.path.insert(0, str(ai_models_path))

from mobilenet_face_recognition import MobileNetFaceRecognitionSystem

def main():
    print("=" * 70)
    print("TESTING MOBILENETV2 FACE RECOGNITION")
    print("=" * 70)
    
    # Load model
    print("\n1. Loading MobileNetV2 model...")
    recognizer = MobileNetFaceRecognitionSystem()
    model_path = str(ai_models_path / "mobilenet_face_model_v2")
    
    if not recognizer.load_model(model_path):
        print("❌ Failed to load model. Please train first:")
        print("   python train_mobilenet_v2.py")
        return
    
    # Test with known persons
    print("\n2. Testing with images from data/known_faces/...")
    known_faces_dir = current_dir / "data" / "known_faces"
    
    if not known_faces_dir.exists():
        print(f"❌ Known faces directory not found: {known_faces_dir}")
        return
    
    test_count = 0
    success_count = 0
    
    for person_dir in known_faces_dir.iterdir():
        if not person_dir.is_dir():
            continue
        
        person_name = person_dir.name
        
        # Skip Unknown folder for authorized person testing
        if person_name == "Unknown":
            continue
            
        print(f"\n📁 Testing {person_name}:")
        
        # Test first 3 images for better coverage
        image_files = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.png"))
        images = image_files[:3]
        
        if len(images) == 0:
            print(f"   ⚠️ No images found in {person_name}")
            continue
        
        for img_path in images:
            print(f"\n   📸 Testing: {img_path.name}")
            
            frame = cv2.imread(str(img_path))
            if frame is None:
                print(f"   ❌ Could not load image")
                continue
            
            face_names, face_locations, verification_results = recognizer.recognize_faces_in_frame(frame)
            
            test_count += 1
            
            if len(face_names) == 0:
                print(f"   ❌ No faces detected")
                continue
            
            name = face_names[0]
            is_authorized = verification_results[0]
            
            print(f"   Result: {'✅ AUTHORIZED' if is_authorized else '🚨 UNAUTHORIZED'}")
            print(f"   Detected Name: {name}")
            
            # Check if recognition is correct
            if is_authorized and (person_name in name or name in person_name):
                print(f"   ✅ PASSED: Correctly recognized as {person_name}")
                success_count += 1
            else:
                print(f"   ❌ FAILED: Expected {person_name}, got {name} (authorized: {is_authorized})")
    
    # Test with Unknown persons
    print("\n\n📁 Testing Unknown persons:")
    unknown_dir = known_faces_dir / "Unknown"
    if unknown_dir.exists():
        unknown_images = list(unknown_dir.glob("*.jpg"))[:3] + list(unknown_dir.glob("*.png"))[:3]
        
        for img_path in unknown_images[:3]:
            print(f"\n   📸 Testing: {img_path.name}")
            
            frame = cv2.imread(str(img_path))
            if frame is None:
                continue
            
            face_names, face_locations, verification_results = recognizer.recognize_faces_in_frame(frame)
            
            test_count += 1
            
            if len(face_names) == 0:
                print(f"   ❌ No faces detected")
                continue
            
            name = face_names[0]
            is_authorized = verification_results[0]
            
            print(f"   Result: {'✅ AUTHORIZED' if is_authorized else '🚨 UNAUTHORIZED'}")
            print(f"   Detected Name: {name}")
            
            # Unknown should NOT be authorized
            if not is_authorized or name == "Unknown":
                print(f"   ✅ PASSED: Correctly identified as unauthorized/unknown")
                success_count += 1
            else:
                print(f"   ❌ FAILED: Unknown person incorrectly identified as {name}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print(f"Success Rate: {success_count}/{test_count} ({100*success_count/test_count if test_count > 0 else 0:.0f}%)")

if __name__ == "__main__":
    main()
