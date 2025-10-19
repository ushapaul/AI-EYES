"""
Quick script to add sample logs to MongoDB for testing
Run this to populate the Event Logs tab with test data
"""
import sys
import os
from datetime import datetime, timedelta
from random import choice, uniform

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import LogModel

# Initialize log model
log_model = LogModel()

# Sample log data
sample_events = [
    ("Camera system initialized", "system", 0.0),
    ("Face recognition started", "CAM-001", 0.0),
    ("Motion detected", "Front Gate", 0.85),
    ("Authorized person detected - Prajwal", "Main Entrance", 0.94),
    ("Authorized person detected - Basava", "Farm Area", 0.91),
    ("Unknown person detected", "Parking Lot", 0.88),
    ("Alert escalated to Security Team", "system", 0.0),
    ("Alert dismissed - False positive", "CAM-002", 0.0),
    ("Camera stream reconnected", "BITM", 0.0),
    ("Face detection threshold updated", "system", 0.0),
]

sample_actions = [
    "system_start",
    "detection_started",
    "motion_detected",
    "person_recognized",
    "person_recognized",
    "intruder_detected",
    "alert_escalated",
    "alert_dismissed",
    "camera_reconnected",
    "settings_updated",
]

print("🔄 Adding sample logs to MongoDB...")
print("=" * 50)

# Add logs with timestamps going back in time
for i, (event, location, confidence) in enumerate(sample_events):
    # Create timestamps going back in time (most recent first)
    timestamp = datetime.now() - timedelta(minutes=i*15)
    
    try:
        log_model.create_log(
            camera_id=location,
            action=sample_actions[i],
            description=event
        )
        print(f"✅ Added log: {event} ({location})")
    except Exception as e:
        print(f"❌ Error adding log: {e}")

print("\n" + "=" * 50)
print(f"✅ Successfully added {len(sample_events)} sample logs!")
print("\n📋 To view logs:")
print("   1. Go to Dashboard → Event Logs tab")
print("   2. Click Refresh button")
print("\n🗑️  To clear all logs:")
print("   python backend/scripts/clear_logs.py")
