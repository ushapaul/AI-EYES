"""Evaluate YOLO model on the `data/known_faces` dataset.

This script will:
- load `yolov8n.pt` from repo root or `backend/` if present
- run inference on each image in `data/known_faces/<label>/*.jpg`
- take the top predicted class per image (by highest confidence)
- compute a confusion matrix and per-class precision/recall/F1 and overall accuracy
- save CSV reports and a plotted confusion matrix under `backend/scripts/eval_results/`

Usage: run from repo root with the project's Python interpreter.
Requires: ultralytics, scikit-learn, matplotlib, pandas, numpy
"""
from pathlib import Path
import sys
import json
import numpy as np
from collections import defaultdict, Counter


def find_model_path():
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [repo_root / "yolov8n.pt", repo_root / "backend" / "yolov8n.pt"]
    for p in candidates:
        if p.exists():
            return p
    print("Model file yolov8n.pt not found in repo root or backend/. Place the model at one of those locations.")
    return None


def gather_images(dataset_dir: Path):
    images = []
    labels = []
    for label_dir in sorted(dataset_dir.iterdir()):
        if not label_dir.is_dir():
            continue
        label = label_dir.name
        for img in sorted(label_dir.glob("*.jpg")) + sorted(label_dir.glob("*.png")):
            images.append(img)
            labels.append(label)
    return images, labels


def ensure_packages():
    try:
        import ultralytics
        import sklearn
        import pandas as pd
        import matplotlib.pyplot as plt
    except Exception as e:
        print("Missing required packages. Install with: pip install ultralytics scikit-learn pandas matplotlib")
        raise


def main():
    ensure_packages()
    from ultralytics import YOLO
    from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
    import pandas as pd
    import matplotlib.pyplot as plt

    repo_root = Path(__file__).resolve().parents[2]
    model_path = find_model_path()
    if model_path is None:
        sys.exit(1)

    model = YOLO(str(model_path))

    dataset_dir = repo_root / "data" / "known_faces"
    if not dataset_dir.exists():
        print(f"Dataset directory {dataset_dir} not found")
        sys.exit(1)

    images, true_labels = gather_images(dataset_dir)
    if not images:
        print("No images found under data/known_faces. Exiting.")
        sys.exit(1)

    print(f"Found {len(images)} images across {len(set(true_labels))} classes")

    pred_labels = []
    class_names = None

    for i, img in enumerate(images, 1):
        # run inference
        try:
            results = model.predict(source=str(img), imgsz=320, conf=0.15, max_det=10)
        except TypeError:
            # fallback older API
            results = model(str(img), imgsz=320)

        res0 = results[0] if isinstance(results, (list, tuple)) else results

        # get class mapping
        if class_names is None:
            # model.names is typically a dict mapping idx->name
            class_names = getattr(model, "names", None) or getattr(res0, "names", None)

        # determine top prediction for the image
        pred = "none"
        best_conf = 0.0
        if hasattr(res0, "boxes"):
            # res0.boxes may expose .conf and .cls or be a list
            try:
                boxes = res0.boxes
                # try to get confidences and class indices
                confs = getattr(boxes, "conf", None)
                cls_idx = getattr(boxes, "cls", None)
                if confs is None or cls_idx is None:
                    # try iterating boxes
                    for b in boxes:
                        bconf = getattr(b, "conf", None) or (getattr(b, "confidence", None) or 0)
                        bcls = getattr(b, "cls", None) or getattr(b, "class", None)
                        if bconf and bconf > best_conf and bcls is not None:
                            best_conf = float(bconf)
                            pred = class_names[int(bcls)] if class_names and int(bcls) in class_names else str(bcls)
                else:
                    # confs/cls may be tensors/arrays
                    confs_arr = np.array(confs).ravel()
                    cls_arr = np.array(cls_idx).ravel().astype(int)
                    if len(confs_arr) > 0:
                        idx = int(np.argmax(confs_arr))
                        best_conf = float(confs_arr[idx])
                        pred = class_names[cls_arr[idx]] if class_names and cls_arr[idx] in class_names else str(cls_arr[idx])
            except Exception:
                # last resort
                pass
        else:
            # older result structures may have .boxes.xyxy and .boxes.conf
            if hasattr(res0, "boxes"):
                pred = "unknown"

        if pred is None or pred == "":
            pred = "none"

        pred_labels.append(pred)

        if i % 50 == 0 or i == len(images):
            print(f"Processed {i}/{len(images)} images")

    # Build label sets
    labels_all = sorted(set(true_labels) | set(pred_labels))

    # Map labels to indices for confusion matrix
    label_to_idx = {l: idx for idx, l in enumerate(labels_all)}
    y_true = [label_to_idx[l] for l in true_labels]
    y_pred = [label_to_idx[l] for l in pred_labels]

    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(labels_all))))
    acc = accuracy_score(y_true, y_pred)
    clf_report = classification_report(y_true, y_pred, labels=list(range(len(labels_all))), target_names=labels_all, output_dict=True)

    out_dir = Path(__file__).resolve().parent / "eval_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save confusion matrix CSV
    import pandas as pd
    cm_df = pd.DataFrame(cm, index=labels_all, columns=labels_all)
    cm_df.to_csv(out_dir / "confusion_matrix.csv")

    # Save classification report
    clf_df = pd.DataFrame(clf_report).T
    clf_df.to_csv(out_dir / "classification_report.csv")

    # Save accuracy + summary
    summary = {
        "num_images": len(images),
        "num_classes": len(set(true_labels)),
        "accuracy": float(acc),
    }
    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Plot confusion matrix
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(len(labels_all)), yticks=np.arange(len(labels_all)), xticklabels=labels_all, yticklabels=labels_all, ylabel="True label", xlabel="Predicted label", title=f"Confusion Matrix (acc={acc:.3f})")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    thresh = cm.max() / 2. if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], "d"), ha="center", va="center", color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    fig.savefig(out_dir / "confusion_matrix.png")

    print("Evaluation complete. Results written to:")
    print(str(out_dir))


if __name__ == "__main__":
    main()
