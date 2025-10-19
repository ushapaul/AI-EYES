"""
Download and prepare real human faces for Unknown class training
Uses Kaggle dataset: ashwingupta3012/human-faces
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def download_kaggle_dataset():
    """Download human faces dataset from Kaggle"""
    
    print("=" * 80)
    print("DOWNLOADING REAL HUMAN FACES FOR UNKNOWN CLASS")
    print("=" * 80)
    
    # Check if kaggle is installed
    try:
        import kaggle
        print("✅ Kaggle API found")
    except ImportError:
        print("❌ Kaggle not installed. Installing...")
        os.system("pip install kaggle")
        import kaggle
    
    # Check if Kaggle API credentials exist
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        print("\n❌ Kaggle API credentials not found!")
        print("\nPlease follow these steps:")
        print("1. Go to https://www.kaggle.com/account")
        print("2. Scroll to 'API' section")
        print("3. Click 'Create New Token'")
        print("4. Save the downloaded kaggle.json to:")
        print(f"   {kaggle_dir}")
        print("\nOn Windows, run:")
        print(f"   mkdir {kaggle_dir}")
        print(f"   move Downloads\\kaggle.json {kaggle_json}")
        return False
    
    print(f"✅ Kaggle credentials found at {kaggle_json}")
    
    # Create download directory
    download_dir = Path(__file__).parent.parent / "data" / "unknown_faces_raw"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📥 Downloading dataset to: {download_dir}")
    print("⏳ This may take a few minutes...")
    
    try:
        # Use Kaggle API directly (not command line)
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        print("✅ Kaggle API authenticated")
        print("📥 Downloading dataset...")
        
        # Download and unzip
        api.dataset_download_files(
            'ashwingupta3012/human-faces',
            path=str(download_dir),
            unzip=True
        )
        
        print("\n✅ Download complete!")
        
        # List downloaded files
        files = list(download_dir.rglob("*.jpg")) + list(download_dir.rglob("*.png"))
        print(f"\n📊 Found {len(files)} images")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading dataset: {e}")
        import traceback
        traceback.print_exc()
        return False

def prepare_unknown_faces(num_images=100):
    """Select and prepare images for Unknown class training
    
    IMPORTANT: Using 100 images to maintain class balance!
    - Authorized persons: 83 images total (32 + 21 + 30)
    - Unknown: 100 images (slightly more, but balanced)
    - Ratio: 45% Authorized / 55% Unknown (realistic!)
    
    DO NOT use 7000+ images - it will destroy the model!
    """
    
    print("\n" + "=" * 80)
    print(f"PREPARING {num_images} IMAGES FOR UNKNOWN CLASS")
    print("⚠️  CLASS BALANCE: 83 authorized + 100 unknown = 183 total (BALANCED!)")
    print("=" * 80)
    
    # Paths
    raw_dir = Path(__file__).parent.parent / "data" / "unknown_faces_raw"
    unknown_dir = Path(__file__).parent.parent / "data" / "known_faces" / "Unknown"
    
    # Create Unknown directory
    unknown_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all images
    all_images = list(raw_dir.rglob("*.jpg")) + list(raw_dir.rglob("*.png"))
    
    if len(all_images) == 0:
        print("❌ No images found in raw directory")
        return False
    
    print(f"📊 Found {len(all_images)} total images")
    
    # Select random subset
    import random
    random.seed(42)  # Reproducible selection
    selected_images = random.sample(all_images, min(num_images, len(all_images)))
    
    print(f"✅ Selected {len(selected_images)} images")
    
    # Copy images to Unknown folder
    print("\n📋 Copying images...")
    for i, img_path in enumerate(selected_images):
        dest_path = unknown_dir / f"unknown_{i+1:03d}{img_path.suffix}"
        shutil.copy2(img_path, dest_path)
        if (i + 1) % 20 == 0:
            print(f"   Copied {i+1}/{len(selected_images)} images...")
    
    print(f"\n✅ Successfully copied {len(selected_images)} images to {unknown_dir}")
    
    # Show existing training data
    print("\n📊 UPDATED TRAINING DATA:")
    known_faces_dir = Path(__file__).parent.parent / "data" / "known_faces"
    for person_dir in sorted(known_faces_dir.iterdir()):
        if person_dir.is_dir():
            num_images = len(list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.png")))
            print(f"   {person_dir.name}: {num_images} images")
    
    return True

def main():
    """Main function"""
    
    print("\n🎯 This script will:")
    print("1. Download real human faces from Kaggle")
    print("2. Select 100 diverse faces for Unknown class")
    print("3. Add them to training data")
    print("4. Ready for retraining (run train_simple.py after this)")
    
    # Download dataset
    if not download_kaggle_dataset():
        print("\n❌ Download failed. Please set up Kaggle API first.")
        return
    
    # Prepare Unknown faces
    if not prepare_unknown_faces(num_images=100):
        print("\n❌ Failed to prepare Unknown faces")
        return
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Ready for retraining")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Run: python train_simple.py")
    print("2. This will create MobileNetV2 v3 with REAL unknown faces")
    print("3. Test again with test_webcam.py")
    print("\n🎯 The model will now recognize real intruders correctly!")

if __name__ == "__main__":
    main()
