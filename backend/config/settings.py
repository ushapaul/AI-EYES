# Flask Configuration
SECRET_KEY = 'your-secret-key-here'
DEBUG = True

# Camera Configuration
DEFAULT_CAMERA_URL = 'http://192.168.1.100:8080/video'  # IP Webcam URL
CAMERA_RESOLUTION = (640, 480)
FPS = 30

# AI Model Configuration
FACE_RECOGNITION_THRESHOLD = 0.6
SUSPICIOUS_ACTIVITY_THRESHOLD = 0.7
DETECTION_CONFIDENCE = 0.5

# Email Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'your-email@gmail.com'
EMAIL_PASSWORD = 'your-app-password'
ALERT_RECIPIENTS = ['admin@yourdomain.com']

# Paths
KNOWN_FACES_PATH = 'data/known_faces'
ALERTS_PATH = 'data/alerts'
MODELS_PATH = 'app/ai_models'

# System Modes
FARM_MODE = 'farm'
BANK_MODE = 'bank'
DEFAULT_MODE = FARM_MODE

# Database (if using SQLite for logs)
DATABASE_URL = 'sqlite:///surveillance.db'