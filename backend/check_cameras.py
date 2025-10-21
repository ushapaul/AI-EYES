from database.models import camera_model

cameras = camera_model.find_all()
print(f"Found {len(cameras)} cameras in MongoDB")
for c in cameras:
    print(f"  - {c['name']} at {c['location']} ({c['url']})")
