#!/usr/bin/env python3
"""
Quick SendGrid Test Script
Tests the SendGrid email alert system
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_sendgrid():
    """Test SendGrid email functionality"""
    
    print("🧪 AI Eyes Security - SendGrid Test")
    print("=" * 40)
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import services
        from app.services.email_service import EmailAlertService
        from app.services.alert_manager import AlertManager
        
        print("📧 Testing SendGrid Email Service...")
        
        # Initialize services
        email_service = EmailAlertService()
        alert_manager = AlertManager(socketio=None)
        
        # Check configuration
        config = email_service.get_configuration_status()
        print("\n📊 Configuration Status:")
        for key, value in config.items():
            icon = "✅" if value else "❌"
            print(f"   {icon} {key.replace('_', ' ').title()}: {value}")
        
        if not config['configured']:
            print("\n❌ SendGrid not configured!")
            print("Run: python configure_sendgrid.py")
            return False
        
        # Test basic email functionality
        print("\n🧪 Testing basic email functionality...")
        basic_test = email_service.send_test_alert()
        
        if basic_test:
            print("✅ Basic email test successful!")
        else:
            print("❌ Basic email test failed!")
            return False
        
        # Test alert manager
        print("\n🚨 Testing alert manager with sample alerts...")
        
        # Test person detection alert
        test_persons = [
            {'confidence': 0.85, 'bbox': [100, 100, 200, 300], 'class_name': 'person'}
        ]
        
        person_alert_id = alert_manager.send_person_detection_alert(
            detections=test_persons,
            camera_id="TEST_CAMERA_1"
        )
        
        if person_alert_id:
            print("✅ Person detection alert sent successfully!")
        
        # Test suspicious activity alert  
        suspicious_alert_id = alert_manager.send_suspicious_activity_alert(
            activity_type="unusual_movement",
            camera_id="TEST_CAMERA_1", 
            confidence=0.75
        )
        
        if suspicious_alert_id:
            print("✅ Suspicious activity alert sent successfully!")
        
        # Show alert statistics
        stats = alert_manager.get_alert_stats()
        print(f"\n📊 Alert Statistics:")
        print(f"   • Total Alerts: {stats['total_alerts']}")
        print(f"   • By Type: {stats['alerts_by_type']}")
        print(f"   • By Severity: {stats['alerts_by_severity']}")
        
        print(f"\n🎉 SendGrid integration test completed successfully!")
        print(f"📬 Check your email for test alerts.")
        print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure SendGrid is installed: pip install sendgrid")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"Details: {traceback.format_exc()}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Starting SendGrid Test...")
    print("This will send actual test emails to your configured recipients.")
    print()
    
    confirm = input("Continue with test? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("👋 Test cancelled.")
        return
    
    print()
    success = test_sendgrid()
    
    if success:
        print("\n✅ All tests passed!")
        print("Your SendGrid email alerts are working correctly.")
    else:
        print("\n❌ Some tests failed.")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()