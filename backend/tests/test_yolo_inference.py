import pytest
from pathlib import Path
import numpy as np


def _find_model_path():
    # Try common locations for the trained model in this repo
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    candidates = [repo_root / "yolov8n.pt", repo_root / "backend" / "yolov8n.pt", Path("yolov8n.pt")]
    for p in candidates:
        if p.exists():
            return p
    pytest.skip("yolov8n.pt not found in repo root or backend/ - skipping YOLO inference test")


def _find_test_image_or_array():
    # Prefer a real validation image in data/validation_images, otherwise return a small white image array
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    imgs_dir = repo_root / "data" / "validation_images"
    if imgs_dir.exists():
        imgs = list(imgs_dir.glob("**/*.jpg")) + list(imgs_dir.glob("**/*.png"))
        if imgs:
            return imgs[0]

    # Fallback: return an in-memory white image as numpy array (HWC, uint8)
    arr = np.full((320, 320, 3), 255, dtype=np.uint8)
    return arr


def test_yolo_model_inference_runs():
    """Load the repo's YOLOv8 model and run a single inference to ensure it doesn't crash.

    This test will be skipped if the `ultralytics` package isn't installed or the model file
    `yolov8n.pt` is not present in the repository.
    """
    ultralytics = pytest.importorskip("ultralytics", reason="ultralytics package is required to run YOLO inference")

    model_path = _find_model_path()
    from ultralytics import YOLO

    # Construct model (this should be fast for the small yolov8n checkpoint)
    model = YOLO(str(model_path))

    img = _find_test_image_or_array()

    # Try the modern predict API, but be tolerant of small differences across ultralytics versions.
    try:
        if isinstance(img, (np.ndarray,)):
            results = model.predict(source=img, imgsz=320, conf=0.25, max_det=20)
        else:
            results = model.predict(source=str(img), imgsz=320, conf=0.25, max_det=20)
    except TypeError:
        # Older API: call model(...) directly
        if isinstance(img, (np.ndarray,)):
            results = model(img, imgsz=320)
        else:
            results = model(str(img), imgsz=320)

    assert results is not None

    # Normalise to a single result object (some versions return a list)
    res0 = results[0] if isinstance(results, (list, tuple)) else results

    # Check that results object is shaped like a detection result. We don't assert a minimum
    # number of detections because a validation image may contain no objects; instead ensure
    # the API returned something we can inspect.
    if hasattr(res0, "boxes"):
        # res0.boxes may be a sequence-like object
        try:
            _ = len(res0.boxes)
        except Exception:
            # Some versions expose .boxes.xyxy as a tensor/array
            if hasattr(res0.boxes, "xyxy"):
                assert getattr(res0.boxes, "xyxy") is not None
    else:
        # Fallback - ensure the result has any attribute that indicates success
        assert hasattr(res0, "masks") or hasattr(res0, "probs") or hasattr(res0, "names")
