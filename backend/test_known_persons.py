"""
Quick test to check if known persons are recognized
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from surveillance.efficientnet_face_recognition import EfficientNetFaceRecognizer
import cv2

print("="*70)
print("TESTING KNOWN PERSON RECOGNITION")
print("="*70)

# Initialize recognizer
print("\n1. Loading EfficientNet model...")
recognizer = EfficientNetFaceRecognizer()

if not recognizer.is_trained:
    print("❌ Model not loaded!")
    exit(1)

print(f"✅ Model loaded")
print(f"✅ Authorized persons: {', '.join(recognizer.get_authorized_persons())}")

# Test with sample images from known_faces
print("\n2. Testing with images from data/known_faces/...")

import glob
from pathlib import Path

known_faces_dir = Path("data/known_faces")
if not known_faces_dir.exists():
    known_faces_dir = Path("../data/known_faces")

if known_faces_dir.exists():
    for person_folder in known_faces_dir.iterdir():
        if person_folder.is_dir():
            print(f"\n📁 Testing {person_folder.name}:")
            
            # Get first image
            images = list(person_folder.glob("*.jpg")) + list(person_folder.glob("*.png"))
            if len(images) == 0:
                print("   ⚠️ No images found")
                continue
            
            for img_path in images[:2]:  # Test first 2 images
                print(f"\n   📸 Testing: {img_path.name}")
                
                # Load image
                frame = cv2.imread(str(img_path))
                if frame is None:
                    print("   ❌ Could not load image")
                    continue
                
                # Recognize
                results = recognizer.recognize_faces(frame)
                
                if len(results) == 0:
                    print("   ❌ No faces detected")
                else:
                    for result in results:
                        name = result['name']
                        conf = result['confidence']
                        auth = "✅ AUTHORIZED" if result['is_authorized'] else "🚨 INTRUDER"
                        
                        print(f"   Result: {auth}")
                        print(f"   Name: {name}")
                        print(f"   Confidence: {conf:.1%}")
                        
                        if result['is_authorized']:
                            print(f"   ✅ SUCCESS: {person_folder.name} recognized!")
                        else:
                            print(f"   ❌ FAILED: Should recognize {person_folder.name}")
else:
    print("⚠️ No known_faces directory found")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
