#!/usr/bin/env python3
"""
Debug Face Recognition System
Test face detection and recognition with live camera feed
"""

import sys
import os
import cv2
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append('.')

from surveillance.face_recognition import LBPHFaceRecognizer

def debug_face_recognition():
    """Debug face recognition with live camera"""
    print("🔍 Debug Face Recognition System")
    print("=" * 50)
    
    # Initialize face recognizer
    face_recognizer = LBPHFaceRecognizer(known_faces_dir="data/known_faces")
    print(f"👤 Face Recognition Status: {'✅ Trained' if face_recognizer.is_trained else '❌ Not trained'}")
    
    if not face_recognizer.is_trained:
        print("⚠️ Training face recognition model...")
        success = face_recognizer.train_from_directory()
        if not success:
            print("❌ Failed to train face recognition model")
            return False
    
    # Connect to camera
    camera_url = "http://192.168.137.254:8080/video"
    print(f"📹 Connecting to camera: {camera_url}")
    
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print("❌ Failed to connect to camera")
        return False
    
    print("✅ Camera connected successfully")
    print("\n🔍 Processing live frames for face detection...")
    print("Press 'q' to quit, 's' to save a test frame")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        frame_count += 1
        
        # Process every 5th frame (same as surveillance system)
        if frame_count % 5 == 0:
            print(f"\n📸 Processing frame {frame_count}")
            
            # Detect faces
            faces = face_recognizer.detect_faces(frame)
            print(f"👤 Detected {len(faces)} faces")
            
            if len(faces) > 0:
                # Process all detected faces
                face_results = face_recognizer.process_frame_faces(frame)
                
                for i, result in enumerate(face_results):
                    print(f"   Face {i+1}:")
                    print(f"     • Name: {result['person_name']}")
                    print(f"     • Confidence: {result['confidence']:.2f}")
                    print(f"     • Status: {result['authorization_status']}")
                    print(f"     • Threat Level: {result['threat_level']}")
                    print(f"     • BBox: {result['bbox']}")
                    
                    # Draw bounding box and label on frame
                    x1, y1, x2, y2 = result['bbox']
                    color = (0, 255, 0) if result['authorization_status'] == 'authorized' else (0, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    label = f"{result['person_name']} ({result['confidence']:.1f})"
                    cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                    
                    # Show authorization status
                    status_text = result['authorization_status'].upper()
                    status_color = (0, 255, 0) if result['authorization_status'] == 'authorized' else (0, 0, 255)
                    cv2.putText(frame, status_text, (x1, y2+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Resize frame for display
        display_frame = cv2.resize(frame, (800, 600))
        cv2.imshow('Face Recognition Debug', display_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save current frame for debugging
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"debug_frame_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 Frame saved: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Face recognition debug session complete")
    return True

if __name__ == "__main__":
    print("🔍👤 AI Eyes Security - Face Recognition Debug")
    print("Testing live face detection and recognition...")
    print()
    
    success = debug_face_recognition()
    
    if success:
        print("\n✅ Face recognition debug completed successfully!")
    else:
        print("\n❌ Face recognition debug failed")