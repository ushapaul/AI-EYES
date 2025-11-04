# Model Evaluation Guide

## 📊 Generate Confusion Matrix & Accuracy for Both Models

This script evaluates both **MobileNetV2 (Face Recognition)** and **YOLOv9 (Object Detection)** models.

## 🚀 Quick Start

```bash
cd backend
python evaluate_models.py
```

## 📁 Setup Validation Data

### For MobileNetV2 Face Recognition:

Create validation images in: `data/validation_images/`

**Folder Structure:**
```
data/validation_images/
├── person1_name/
│   ├── test1.jpg
│   ├── test2.jpg
│   └── test3.jpg
├── person2_name/
│   ├── test1.jpg
│   └── test2.jpg
├── Unknown/
│   ├── stranger1.jpg
│   ├── stranger2.jpg
│   └── stranger3.jpg
```

**Tips:**
- Use 5-10 test images per person
- Include images NOT used in training
- Add Unknown folder with faces of people NOT in the system
- Use clear, well-lit images

### For YOLOv9 Object Detection:

Create test images in: `data/validation_images/yolo_test/`

**Folder Structure:**
```
data/validation_images/yolo_test/
├── labels.json
├── test_image1.jpg
├── test_image2.jpg
└── test_image3.jpg
```

**labels.json format:**
```json
{
  "test_image1.jpg": ["person", "knife"],
  "test_image2.jpg": ["person", "person"],
  "test_image3.jpg": ["person", "backpack"],
  "test_image4.jpg": []
}
```

**Target Classes:**
- `person` - Human detection
- `knife` - Knife/weapon
- `scissors` - Scissors
- `backpack` - Backpack
- `handbag` - Handbag
- `suitcase` - Suitcase

## 📈 Output Files

After running, you'll get:

### In `evaluation_results/` folder:

1. **mobilenet_confusion_matrix.png** - Face recognition confusion matrix
2. **mobilenet_results.json** - Detailed metrics (accuracy, precision, recall, F1)
3. **yolov9_confusion_matrix.png** - Object detection confusion matrix  
4. **yolov9_results.json** - Detection metrics

## 📊 Metrics Explained

### Accuracy
Overall correctness: (TP + TN) / Total

### Precision
When model predicts positive, how often is it correct: TP / (TP + FP)

### Recall (Sensitivity)
How many actual positives were found: TP / (TP + FN)

### F1-Score
Balance between precision and recall: 2 * (Precision * Recall) / (Precision + Recall)

### Confusion Matrix
- **TP (True Positive)**: Correctly identified
- **TN (True Negative)**: Correctly rejected
- **FP (False Positive)**: Incorrectly identified
- **FN (False Negative)**: Missed detection

## 🎯 Good Accuracy Targets

- **Face Recognition**: 95%+ accuracy
- **Object Detection**: 80%+ accuracy (depends on image quality)

## 💡 Improving Accuracy

### For Face Recognition:
1. Add more training images per person (30-50 images)
2. Use varied lighting conditions
3. Include different angles and expressions
4. Retrain model after adding new data

### For Object Detection:
1. Use higher resolution images
2. Ensure good lighting
3. Avoid occlusions
4. Test with clear, unobstructed objects

## 🔧 Troubleshooting

**"Model is not trained"**
- Run `python train_mobilenet_v2.py` first

**"No test images found"**
- Check folder structure matches the format above
- Verify image file extensions (.jpg, .png)

**"labels.json not found"**
- Create the labels.json file in yolo_test folder
- Use correct JSON format

## 📞 Need Help?

Check that:
1. Models are trained (`ai_models/face_recognition/mobilenet_face_model_v2_classifier.h5` exists)
2. Test images are in correct folders
3. Images are readable (.jpg or .png format)
4. File paths are correct
