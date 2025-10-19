"""
Live Webcam Face Recognition Test
Test the trained MobileNetV2 model with your laptop camera
"""

import sys
from pathlib import Path
import cv2
from datetime import datetime

current_dir = Path(__file__).parent
ai_models_path = current_dir / "ai_models" / "face_recognition"
sys.path.insert(0, str(ai_models_path))

from mobilenet_face_recognition import MobileNetFaceRecognitionSystem

def main():
    print("=" * 70)
    print("🎥 LIVE WEBCAM FACE RECOGNITION TEST")
    print("=" * 70)
    
    # Load model
    print("\n📦 Loading MobileNetV2 model...")
    recognizer = MobileNetFaceRecognitionSystem()
    model_path = str(ai_models_path / "mobilenet_face_model_v2")
    
    if not recognizer.load_model(model_path):
        print("❌ Failed to load model. Please train first:")
        print("   python train_mobilenet_v2.py")
        return
    
    print("✅ Model loaded successfully!")
    print(f"✅ Authorized persons: {', '.join(recognizer.authorized_persons)}")
    
    # Initialize webcam
    print("\n🎥 Initializing webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open webcam")
        print("💡 Try:")
        print("   - Check if webcam is connected")
        print("   - Close other apps using the camera")
        print("   - Try camera index 1: cv2.VideoCapture(1)")
        return
    
    # Set smaller resolution for better display
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("✅ Webcam initialized!")
    print("\n" + "=" * 70)
    print("📹 LIVE RECOGNITION STARTED")
    print("=" * 70)
    print("🎯 Instructions:")
    print("   • Position your face in front of the camera")
    print("   • Try different angles and distances")
    print("   • Green box = AUTHORIZED person")
    print("   • Red box = UNAUTHORIZED/Unknown person")
    print("   • Press 'q' to quit")
    print("   • Press 's' to take a screenshot")
    print("=" * 70)
    print()
    
    frame_count = 0
    fps_start_time = datetime.now()
    fps = 0
    
    # Temporal smoothing - remember last N recognitions
    recognition_history = []
    history_size = 5  # Remember last 5 recognitions
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not read frame")
            break
        
        # Process every 2nd frame for better performance
        if frame_count % 2 == 0:
            # Recognize faces
            face_names, face_locations, verification_results = recognizer.recognize_faces_in_frame(frame)
            
            # Apply temporal smoothing for stable recognition
            if face_names:
                # Store current recognition
                recognition_history.append(face_names[0])
                
                # Keep only last N recognitions
                if len(recognition_history) > history_size:
                    recognition_history.pop(0)
                
                # Use majority vote from history for stable display
                if len(recognition_history) >= 3:
                    # Count occurrences
                    name_counts = {}
                    for name in recognition_history:
                        name_counts[name] = name_counts.get(name, 0) + 1
                    
                    # Get most common name
                    stable_name = max(name_counts.items(), key=lambda x: x[1])[0]
                    
                    # Use stable name if it appears at least 2 times in last 5
                    if name_counts[stable_name] >= 2:
                        face_names[0] = stable_name
            
            # Calculate FPS
            if frame_count % 20 == 0:
                fps_end_time = datetime.now()
                time_diff = (fps_end_time - fps_start_time).total_seconds()
                if time_diff > 0:
                    fps = 20 / time_diff
                fps_start_time = fps_end_time
            
            # Log results with timestamp
            if face_names:
                timestamp = datetime.now().strftime("%H:%M:%S")
                for name, result in zip(face_names, verification_results):
                    status = "✅ AUTHORIZED" if result == 1 else "🚨 UNAUTHORIZED"
                    print(f"[{timestamp}] {status}: {name}")
            
            # Draw rectangles and labels
            for (name, (top, right, bottom, left), result) in zip(face_names, face_locations, verification_results):
                # Choose color based on verification result
                if result == 1:
                    color = (0, 255, 0)  # Green for authorized
                    label = f"✓ {name}"
                else:
                    color = (0, 0, 255)  # Red for unauthorized
                    label = f"✗ {name}"
                
                # Draw rectangle around face
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw label background
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                
                # Draw label text
                cv2.putText(frame, label, (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        
        # Add FPS counter
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Add instructions
        cv2.putText(frame, "Press 'q' to quit | 's' for screenshot", (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display the frame
        cv2.imshow('Live Face Recognition - MobileNetV2', frame)
        
        frame_count += 1
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n🛑 Stopping recognition...")
            break
        elif key == ord('s'):
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"📸 Screenshot saved: {filename}")
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 70)
    print("✅ LIVE RECOGNITION TEST COMPLETE")
    print("=" * 70)
    print(f"📊 Total frames processed: {frame_count}")
    print(f"⚡ Average FPS: {fps:.1f}")
    print("Thank you for testing!")

if __name__ == "__main__":
    main()
