"""
Update existing cameras in MongoDB to add ai_mode field
"""
from database.config import get_database
from pymongo import MongoClient

def update_cameras_ai_mode():
    """Add ai_mode field to all existing cameras (default: 'both')"""
    try:
        db = get_database()
        cameras_collection = db['cameras']
        
        # Get all cameras
        cameras = list(cameras_collection.find())
        print(f"\n📂 Found {len(cameras)} cameras in database")
        
        # Update each camera to add ai_mode if missing
        updated_count = 0
        for camera in cameras:
            camera_id = camera['_id']
            camera_name = camera.get('name', 'Unknown')
            
            # Check if ai_mode already exists
            if 'ai_mode' not in camera:
                result = cameras_collection.update_one(
                    {'_id': camera_id},
                    {'$set': {'ai_mode': 'both'}}  # Default to 'both' (full protection)
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ Updated '{camera_name}': ai_mode = 'both'")
            else:
                print(f"ℹ️  '{camera_name}': ai_mode already set to '{camera['ai_mode']}'")
        
        print(f"\n✅ Updated {updated_count} cameras with ai_mode field")
        print("📋 All cameras now have AI mode configuration")
        
        # Show final camera list with AI modes
        print("\n📋 Camera Configuration:")
        cameras = list(cameras_collection.find())
        for camera in cameras:
            name = camera.get('name', 'Unknown')
            ai_mode = camera.get('ai_mode', 'both')
            location = camera.get('location', 'Unknown')
            
            mode_desc = {
                'both': '🛡️ Full Protection (Face + Activity)',
                'lbph': '👤 Face Recognition Only',
                'yolov9': '⚠️ Activity Detection Only'
            }
            
            print(f"  • {name} ({location})")
            print(f"    {mode_desc.get(ai_mode, ai_mode)}")
        
    except Exception as e:
        print(f"❌ Error updating cameras: {e}")

if __name__ == "__main__":
    update_cameras_ai_mode()
