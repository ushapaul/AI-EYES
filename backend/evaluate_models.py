"""
Model Evaluation Script
Generate confusion matrix and accuracy metrics for both MobileNetV2 and YOLOv9
"""

import os
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score
import json

# Add backend to path
sys.path.append('.')

from ai_models.face_recognition.mobilenet_face_recognition import MobileNetFaceRecognitionSystem
from surveillance.detector import YOLOv9Detector


class ModelEvaluator:
    """Evaluate AI models with confusion matrix and metrics"""
    
    def __init__(self):
        self.results_dir = Path("evaluation_results")
        self.results_dir.mkdir(exist_ok=True)
        
    def evaluate_mobilenet_face_recognition(self, test_data_path="data/validation_images"):
        """
        Evaluate MobileNetV2 face recognition model
        
        Expected folder structure:
        data/validation_images/
            ├── person1/
            │   ├── image1.jpg
            │   ├── image2.jpg
            ├── person2/
            │   ├── image1.jpg
            ├── Unknown/
            │   ├── image1.jpg
        """
        print("\n" + "="*60)
        print("📊 EVALUATING MOBILENETV2 FACE RECOGNITION MODEL")
        print("="*60)
        
        # Load model
        print("\n🔄 Loading MobileNetV2 model...")
        face_recognizer = MobileNetFaceRecognitionSystem()
        
        if not face_recognizer.is_trained:
            print("❌ Model is not trained! Please train the model first.")
            return
        
        print(f"✅ Model loaded successfully")
        print(f"📋 Authorized persons: {', '.join(face_recognizer.get_authorized_persons())}")
        
        # Collect test data
        test_path = Path(test_data_path)
        if not test_path.exists():
            print(f"❌ Test data path not found: {test_data_path}")
            print(f"💡 Please create validation images in: {test_path.absolute()}")
            return
        
        print(f"\n🔍 Scanning test data from: {test_path}")
        
        y_true = []  # True labels
        y_pred = []  # Predicted labels
        
        test_images = []
        
        # Iterate through each person's folder
        for person_folder in test_path.iterdir():
            if not person_folder.is_dir():
                continue
                
            person_name = person_folder.name
            print(f"\n📁 Testing images for: {person_name}")
            
            image_files = list(person_folder.glob("*.jpg")) + list(person_folder.glob("*.png"))
            print(f"   Found {len(image_files)} images")
            
            for img_path in image_files:
                try:
                    # Read image
                    image = cv2.imread(str(img_path))
                    if image is None:
                        print(f"   ⚠️  Could not read: {img_path.name}")
                        continue
                    
                    # Recognize faces
                    face_names, face_locations, verification_results = face_recognizer.recognize_faces_in_frame(image)
                    
                    if len(face_names) > 0:
                        predicted_name = face_names[0]
                        y_true.append(person_name)
                        y_pred.append(predicted_name)
                        
                        match = "✅" if predicted_name == person_name else "❌"
                        print(f"   {match} {img_path.name}: True={person_name}, Pred={predicted_name}")
                    else:
                        print(f"   ⚠️  No face detected in: {img_path.name}")
                        
                except Exception as e:
                    print(f"   ❌ Error processing {img_path.name}: {e}")
        
        if len(y_true) == 0:
            print("\n❌ No test images were successfully processed!")
            return
        
        # Calculate metrics
        print("\n" + "="*60)
        print("📈 FACE RECOGNITION RESULTS")
        print("="*60)
        
        accuracy = accuracy_score(y_true, y_pred)
        print(f"\n🎯 Overall Accuracy: {accuracy*100:.2f}%")
        
        # Get all unique labels
        labels = sorted(list(set(y_true + y_pred)))
        
        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        
        print(f"\n📊 Confusion Matrix:")
        print(f"    Labels: {labels}")
        print(cm)
        
        # Plot confusion matrix
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=labels, yticklabels=labels)
        plt.title('MobileNetV2 Face Recognition - Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        cm_path = self.results_dir / "mobilenet_confusion_matrix.png"
        plt.savefig(cm_path, dpi=300, bbox_inches='tight')
        print(f"\n💾 Confusion matrix saved to: {cm_path}")
        plt.close()
        
        # Classification Report
        print(f"\n📋 Classification Report:")
        report = classification_report(y_true, y_pred, labels=labels, zero_division=0)
        print(report)
        
        # Save detailed report
        report_dict = classification_report(y_true, y_pred, labels=labels, 
                                           output_dict=True, zero_division=0)
        
        # Calculate per-class metrics
        print(f"\n📊 Per-Class Metrics:")
        for label in labels:
            if label in report_dict:
                precision = report_dict[label]['precision']
                recall = report_dict[label]['recall']
                f1 = report_dict[label]['f1-score']
                support = report_dict[label]['support']
                print(f"\n{label}:")
                print(f"  Precision: {precision*100:.2f}%")
                print(f"  Recall:    {recall*100:.2f}%")
                print(f"  F1-Score:  {f1*100:.2f}%")
                print(f"  Support:   {int(support)} images")
        
        # Save results to JSON
        results = {
            'model': 'MobileNetV2',
            'accuracy': float(accuracy),
            'total_samples': len(y_true),
            'labels': labels,
            'confusion_matrix': cm.tolist(),
            'classification_report': report_dict
        }
        
        results_path = self.results_dir / "mobilenet_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {results_path}")
        
        return results
    
    def evaluate_yolov9_detector(self, test_data_path="data/validation_images/yolo_test"):
        """
        Evaluate YOLOv9 object detection model
        
        Expected structure:
        data/validation_images/yolo_test/
            ├── labels.json  # {"image1.jpg": ["person", "knife"], ...}
            ├── image1.jpg
            ├── image2.jpg
        """
        print("\n" + "="*60)
        print("📊 EVALUATING YOLOV9 OBJECT DETECTION MODEL")
        print("="*60)
        
        # Load model
        print("\n🔄 Loading YOLOv9 detector...")
        detector = YOLOv9Detector(conf_threshold=0.4, device='cpu')
        print("✅ Model loaded successfully")
        
        test_path = Path(test_data_path)
        if not test_path.exists():
            print(f"❌ Test data path not found: {test_data_path}")
            print(f"💡 Please create test images and labels.json in: {test_path.absolute()}")
            return
        
        # Load ground truth labels
        labels_file = test_path / "labels.json"
        if not labels_file.exists():
            print(f"❌ labels.json not found in {test_path}")
            print(f"💡 Create a labels.json file with format:")
            print('   {"image1.jpg": ["person", "knife"], "image2.jpg": ["person"]}')
            return
        
        with open(labels_file, 'r') as f:
            ground_truth = json.load(f)
        
        print(f"\n🔍 Found {len(ground_truth)} labeled images")
        
        # Detect objects
        y_true_all = []
        y_pred_all = []
        
        # Classes we're interested in
        target_classes = ['person', 'knife', 'scissors', 'backpack', 'handbag', 'suitcase']
        
        print(f"\n🎯 Target classes: {target_classes}")
        
        for image_name, true_labels in ground_truth.items():
            image_path = test_path / image_name
            
            if not image_path.exists():
                print(f"⚠️  Image not found: {image_name}")
                continue
            
            try:
                # Read image
                frame = cv2.imread(str(image_path))
                if frame is None:
                    print(f"⚠️  Could not read: {image_name}")
                    continue
                
                # Detect objects
                detections = detector.detect(frame)
                
                # Extract detected classes
                pred_labels = [d['class_name'] for d in detections]
                
                # For each target class, check if present
                for cls in target_classes:
                    y_true_all.append(1 if cls in true_labels else 0)
                    y_pred_all.append(1 if cls in pred_labels else 0)
                
                match = "✅" if set(true_labels) == set(pred_labels) else "❌"
                print(f"{match} {image_name}:")
                print(f"   True: {true_labels}")
                print(f"   Pred: {pred_labels}")
                
            except Exception as e:
                print(f"❌ Error processing {image_name}: {e}")
        
        if len(y_true_all) == 0:
            print("\n❌ No test images were successfully processed!")
            return
        
        # Calculate metrics
        print("\n" + "="*60)
        print("📈 YOLOV9 DETECTION RESULTS")
        print("="*60)
        
        accuracy = accuracy_score(y_true_all, y_pred_all)
        precision = precision_score(y_true_all, y_pred_all, zero_division=0)
        recall = recall_score(y_true_all, y_pred_all, zero_division=0)
        f1 = f1_score(y_true_all, y_pred_all, zero_division=0)
        
        print(f"\n🎯 Overall Detection Metrics:")
        print(f"   Accuracy:  {accuracy*100:.2f}%")
        print(f"   Precision: {precision*100:.2f}%")
        print(f"   Recall:    {recall*100:.2f}%")
        print(f"   F1-Score:  {f1*100:.2f}%")
        
        # Confusion matrix (binary: detected vs not detected)
        cm = confusion_matrix(y_true_all, y_pred_all)
        
        print(f"\n📊 Confusion Matrix (Binary Detection):")
        print(f"    TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")
        
        # Plot confusion matrix
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Not Detected', 'Detected'],
                    yticklabels=['Not Present', 'Present'])
        plt.title('YOLOv9 Object Detection - Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        cm_path = self.results_dir / "yolov9_confusion_matrix.png"
        plt.savefig(cm_path, dpi=300, bbox_inches='tight')
        print(f"\n💾 Confusion matrix saved to: {cm_path}")
        plt.close()
        
        # Save results
        results = {
            'model': 'YOLOv9',
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'total_predictions': len(y_true_all),
            'confusion_matrix': cm.tolist()
        }
        
        results_path = self.results_dir / "yolov9_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {results_path}")
        
        return results


def main():
    """Main evaluation function"""
    evaluator = ModelEvaluator()
    
    print("\n" + "="*60)
    print("🤖 AI EYES - MODEL EVALUATION")
    print("="*60)
    
    # Evaluate MobileNetV2
    print("\n1️⃣  Evaluating Face Recognition Model...")
    try:
        mobilenet_results = evaluator.evaluate_mobilenet_face_recognition()
    except Exception as e:
        print(f"❌ Error evaluating MobileNetV2: {e}")
        import traceback
        traceback.print_exc()
    
    # Evaluate YOLOv9
    print("\n2️⃣  Evaluating Object Detection Model...")
    try:
        yolo_results = evaluator.evaluate_yolov9_detector()
    except Exception as e:
        print(f"❌ Error evaluating YOLOv9: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ EVALUATION COMPLETE!")
    print("="*60)
    print(f"\n📁 Results saved in: evaluation_results/")
    print("   - mobilenet_confusion_matrix.png")
    print("   - mobilenet_results.json")
    print("   - yolov9_confusion_matrix.png")
    print("   - yolov9_results.json")


if __name__ == "__main__":
    main()
