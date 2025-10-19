"""
Ensure all unknown face images are in backend/data/known_faces/Unknown/ as .jpg files (no subfolders)
"""
import os
import shutil
from pathlib import Path

def fix_unknown_folder():
    root = Path(__file__).parent.parent.parent  # AI eyes root
    backend_dir = root / "backend"
    unknown_dir = backend_dir / "data" / "known_faces" / "Unknown"
    unknown_dir.mkdir(parents=True, exist_ok=True)

    # Find all possible unknown images in the workspace
    print(f"Searching for unknown face images in {root} ...")
    found = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        for img in root.rglob(ext):
            if "unknown" in img.name.lower() or img.parent.name.lower() == "unknown":
                found.append(img)

    print(f"Found {len(found)} possible unknown images.")
    if not found:
        print("No unknown images found. Please check manually.")
        return

    # Copy all to Unknown/ as .jpg
    for i, img_path in enumerate(found, 1):
        dest = unknown_dir / f"unknown_{i:03d}.jpg"
        try:
            img = cv2.imread(str(img_path))
            if img is not None:
                cv2.imwrite(str(dest), img)
        except Exception as e:
            print(f"Failed to copy {img_path}: {e}")
    print(f"Copied {len(found)} images to {unknown_dir}")

    # Remove any subfolders in Unknown/
    for item in unknown_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
    print("Cleaned up subfolders in Unknown/")

if __name__ == "__main__":
    import cv2
    fix_unknown_folder()
