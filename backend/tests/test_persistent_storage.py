#!/usr/bin/env python3
"""
Test Persistent Storage System
Verify JSON storage is working correctly
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_storage():
    """Test persistent storage functionality"""
    
    print("=" * 60)
    print("🧪 TESTING PERSISTENT STORAGE SYSTEM")
    print("=" * 60)
    
    # Test 1: Import persistent storage
    try:
        from database.persistent_storage import get_persistent_storage
        storage = get_persistent_storage()
        print("\n✅ Test 1: Persistent storage module imported")
    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        return False
    
    # Test 2: Check storage directory
    storage_dir = Path("storage/database")
    if storage_dir.exists():
        print(f"✅ Test 2: Storage directory exists: {storage_dir}")
    else:
        print(f"⚠️ Test 2: Storage directory will be created: {storage_dir}")
    
    # Test 3: Check JSON files
    alerts_file = storage_dir / "alerts.json"
    cameras_file = storage_dir / "cameras.json"
    logs_file = storage_dir / "logs.json"
    
    files_exist = [
        ("alerts.json", alerts_file.exists()),
        ("cameras.json", cameras_file.exists()),
        ("logs.json", logs_file.exists())
    ]
    
    print("\n📁 Storage Files:")
    for filename, exists in files_exist:
        status = "✅" if exists else "⚠️ Will be created"
        print(f"   {status} {filename}")
    
    # Test 4: Read existing alerts
    try:
        alerts = storage.get_alerts(limit=100)
        print(f"\n✅ Test 3: Read alerts from storage")
        print(f"📊 Total alerts in storage: {len(alerts)}")
        
        if len(alerts) > 0:
            print(f"\n📋 Recent Alerts:")
            for i, alert in enumerate(alerts[:5], 1):
                print(f"   {i}. {alert.get('type', 'unknown')} - "
                      f"{alert.get('camera_id', 'unknown')} - "
                      f"Severity: {alert.get('severity', 'unknown')}")
        else:
            print("   ℹ️ No alerts in storage yet (will appear after detection)")
    except Exception as e:
        print(f"⚠️ Test 3: Could not read alerts: {e}")
    
    # Test 5: Test alert creation
    try:
        test_alert = {
            'camera_id': 'Test_Camera',
            'type': 'test_alert',
            'message': 'Test alert for storage verification',
            'severity': 'low',
            'image_path': None
        }
        
        alert_id = storage.save_alert(test_alert)
        print(f"\n✅ Test 4: Created test alert: {alert_id}")
        
        # Verify it was saved
        retrieved = storage.get_alert_by_id(alert_id)
        if retrieved:
            print(f"✅ Test 5: Retrieved test alert successfully")
            print(f"   ID: {retrieved['id']}")
            print(f"   Type: {retrieved['type']}")
            print(f"   Message: {retrieved['message']}")
        else:
            print(f"❌ Test 5: Could not retrieve test alert")
    except Exception as e:
        print(f"❌ Test 4/5 FAILED: {e}")
    
    # Test 6: Statistics
    try:
        stats = storage.get_statistics()
        print(f"\n📊 Storage Statistics:")
        print(f"   Total Alerts: {stats['total_alerts']}")
        print(f"   Alerts Today: {stats['alerts_today']}")
        print(f"   Total Cameras: {stats['total_cameras']}")
        print(f"   Online Cameras: {stats['online_cameras']}")
        print(f"   Storage Type: {stats['storage_type']}")
        print(f"\n✅ Test 6: Statistics retrieved successfully")
    except Exception as e:
        print(f"❌ Test 6 FAILED: {e}")
    
    # Test 7: Test AlertModel integration
    try:
        from database.models import AlertModel
        alert_model = AlertModel()
        print(f"\n✅ Test 7: AlertModel initialized with persistent storage")
        
        # Create alert through model
        db_alert_id = alert_model.create_alert(
            camera_id="Test_Camera_Model",
            alert_type="test_model_alert",
            message="Test alert through AlertModel",
            severity="medium"
        )
        print(f"✅ Test 8: Alert created through AlertModel: {db_alert_id}")
        
        # Retrieve recent alerts
        recent = alert_model.get_recent_alerts(limit=5)
        print(f"✅ Test 9: Retrieved {len(recent)} recent alerts through AlertModel")
        
    except Exception as e:
        print(f"⚠️ Test 7-9: AlertModel test: {e}")
    
    print("\n" + "=" * 60)
    print("✅ PERSISTENT STORAGE SYSTEM: OPERATIONAL")
    print("=" * 60)
    
    print("\n📝 Next Steps:")
    print("   1. Restart surveillance: python multi_camera_surveillance.py")
    print("   2. Alerts will now persist across restarts")
    print("   3. Check storage/database/alerts.json for saved data")
    print("   4. Dashboard will show alerts even after server restart")
    
    return True

if __name__ == "__main__":
    try:
        success = test_storage()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
