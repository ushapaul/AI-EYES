"""
Force LBPH Model Retraining
Deletes old model and trains fresh with current images
"""

import os
from pathlib import Path
from surveillance.face_recognition import LBPHFaceRecognizer

# Delete old model files
model_path = Path("data/lbph_model.yml")
labels_path = Path("data/face_labels.pkl")

if model_path.exists():
    os.remove(model_path)
    print(f"🗑️  Deleted old model: {model_path}")

if labels_path.exists():
    os.remove(labels_path)
    print(f"🗑️  Deleted old labels: {labels_path}")

print("\n" + "=" * 80)
print("🎯 Starting Fresh LBPH Training")
print("=" * 80)

# Initialize recognizer (will automatically train)
recognizer = LBPHFaceRecognizer(known_faces_dir="data/known_faces")

if recognizer.is_trained:
    print("\n✅ Training successful!")
    print(f"📊 Known persons: {recognizer.get_known_persons()}")
    print(f"💾 Model saved to: {model_path}")
else:
    print("\n❌ Training failed!")
    print("Check the logs above for errors.")
