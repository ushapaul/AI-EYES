#!/usr/bin/env python3
"""
Quick Face Detection Test
Test if OpenCV Haar cascade can detect faces in live camera feed
"""

import sys
import cv2
import time

def test_face_detection():
    """Test basic face detection"""
    print("🔍 Testing Face Detection")
    print("=" * 40)
    
    # Load Haar cascade for face detection
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    
    if face_cascade.empty():
        print("❌ Failed to load face cascade")
        return False
    
    print("✅ Face cascade loaded successfully")
    
    # Connect to camera
    camera_url = "http://192.168.137.254:8080/video"
    print(f"📹 Connecting to camera: {camera_url}")
    
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print("❌ Failed to connect to camera")
        return False
    
    print("✅ Camera connected successfully")
    print("\n🔍 Testing face detection parameters...")
    print("Press 'q' to quit, 's' to save frame")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Test with different parameters
        if frame_count % 10 == 0:  # Test every 10th frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Test with relaxed parameters
            faces_relaxed = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,    # More sensitive
                minNeighbors=3,     # Less strict
                minSize=(30, 30)    # Smaller minimum size
            )
            
            # Test with normal parameters
            faces_normal = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,    # Normal
                minNeighbors=5,     # Normal
                minSize=(50, 50)    # Normal
            )
            
            # Test with strict parameters
            faces_strict = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.5,    # Less sensitive
                minNeighbors=8,     # More strict
                minSize=(80, 80)    # Larger minimum size
            )
            
            print(f"\n📸 Frame {frame_count}:")
            print(f"   Relaxed params: {len(faces_relaxed)} faces")
            print(f"   Normal params:  {len(faces_normal)} faces")
            print(f"   Strict params:  {len(faces_strict)} faces")
            
            # Draw all detected faces with different colors
            for (x, y, w, h) in faces_relaxed:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Green - relaxed
                cv2.putText(frame, "RELAXED", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            for (x, y, w, h) in faces_normal:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)  # Blue - normal
                cv2.putText(frame, "NORMAL", (x, y-25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            for (x, y, w, h) in faces_strict:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)  # Red - strict
                cv2.putText(frame, "STRICT", (x, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Show frame
        display_frame = cv2.resize(frame, (800, 600))
        cv2.imshow('Face Detection Test', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"face_test_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 Frame saved: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    print("🔍👤 Face Detection Parameter Test")
    print("Testing different face detection parameters...")
    print()
    
    test_face_detection()