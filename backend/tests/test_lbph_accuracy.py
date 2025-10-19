#!/usr/bin/env python3
"""
LBPH Face Recognition Accuracy Testing Tool
Tests accuracy of face recognition for known faces in the AI Eyes Security System
"""

import cv2
import numpy as np
import os
import glob
from surveillance.face_recognition import LBPHFaceRecognizer
import time
from collections import defaultdict
import json

class LBPHAccuracyTester:
    def __init__(self):
        self.face_recognizer = LBPHFaceRecognizer()
        self.results = {
            'total_tests': 0,
            'correct_recognitions': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'per_person_accuracy': {},
            'confidence_stats': {},
            'performance_metrics': {}
        }
        
    def test_known_faces_accuracy(self):
        """Test accuracy with all known face images"""
        print("🧪 Testing LBPH Face Recognition Accuracy")
        print("=" * 60)
        
        known_faces_dir = "data/known_faces"
        if not os.path.exists(known_faces_dir):
            print(f"❌ Known faces directory not found: {known_faces_dir}")
            return
            
        print(f"📁 Testing faces from: {known_faces_dir}")
        print(f"👤 Face recognizer trained: {self.face_recognizer.is_trained}")
        
        if not self.face_recognizer.is_trained:
            print("❌ Face recognizer not trained! Train first.")
            return
            
        # Test each known person
        for person_name in os.listdir(known_faces_dir):
            person_dir = os.path.join(known_faces_dir, person_name)
            if not os.path.isdir(person_dir):
                continue
                
            print(f"\n🔍 Testing: {person_name}")
            print("-" * 40)
            
            # Initialize person stats
            self.results['per_person_accuracy'][person_name] = {
                'total_images': 0,
                'correct_recognitions': 0,
                'false_negatives': 0,
                'accuracy_percentage': 0,
                'avg_confidence': 0,
                'confidence_range': [float('inf'), 0]
            }
            
            # Test all images for this person
            image_files = glob.glob(os.path.join(person_dir, "*.jpg")) + \
                         glob.glob(os.path.join(person_dir, "*.png")) + \
                         glob.glob(os.path.join(person_dir, "*.jpeg"))
            
            person_confidences = []
            
            for image_path in image_files:
                result = self._test_single_image(image_path, person_name)
                if result:
                    person_confidences.append(result['confidence'])
                    
            # Calculate person-specific stats
            person_stats = self.results['per_person_accuracy'][person_name]
            if person_stats['total_images'] > 0:
                person_stats['accuracy_percentage'] = (
                    person_stats['correct_recognitions'] / person_stats['total_images'] * 100
                )
                
            if person_confidences:
                person_stats['avg_confidence'] = np.mean(person_confidences)
                person_stats['confidence_range'] = [min(person_confidences), max(person_confidences)]
                
            print(f"   📊 Accuracy: {person_stats['accuracy_percentage']:.1f}%")
            print(f"   📈 Avg Confidence: {person_stats['avg_confidence']:.2f}")
            print(f"   📉 Confidence Range: {person_stats['confidence_range'][0]:.2f} - {person_stats['confidence_range'][1]:.2f}")
            
        self._calculate_overall_accuracy()
        self._print_detailed_results()
        
    def _test_single_image(self, image_path, expected_person):
        """Test recognition accuracy on a single image"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print(f"   ❌ Could not load: {os.path.basename(image_path)}")
                return None
                
            start_time = time.time()
            
            # Detect faces
            faces = self.face_recognizer.detect_faces(image)
            if len(faces) == 0:
                print(f"   ❌ No faces detected: {os.path.basename(image_path)}")
                self.results['per_person_accuracy'][expected_person]['false_negatives'] += 1
                self.results['false_negatives'] += 1
                self.results['total_tests'] += 1
                self.results['per_person_accuracy'][expected_person]['total_images'] += 1
                return None
                
            # Use the largest face detected
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            
            # Extract face crop
            face_crop = self.face_recognizer.extract_face_crop(image, largest_face)
            if face_crop is None:
                print(f"   ❌ Could not extract face: {os.path.basename(image_path)}")
                return None
                
            # Recognize face
            recognized_name, confidence = self.face_recognizer.recognize_face(face_crop)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self.results['total_tests'] += 1
            self.results['per_person_accuracy'][expected_person]['total_images'] += 1
            
            if recognized_name == expected_person:
                self.results['correct_recognitions'] += 1
                self.results['per_person_accuracy'][expected_person]['correct_recognitions'] += 1
                status = "✅ CORRECT"
            elif recognized_name == "unknown":
                self.results['false_negatives'] += 1
                self.results['per_person_accuracy'][expected_person]['false_negatives'] += 1
                status = "❌ FALSE NEGATIVE (unknown)"
            else:
                self.results['false_positives'] += 1
                status = f"❌ FALSE POSITIVE ({recognized_name})"
                
            print(f"   {status} | {os.path.basename(image_path)} | Confidence: {confidence:.2f} | Time: {processing_time*1000:.1f}ms")
            
            return {
                'recognized_name': recognized_name,
                'confidence': confidence,
                'processing_time': processing_time,
                'status': status
            }
            
        except Exception as e:
            print(f"   ❌ Error processing {os.path.basename(image_path)}: {e}")
            return None
            
    def _calculate_overall_accuracy(self):
        """Calculate overall system accuracy"""
        if self.results['total_tests'] > 0:
            overall_accuracy = (self.results['correct_recognitions'] / self.results['total_tests']) * 100
            
            self.results['performance_metrics'] = {
                'overall_accuracy': overall_accuracy,
                'precision': self._calculate_precision(),
                'recall': self._calculate_recall(),
                'f1_score': self._calculate_f1_score()
            }
            
    def _calculate_precision(self):
        """Calculate precision: TP / (TP + FP)"""
        tp = self.results['correct_recognitions']
        fp = self.results['false_positives']
        return (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
        
    def _calculate_recall(self):
        """Calculate recall: TP / (TP + FN)"""
        tp = self.results['correct_recognitions']
        fn = self.results['false_negatives']
        return (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
        
    def _calculate_f1_score(self):
        """Calculate F1 score: 2 * (precision * recall) / (precision + recall)"""
        precision = self._calculate_precision()
        recall = self._calculate_recall()
        return (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
    def _print_detailed_results(self):
        """Print comprehensive accuracy results"""
        print("\n" + "=" * 60)
        print("📊 LBPH FACE RECOGNITION ACCURACY REPORT")
        print("=" * 60)
        
        metrics = self.results['performance_metrics']
        
        print(f"🎯 Overall Accuracy: {metrics['overall_accuracy']:.2f}%")
        print(f"🎯 Precision: {metrics['precision']:.2f}%")
        print(f"🎯 Recall: {metrics['recall']:.2f}%")
        print(f"🎯 F1 Score: {metrics['f1_score']:.2f}%")
        
        print(f"\n📈 Test Results:")
        print(f"   Total Tests: {self.results['total_tests']}")
        print(f"   Correct Recognitions: {self.results['correct_recognitions']}")
        print(f"   False Positives: {self.results['false_positives']}")
        print(f"   False Negatives: {self.results['false_negatives']}")
        
        print(f"\n👥 Per-Person Accuracy:")
        for person, stats in self.results['per_person_accuracy'].items():
            print(f"   {person}:")
            print(f"      Accuracy: {stats['accuracy_percentage']:.1f}%")
            print(f"      Images Tested: {stats['total_images']}")
            print(f"      Avg Confidence: {stats['avg_confidence']:.2f}")
            print(f"      Confidence Range: {stats['confidence_range'][0]:.2f} - {stats['confidence_range'][1]:.2f}")
            
        # Performance recommendations
        self._print_recommendations()
        
    def _print_recommendations(self):
        """Print recommendations based on accuracy results"""
        print(f"\n💡 RECOMMENDATIONS:")
        
        overall_accuracy = self.results['performance_metrics']['overall_accuracy']
        
        if overall_accuracy >= 95:
            print("   ✅ Excellent accuracy! System is production-ready.")
        elif overall_accuracy >= 85:
            print("   ✅ Good accuracy. Consider adding more training images for improvement.")
        elif overall_accuracy >= 70:
            print("   ⚠️  Moderate accuracy. Add more diverse training images.")
        else:
            print("   ❌ Low accuracy. Consider:")
            print("      - Adding more training images per person")
            print("      - Using higher quality images")
            print("      - Adjusting face detection parameters")
            print("      - Consider switching to a different recognition algorithm")
            
        # Check individual person performance
        for person, stats in self.results['per_person_accuracy'].items():
            if stats['accuracy_percentage'] < 80:
                print(f"   ⚠️  {person}: Low accuracy ({stats['accuracy_percentage']:.1f}%) - add more training images")
                
    def test_confidence_thresholds(self):
        """Test different confidence thresholds to optimize accuracy"""
        print("\n🔧 Testing Confidence Thresholds...")
        
        thresholds = [50, 60, 70, 80, 90, 100, 110, 120]
        
        for threshold in thresholds:
            # This would require modifying the recognizer to use different thresholds
            print(f"Threshold {threshold}: Testing...")
            
    def save_results(self, filename="lbph_accuracy_report.json"):
        """Save test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Run LBPH accuracy tests"""
    print("🤖 AI Eyes Security - LBPH Face Recognition Accuracy Test")
    print("=" * 60)
    
    tester = LBPHAccuracyTester()
    
    # Test known faces accuracy
    tester.test_known_faces_accuracy()
    
    # Save results
    tester.save_results()
    
    print(f"\n✅ Accuracy testing complete!")

if __name__ == "__main__":
    main()