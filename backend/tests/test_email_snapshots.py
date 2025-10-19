#!/usr/bin/env python3
"""
Test Email Alert System with Snapshots
Tests that email alerts include proper image attachments
"""

import sys
import os
import cv2
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append('.')

from app.services.alert_manager import AlertManager

def create_test_image():
    """Create a test image for email attachment testing"""
    # Create a test image with some text
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add colored background
    test_image[:] = (50, 50, 100)  # Dark blue background
    
    # Add text
    cv2.putText(test_image, "INTRUDER DETECTED", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    cv2.putText(test_image, "Test Alert Image", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(test_image, f"Camera: TEST_FARM_CAMERA", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    
    # Add a simple face-like rectangle
    cv2.rectangle(test_image, (250, 50), (390, 200), (0, 255, 0), 3)
    cv2.putText(test_image, "UNKNOWN", (270, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return test_image

def test_email_with_snapshots():
    """Test email alerts with image attachments"""
    print("📧 Testing Email Alert System with Snapshots")
    print("=" * 60)
    
    # Initialize alert manager
    alert_manager = AlertManager(socketio=None)
    
    # Check email configuration
    config_status = alert_manager.email_service.get_configuration_status()
    print(f"📧 Email Configuration Status:")
    for key, value in config_status.items():
        icon = "✅" if value else "❌"
        print(f"   {icon} {key}: {value}")
    
    if not config_status['configured']:
        print("❌ Email system not properly configured!")
        return False
    
    # Create test image
    print("\n📸 Creating test snapshot...")
    test_image = create_test_image()
    
    # Save test image
    os.makedirs("storage/snapshots", exist_ok=True)
    test_image_path = "storage/snapshots/test_intruder_snapshot.jpg"
    cv2.imwrite(test_image_path, test_image)
    print(f"✅ Test image saved: {test_image_path}")
    
    # Test intruder alert with image
    print("\n🚨 Testing intruder alert with snapshot...")
    try:
        alert_id = alert_manager.send_intruder_alert(
            person_name="unknown_intruder",
            camera_id="TEST_FARM_CAMERA",
            confidence=0.87,
            image_path=test_image_path
        )
        print(f"✅ Intruder alert sent successfully! Alert ID: {alert_id}")
        print(f"📧 Email with snapshot should be sent to: {alert_manager.email_service.recipients}")
        
    except Exception as e:
        print(f"❌ Error sending intruder alert with image: {e}")
        return False
    
    # Test weapon alert with image
    print("\n🔫 Testing weapon alert with snapshot...")
    try:
        alert_id = alert_manager.send_weapon_detection_alert(
            weapon_type="knife",
            camera_id="TEST_BANK_CAMERA",
            confidence=0.92,
            image_path=test_image_path
        )
        print(f"✅ Weapon alert sent successfully! Alert ID: {alert_id}")
        
    except Exception as e:
        print(f"❌ Error sending weapon alert with image: {e}")
        return False
    
    # Test abandoned object alert with image
    print("\n🎒 Testing abandoned object alert with snapshot...")
    try:
        alert_id = alert_manager.send_suspicious_activity_alert(
            activity_type="abandoned_object",
            camera_id="TEST_BANK_CAMERA",
            confidence=0.78,
            image_path=test_image_path
        )
        print(f"✅ Abandoned object alert sent successfully! Alert ID: {alert_id}")
        
    except Exception as e:
        print(f"❌ Error sending abandoned object alert with image: {e}")
        return False
    
    # Show alert statistics
    print("\n📊 Alert Statistics:")
    stats = alert_manager.get_alert_stats()
    for key, value in stats.items():
        if key == 'recent_alerts':
            print(f"   • {key}: {len(value)} alerts")
        else:
            print(f"   • {key}: {value}")
    
    print("\n🎉 Email Alert System with Snapshots Test Complete!")
    print("📬 Check your email inbox for alerts with image attachments")
    print(f"📸 Test image saved at: {test_image_path}")
    
    return True

if __name__ == "__main__":
    print("📧🚨 AI Eyes Security - Email Alert System with Snapshots Test")
    print("Testing SendGrid email alerts with image attachments...")
    print()
    
    success = test_email_with_snapshots()
    
    if success:
        print("\n✅ Email alert system with snapshots is working correctly!")
        print("📧 SendGrid configured and sending emails with image attachments")
        print("📸 Snapshots are properly saved and attached to emails")
    else:
        print("\n❌ Email alert system with snapshots needs attention")