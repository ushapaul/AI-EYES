"""
Copy exactly 100 unknown face images from extracted folder to training data
User will place extracted folder in root directory
"""

import os
import shutil
from pathlib import Path
import random

def copy_unknown_faces():
    """Copy 100 random images from extracted folder to Unknown class"""
    
    print("=" * 80)
    print("COPYING 100 UNKNOWN FACES FOR TRAINING")
    print("=" * 80)
    
    # Root directory (AI eyes folder)
    root_dir = Path(__file__).parent.parent.parent
    
    # Destination: backend/data/known_faces/Unknown
    unknown_dir = Path(__file__).parent.parent / "data" / "known_faces" / "Unknown"
    unknown_dir.mkdir(parents=True, exist_ok=True)
    
    # Clear existing Unknown images (keep only authorized persons)
    print("\n🗑️  Clearing old Unknown images...")
    for old_file in unknown_dir.glob("*"):
        old_file.unlink()
    print("✅ Cleared!")
    
    # Find all extracted folders in root directory
    print(f"\n📂 Searching for image folders in: {root_dir}")
    
    possible_folders = []
    for item in root_dir.iterdir():
        if item.is_dir() and item.name not in ['backend', 'src', 'node_modules', '.git', 'data']:
            # Check if folder contains images
            images = list(item.rglob("*.jpg")) + list(item.rglob("*.png")) + list(item.rglob("*.jpeg"))
            if len(images) > 0:
                possible_folders.append((item, len(images)))
    
    if not possible_folders:
        print("\n❌ No image folders found in root directory!")
        print("\n📋 Please:")
        print("1. Extract the human-faces.zip to the root folder (AI eyes/)")
        print("2. Make sure the extracted folder contains .jpg or .png files")
        print("3. Run this script again")
        return False
    
    # Show found folders
    print("\n📊 Found image folders:")
    for folder, count in possible_folders:
        print(f"   {folder.name}: {count} images")
    
    # Use the folder with most images
    source_folder, total_images = max(possible_folders, key=lambda x: x[1])
    print(f"\n✅ Using folder: {source_folder.name} ({total_images} images)")
    
    # Get all images from the folder
    all_images = list(source_folder.rglob("*.jpg")) + list(source_folder.rglob("*.png")) + list(source_folder.rglob("*.jpeg"))
    
    if len(all_images) < 100:
        print(f"\n⚠️  Warning: Only {len(all_images)} images available (need 100)")
        print("Will use all available images...")
        num_to_copy = len(all_images)
    else:
        num_to_copy = 100
    
    # Randomly select 100 images
    random.seed(42)  # Reproducible selection
    selected_images = random.sample(all_images, num_to_copy)
    
    print(f"\n📋 Copying {num_to_copy} random images to Unknown folder...")
    
    # Copy images
    for i, img_path in enumerate(selected_images, 1):
        dest_path = unknown_dir / f"unknown_{i:03d}{img_path.suffix}"
        shutil.copy2(img_path, dest_path)
        
        if i % 20 == 0 or i == num_to_copy:
            print(f"   ✅ Copied {i}/{num_to_copy} images...")
    
    print(f"\n✅ Successfully copied {num_to_copy} images to: {unknown_dir}")
    
    # Show updated training data summary
    print("\n" + "=" * 80)
    print("📊 UPDATED TRAINING DATA SUMMARY:")
    print("=" * 80)
    
    known_faces_dir = Path(__file__).parent.parent / "data" / "known_faces"
    total = 0
    for person_dir in sorted(known_faces_dir.iterdir()):
        if person_dir.is_dir():
            num_images = len(list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.png")) + list(person_dir.glob("*.jpeg")))
            print(f"   {person_dir.name}: {num_images} images")
            total += num_images
    
    print(f"\n   TOTAL: {total} images")
    
    # Calculate balance
    authorized = total - num_to_copy
    unknown_pct = (num_to_copy / total) * 100
    authorized_pct = (authorized / total) * 100
    
    print(f"\n   Balance: {authorized_pct:.1f}% Authorized / {unknown_pct:.1f}% Unknown")
    
    if 40 <= authorized_pct <= 60:
        print("   ✅ EXCELLENT BALANCE! Ready for training!")
    elif 30 <= authorized_pct <= 70:
        print("   ✅ Good balance! Should work well!")
    else:
        print("   ⚠️  Balance might be off - consider adjusting!")
    
    print("\n" + "=" * 80)
    print("✅ READY FOR TRAINING!")
    print("=" * 80)
    print("\nNext step: Run the training script:")
    print("   python train_simple.py")
    print("\nThis will create MobileNetV2 v3 with real unknown faces!")
    
    return True

if __name__ == "__main__":
    success = copy_unknown_faces()
    
    if not success:
        print("\n❌ Failed! Please check the instructions above.")
    else:
        print("\n🎉 Success! You can now train the model!")
