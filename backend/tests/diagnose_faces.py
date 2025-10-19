"""
Face Detection Diagnostic Tool
Tests face detection on your training images
"""

import cv2
import os
from pathlib import Path

def test_face_detection(image_path):
    """Test face detection on a single image"""
    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        return None, "Failed to load image"
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Load Haar Cascade
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    # Try different detection parameters
    results = {}
    
    # Very sensitive (what we're using now)
    faces1 = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.02,
        minNeighbors=2,
        minSize=(15, 15),
        maxSize=(400, 400)
    )
    results['current_params'] = len(faces1)
    
    # Original sensitive
    faces2 = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30)
    )
    results['moderate_params'] = len(faces2)
    
    # Very aggressive
    faces3 = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.01,
        minNeighbors=1,
        minSize=(10, 10)
    )
    results['aggressive_params'] = len(faces3)
    
    return results, faces1

def diagnose_training_data():
    """Diagnose face detection on training images"""
    known_faces_dir = Path("data/known_faces")
    
    print("=" * 80)
    print("🔍 FACE DETECTION DIAGNOSTIC TOOL")
    print("=" * 80)
    
    if not known_faces_dir.exists():
        print(f"❌ Directory not found: {known_faces_dir}")
        return
    
    total_images = 0
    total_faces_detected = 0
    person_stats = {}
    
    for person_dir in known_faces_dir.iterdir():
        if not person_dir.is_dir() or person_dir.name.startswith('.'):
            continue
        
        person_name = person_dir.name
        print(f"\n👤 Testing: {person_name}")
        print("-" * 80)
        
        image_files = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.jpeg")) + list(person_dir.glob("*.png"))
        
        person_stats[person_name] = {
            'total_images': len(image_files),
            'faces_detected': 0,
            'no_faces': 0,
            'failed_to_load': 0
        }
        
        for i, image_path in enumerate(image_files[:5]):  # Test first 5 images
            results, faces = test_face_detection(image_path)
            total_images += 1
            
            if results is None:
                print(f"  ❌ {image_path.name}: {faces}")
                person_stats[person_name]['failed_to_load'] += 1
            elif results['current_params'] > 0:
                print(f"  ✅ {image_path.name}: {results['current_params']} face(s) detected")
                print(f"     (moderate: {results['moderate_params']}, aggressive: {results['aggressive_params']})")
                person_stats[person_name]['faces_detected'] += 1
                total_faces_detected += 1
            else:
                print(f"  ⚠️  {image_path.name}: NO faces detected")
                print(f"     (moderate: {results['moderate_params']}, aggressive: {results['aggressive_params']})")
                person_stats[person_name]['no_faces'] += 1
        
        if len(image_files) > 5:
            print(f"  ... and {len(image_files) - 5} more images")
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    for person_name, stats in person_stats.items():
        print(f"\n{person_name}:")
        print(f"  Total images: {stats['total_images']}")
        print(f"  Faces detected: {stats['faces_detected']}")
        print(f"  No faces: {stats['no_faces']}")
        print(f"  Failed to load: {stats['failed_to_load']}")
        
        if stats['faces_detected'] > 0:
            success_rate = (stats['faces_detected'] / stats['total_images']) * 100
            print(f"  Success rate: {success_rate:.1f}%")
    
    print(f"\n🎯 Overall: {total_faces_detected}/{total_images} images with detected faces")
    
    if total_faces_detected == 0:
        print("\n⚠️  RECOMMENDATION:")
        print("   Face detection is not working on your images.")
        print("   Possible causes:")
        print("   1. Images are too blurry or low quality")
        print("   2. Faces are not frontal or at extreme angles")
        print("   3. Poor lighting conditions")
        print("   4. Face is too small in the image")
        print("\n   Solutions:")
        print("   ✅ Use clearer, well-lit frontal face photos")
        print("   ✅ Ensure face takes up at least 30% of the image")
        print("   ✅ Upgrade to modern face detector (MTCNN, RetinaFace)")
    elif total_faces_detected < total_images * 0.5:
        print("\n⚠️  LOW DETECTION RATE")
        print("   Consider improving image quality or using a modern face detector")

if __name__ == "__main__":
    diagnose_training_data()
