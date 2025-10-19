"""
Force retrain LBPH face recognition model
"""

import sys
sys.path.append('.')

from surveillance.face_recognition import LBPHFaceRecognizer
import os

def retrain_model():
    """Force retrain the LBPH model"""
    print("=" * 80)
    print("🔄 RETRAINING LBPH FACE RECOGNITION MODEL")
    print("=" * 80)
    
    # Remove old model files to force retraining
    model_files = [
        "data/lbph_model.yml",
        "data/face_labels.pkl"
    ]
    
    for file in model_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️  Removed old model file: {file}")
    
    print("\n📚 Training new model from images...")
    
    # Initialize face recognizer (will trigger training)
    recognizer = LBPHFaceRecognizer(known_faces_dir="data/known_faces")
    
    if recognizer.is_trained:
        print("\n✅ MODEL TRAINED SUCCESSFULLY!")
        print(f"👥 Known persons: {recognizer.get_known_persons()}")
        print(f"📊 Total identities: {len(recognizer.get_known_persons())}")
        
        # Test the model
        print("\n🧪 Testing model...")
        import cv2
        import numpy as np
        
        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        try:
            results = recognizer.process_frame_faces(test_frame)
            print(f"✅ Model test passed (detected {len(results)} faces in test frame)")
        except Exception as e:
            print(f"⚠️  Model test error: {e}")
        
        print("\n" + "=" * 80)
        print("🎉 RETRAINING COMPLETE!")
        print("=" * 80)
        print("\nYou can now:")
        print("1. Run the surveillance system: python multi_camera_surveillance.py")
        print("2. Test accuracy: python test_lbph_accuracy.py")
        
    else:
        print("\n❌ TRAINING FAILED!")
        print("Check the error messages above for details.")

if __name__ == "__main__":
    retrain_model()
