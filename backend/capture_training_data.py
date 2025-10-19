#!/usr/bin/env python3
"""
Training Data Capture Tool
Helps capture high-quality training images with variety
"""

import cv2
import os
from datetime import datetime
from pathlib import Path

class TrainingDataCapture:
    def __init__(self):
        self.data_path = Path("data/known_faces")
        
    def capture_person_images(self, person_name, num_images=50):
        """
        Capture training images with guidance for variety
        """
        # Create person folder if not exists
        person_folder = self.data_path / person_name
        person_folder.mkdir(parents=True, exist_ok=True)
        
        # Find next image number
        existing_images = list(person_folder.glob(f"{person_name}_*.jpg"))
        start_num = len(existing_images) + 1
        
        print(f"\n{'='*60}")
        print(f"📸 CAPTURING TRAINING DATA FOR: {person_name}")
        print(f"{'='*60}")
        print(f"Starting from image #{start_num}")
        print(f"Target: {num_images} images")
        print(f"\n🎯 VARIETY CHECKLIST:")
        print("   1. Different angles (front, 45° left, 45° right, profile)")
        print("   2. Different lighting (bright, dim, backlit)")
        print("   3. Different expressions (smile, neutral, serious)")
        print("   4. Different distances (close, medium, far)")
        print("   5. With/without glasses, hat, mask")
        print(f"\n{'='*60}")
        
        # Open camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        captured_count = 0
        image_num = start_num
        
        # Capture instructions
        instructions = [
            "📷 Front face - looking straight",
            "📷 Turn 45° to the LEFT",
            "📷 Turn 45° to the RIGHT", 
            "📷 Side profile (left)",
            "📷 Side profile (right)",
            "📷 Look slightly UP",
            "📷 Look slightly DOWN",
            "😊 SMILE!",
            "😐 Neutral expression",
            "🤔 Serious look",
            "👓 Put on glasses (if available)",
            "🧢 Put on hat/cap (if available)",
            "💡 Move to BRIGHT light area",
            "🌙 Move to DIM light area",
            "📏 Move CLOSER to camera",
            "📍 Move FARTHER from camera"
        ]
        
        instruction_index = 0
        
        print(f"\n🎬 Camera ready!")
        print(f"📌 Current instruction: {instructions[instruction_index]}")
        print(f"\nControls:")
        print("  SPACE = Capture image")
        print("  N = Next instruction")
        print("  Q = Quit")
        
        while captured_count < num_images:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Error reading frame")
                break
            
            # Display instruction on frame
            display_frame = frame.copy()
            
            # Add instruction text
            cv2.putText(display_frame, instructions[instruction_index], 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add progress
            progress_text = f"Captured: {captured_count}/{num_images}"
            cv2.putText(display_frame, progress_text, 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Add controls
            cv2.putText(display_frame, "SPACE=Capture | N=Next | Q=Quit", 
                       (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (200, 200, 200), 1)
            
            cv2.imshow(f"Training Data Capture - {person_name}", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '):  # Space bar - capture
                filename = f"{person_name}_{image_num}.jpg"
                filepath = person_folder / filename
                cv2.imwrite(str(filepath), frame)
                captured_count += 1
                image_num += 1
                print(f"✅ Captured {captured_count}/{num_images}: {filename}")
                
            elif key == ord('n'):  # Next instruction
                instruction_index = (instruction_index + 1) % len(instructions)
                print(f"📌 {instructions[instruction_index]}")
                
            elif key == ord('q'):  # Quit
                print("\n⏹️ Capture stopped by user")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n{'='*60}")
        print(f"✅ CAPTURE COMPLETE!")
        print(f"{'='*60}")
        print(f"📊 Total images captured: {captured_count}")
        print(f"💾 Saved to: {person_folder}")
        print(f"📁 Total images in folder: {len(list(person_folder.glob('*.jpg')))}")
        
    def show_dataset_summary(self):
        """Show current dataset statistics"""
        print(f"\n{'='*60}")
        print("📊 CURRENT DATASET SUMMARY")
        print(f"{'='*60}")
        
        for person_folder in sorted(self.data_path.glob("*")):
            if person_folder.is_dir():
                images = list(person_folder.glob("*.jpg")) + list(person_folder.glob("*.png"))
                count = len(images)
                
                # Status indicator
                if count >= 80:
                    status = "✅ Excellent"
                elif count >= 50:
                    status = "✅ Good"
                elif count >= 30:
                    status = "⚠️ Adequate"
                elif count >= 20:
                    status = "⚠️ Minimum"
                else:
                    status = "❌ Too Few"
                
                print(f"\n{person_folder.name}:")
                print(f"   Images: {count}")
                print(f"   Status: {status}")
                print(f"   Recommendation: {'Add more variety' if count < 80 else 'Good to go!'}")

def main():
    capture = TrainingDataCapture()
    
    # Show current status
    capture.show_dataset_summary()
    
    print(f"\n{'='*60}")
    print("📸 TRAINING DATA CAPTURE TOOL")
    print(f"{'='*60}")
    
    # Get person name
    person_name = input("\nEnter person name (e.g., farmer_Basava, manager_prajwal): ").strip()
    
    if not person_name:
        print("❌ Person name cannot be empty")
        return
    
    # Get number of images to capture
    try:
        num_images = int(input(f"How many images to capture? (recommended: 50): ").strip() or "50")
    except ValueError:
        num_images = 50
    
    # Start capture
    capture.capture_person_images(person_name, num_images)
    
    # Show updated summary
    capture.show_dataset_summary()

if __name__ == "__main__":
    main()
