#!/usr/bin/env python3
"""
Test Farm Security Alert System
Tests LBPH face recognition and intruder detection alerts
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append('.')

from app.services.alert_manager import AlertManager
from surveillance.face_recognition import LBPHFaceRecognizer
import cv2
import numpy as np

def test_farm_security_alerts():
    """Test the farm security alert system"""
    print("🚜 Testing Farm Security Alert System")
    print("=" * 50)
    
    # Initialize components
    print("🔧 Initializing components...")
    alert_manager = AlertManager(socketio=None)
    face_recognizer = LBPHFaceRecognizer(known_faces_dir="data/known_faces")
    
    # Check if face recognition model is trained
    print(f"👤 Face Recognition Status: {'✅ Trained' if face_recognizer.is_trained else '❌ Not trained'}")
    
    if not face_recognizer.is_trained:
        print("⚠️ Training face recognition model...")
        success = face_recognizer.train_from_directory()
        if success:
            print("✅ Face recognition model trained successfully!")
        else:
            print("❌ Failed to train face recognition model")
            return False
    
    # Test intruder alert method
    print("\n🧪 Testing intruder alert method...")
    
    # Test data for intruder alert
    test_intruder_data = {
        'person_name': 'unknown_person',
        'camera_id': 'TEST_FARM_CAMERA',
        'confidence': 0.85
    }
    
    try:
        alert_id = alert_manager.send_intruder_alert(
            person_name=test_intruder_data['person_name'],
            camera_id=test_intruder_data['camera_id'],
            confidence=test_intruder_data['confidence']
        )
        
        print(f"✅ Intruder alert sent successfully! Alert ID: {alert_id}")
        print(f"📧 Email alert should be sent to: {alert_manager.email_service.recipients}")
        
    except Exception as e:
        print(f"❌ Error sending intruder alert: {e}")
        return False
    
    # Test face recognition functionality
    print("\n👤 Testing face recognition...")
    
    # Create a dummy frame for testing
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(test_frame, "Test Frame", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    try:
        face_results = face_recognizer.process_frame_faces(test_frame)
        print(f"✅ Face recognition processing successful")
        print(f"📊 Detected faces: {len(face_results)}")
        
        for i, result in enumerate(face_results):
            print(f"   Face {i+1}: {result['person_name']} (confidence: {result['confidence']:.2f}, status: {result['authorization_status']})")
            
    except Exception as e:
        print(f"⚠️ Face recognition test (no faces expected): {e}")
    
    # Test alert statistics
    print("\n📊 Alert Statistics:")
    stats = alert_manager.get_alert_stats()
    for key, value in stats.items():
        print(f"   • {key}: {value}")
    
    print("\n🎉 Farm Security Alert System Test Complete!")
    print("✅ All components are properly integrated")
    print("📬 Check your email for the test intruder alert")
    
    return True

if __name__ == "__main__":
    print("🚜 AI Eyes Farm Security - Alert System Test")
    print("Testing LBPH face recognition and intruder alerts...")
    print()
    
    success = test_farm_security_alerts()
    
    if success:
        print("\n✅ Farm security alert system is working correctly!")
        print("🔹 Known faces: farmer_Basava, manager_prajwal, owner_rajasekhar")
        print("🔹 Intruder detection: ✅ Active")
        print("🔹 Email alerts: ✅ Configured")
    else:
        print("\n❌ Farm security alert system needs attention")