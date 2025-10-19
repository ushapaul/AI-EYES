# 🔍 AI Eyes Surveillance System

A comprehensive intelligent surveillance system with real-time object detection, person tracking, face recognition, and suspicious activity detection using YOLOv9 and OpenCV.

## ✨ Features

### 🎯 Core Detection Capabilities
- **YOLOv9 Object Detection**: Real-time detection of persons, weapons, bags, and other objects
- **Person Tracking**: Multi-person tracking with unique IDs across video frames
- **LBPH Face Recognition**: Detect and recognize authorized vs unauthorized persons
- **Suspicious Activity Detection**: Advanced behavioral analysis

### 🚨 Activity Detection Types
- **Loitering Detection**: Identify people staying in areas too long
- **Zone Intrusion**: Alert when unauthorized access to restricted areas
- **Weapon Detection**: Real-time weapon and threat identification  
- **Abandoned Object Detection**: Detect unattended bags or objects
- **Unauthorized Person Detection**: Face recognition for access control

### 📧 Alert System
- **Email Notifications**: Instant alerts with activity snapshots
- **Database Logging**: Persistent storage of all security events
- **Real-time Callbacks**: WebSocket support for live dashboard updates
- **Threat Level Assessment**: Automatic risk categorization

### 🌐 API Integration
- **Flask REST API**: Complete web service integration
- **Live Video Streaming**: Real-time camera feed with overlay graphics
- **Zone Management**: Dynamic security zone configuration
- **Face Database Management**: Add/remove authorized persons

## 🏗️ Architecture

```
surveillance/
├── __init__.py                 # Module initialization
├── detector.py                 # YOLOv9 object detection
├── tracker.py                  # Multi-person tracking
├── face_recognition.py         # LBPH face recognition
├── activity_analyzer.py        # Suspicious activity detection
├── surveillance_manager.py     # Main coordinator
├── alert_manager.py            # Email alerts & notifications
└── surveillance_api.py         # Flask API routes
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Run the automated setup
python setup_surveillance.py

# Or install manually
pip install torch torchvision ultralytics opencv-python numpy Pillow Flask Flask-CORS python-dotenv email-validator
```

### 2. Configure Environment
```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
ALERT_EMAIL=alerts@yourdomain.com
```

### 3. Add Known Faces
```bash
# Create directories for authorized persons
mkdir -p data/known_faces/person_name/
# Add face images (JPG/PNG) to each person's folder
```

### 4. Test the System
```bash
# Test individual components
python test_surveillance.py

# Start the Flask backend
python app_simple.py
```

## 📊 API Endpoints

### Surveillance Control
```http
POST /api/surveillance/start
POST /api/surveillance/stop
GET  /api/surveillance/status
GET  /api/surveillance/statistics
```

### Live Monitoring
```http
GET  /api/surveillance/live_frame
GET  /api/surveillance/activities
```

### Configuration
```http
GET    /api/surveillance/detection_zones
POST   /api/surveillance/detection_zones
DELETE /api/surveillance/detection_zones/<zone_id>

GET    /api/surveillance/known_faces
POST   /api/surveillance/known_faces
DELETE /api/surveillance/known_faces/<person_name>
```

## 🎮 Usage Examples

### Basic Surveillance Setup
```python
from surveillance import SurveillanceManager
from surveillance.activity_analyzer import DetectionZone, ActivityType

# Initialize manager
manager = SurveillanceManager(
    camera_id=0,  # Use webcam
    output_dir="storage",
    known_faces_dir="data/known_faces"
)

# Add detection zone
zone = DetectionZone(
    name="Main Entrance",
    points=[(100, 100), (500, 100), (500, 400), (100, 400)],
    zone_type="restricted",
    activity_types=[
        ActivityType.UNAUTHORIZED_PERSON,
        ActivityType.LOITERING,
        ActivityType.WEAPON_DETECTED
    ]
)
manager.add_detection_zone(zone)

# Set up alerts
def on_alert(activity):
    print(f"🚨 ALERT: {activity.activity_type.value}")
    print(f"Threat Level: {activity.threat_level.value}")

manager.set_activity_callback(on_alert)

# Start surveillance
manager.start_surveillance()
```

### Face Recognition Training
```python
from surveillance.face_recognition import LBPHFaceRecognizer

recognizer = LBPHFaceRecognizer("data/known_faces")

# Train from directories
recognizer.train_from_directory()

# Add new person
recognizer.add_known_person("john_doe", "path/to/john_images/")

# Recognize faces in frame
faces = recognizer.detect_faces(frame)
for face in faces:
    name, confidence = recognizer.recognize_face(frame, face)
    print(f"Recognized: {name} (confidence: {confidence})")
```

### Custom Activity Detection
```python
from surveillance.activity_analyzer import SuspiciousActivityAnalyzer, ActivityType

analyzer = SuspiciousActivityAnalyzer()

# Configure detection parameters
analyzer.loitering_time_threshold = 30.0  # 30 seconds
analyzer.zone_entry_threshold = 5        # 5 pixels

# Add custom detection zones
analyzer.add_detection_zone(DetectionZone(
    name="Server Room",
    points=[(200, 150), (600, 150), (600, 450), (200, 450)],
    zone_type="restricted",
    activity_types=[ActivityType.UNAUTHORIZED_PERSON]
))

# Analyze frame
activities = analyzer.analyze_frame(frame, detections, tracks)
```

## ⚙️ Configuration Options

### Detection Settings
```python
# YOLOv9 Detection
CONFIDENCE_THRESHOLD = 0.5      # Detection confidence
NMS_THRESHOLD = 0.4             # Non-maximum suppression
PERSON_CLASS_ID = 0             # COCO person class

# Face Recognition  
FACE_RECOGNITION_THRESHOLD = 100  # LBPH confidence threshold
MIN_FACE_SIZE = (30, 30)         # Minimum face dimensions

# Activity Detection
LOITERING_TIME_THRESHOLD = 30.0   # Seconds before loitering alert
ABANDONED_OBJECT_TIME = 60.0      # Seconds before abandoned object alert
ZONE_ENTRY_BUFFER = 5             # Pixels buffer for zone entry
```

### Alert Configuration
```python
# Email Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_RATE_LIMIT = 60           # Seconds between emails for same activity

# Storage Settings  
MAX_SNAPSHOTS = 1000            # Maximum stored alert images
CLEANUP_INTERVAL = 3600         # Seconds between cleanup runs
```

## 🔧 Troubleshooting

### Common Issues

#### Camera Access Problems
```bash
# Check camera permissions
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Failed')"

# Try different camera IDs
python -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"
```

#### Model Loading Issues
```bash
# Clear model cache
rm -rf ~/.cache/torch/hub/
rm -rf ~/.ultralytics/

# Reinstall ultralytics
pip uninstall ultralytics
pip install ultralytics
```

#### Memory Issues
```bash
# Reduce model size in detector.py
model = YOLO('yolov5n.pt')  # Use nano model instead of yolov9c.pt

# Reduce frame size
manager = SurveillanceManager(
    camera_id=0,
    frame_width=320,    # Reduce from default 640
    frame_height=240    # Reduce from default 480
)
```

### Performance Optimization

#### CPU Optimization
```python
# Use fewer detection classes
detector.target_classes = [0]  # Only detect persons

# Reduce tracking frequency
tracker.update_interval = 3    # Update every 3rd frame

# Optimize face recognition
recognizer.scale_factor = 1.2  # Increase for faster detection
recognizer.min_neighbors = 3   # Reduce for faster detection
```

#### GPU Acceleration
```python
# Enable CUDA if available
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# In detector.py, initialize with device
self.model = YOLO(model_path).to(device)
```

## 📈 Performance Metrics

### Typical Performance
- **Detection FPS**: 15-30 FPS (depending on hardware)
- **Face Recognition**: ~10ms per face
- **Activity Analysis**: ~5ms per frame
- **Memory Usage**: 1-2GB (with YOLOv9)

### Benchmarking
```python
# Get performance statistics
stats = manager.get_statistics()
print(f"Processing FPS: {stats['processing_fps']:.2f}")
print(f"Active Tracks: {stats['active_tracks']}")
print(f"Activities Detected: {stats['activities_detected']}")
```

## 🔒 Security Considerations

### Data Protection
- **Encrypted Storage**: Use encrypted drives for face databases
- **Access Control**: Implement proper API authentication
- **Privacy Compliance**: Follow local privacy laws and regulations
- **Data Retention**: Configure automatic cleanup of old recordings

### Network Security
- **HTTPS Only**: Always use HTTPS in production
- **API Rate Limiting**: Implement rate limiting for API endpoints
- **Input Validation**: Validate all input parameters
- **Audit Logging**: Log all system access and changes

## 🤝 Contributing

### Development Setup
```bash
# Clone the repository
git clone <repository_url>

# Install development dependencies
pip install -r requirements_surveillance.txt
pip install pytest black flake8

# Run tests
python -m pytest tests/

# Format code
black surveillance/
```

### Testing
```bash
# Test individual components
python test_surveillance.py

# Test with mock data
python -m pytest tests/test_surveillance.py

# Performance testing
python benchmark_surveillance.py
```

## 📚 Documentation

- **[Setup Guide](SETUP_GUIDE.md)**: Detailed installation instructions
- **[API Reference](API_REFERENCE.md)**: Complete API documentation
- **[Architecture Guide](ARCHITECTURE.md)**: System design and components
- **[Troubleshooting](TROUBLESHOOTING.md)**: Common issues and solutions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **YOLOv9**: Object detection model by Ultralytics
- **OpenCV**: Computer vision library
- **PyTorch**: Deep learning framework
- **Flask**: Web framework for API

---

**⚠️ Important**: This surveillance system is for educational and legitimate security purposes only. Always comply with local laws and regulations regarding surveillance and privacy.