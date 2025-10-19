# 🏗️ AI Eyes Security - Clean Project Structure

## 📁 **Root Directory**

```
AI eyes/
├── backend/              # Backend surveillance system
├── src/                  # Frontend React application
├── data/                 # Known faces training data
├── storage/              # Runtime data storage
├── node_modules/         # Node.js dependencies (gitignored)
├── .venv_new/            # Python virtual environment (gitignored)
├── .env.template         # Environment variable template
├── .gitignore            # Git ignore rules
├── index.html            # Frontend entry point
├── package.json          # Node.js dependencies
├── vite.config.ts        # Vite configuration
├── tailwind.config.ts    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
├── LICENSE               # Project license
├── README.md             # Project documentation
└── SETUP_GUIDE.md        # Setup instructions
```

---

## 🐍 **Backend Directory**

```
backend/
├── app/                           # Flask application
│   ├── routes/                    # API endpoints
│   │   ├── camera.py             # Camera management API
│   │   ├── alerts.py             # Alert management API
│   │   └── surveillance_api.py   # Surveillance API
│   ├── services/                  # Business logic
│   │   ├── camera_service.py     # Camera service
│   │   ├── alert_manager.py      # Alert manager
│   │   └── email_service.py      # Email notifications
│   ├── ai_models/                 # AI models
│   │   ├── face_recognition_model.py
│   │   └── suspicious_activity_model.py
│   ├── utils/                     # Utilities
│   │   ├── auth.py               # Authentication
│   │   └── camera_utils.py       # Camera utilities
│   └── models/                    # YOLO model weights
│       ├── yolov9c.pt
│       └── gelan-c.pt
│
├── config/                        # Configuration
│   ├── settings.py               # Application settings
│   └── system_config.json        # System configuration
│
├── database/                      # Database models
│   ├── models.py                 # SQLAlchemy models
│   └── config.py                 # Database configuration
│
├── surveillance/                  # Surveillance modules
│   ├── detector.py               # Object detection
│   ├── tracker.py                # Person tracking
│   ├── face_recognition.py       # Face recognition
│   ├── activity_analyzer.py      # Activity analysis
│   ├── alert_manager.py          # Alert management
│   └── surveillance_manager.py   # Main surveillance manager
│
├── storage/                       # Runtime storage
│   ├── database/                 # JSON persistent storage
│   │   ├── alerts.json
│   │   ├── cameras.json
│   │   └── logs.json
│   ├── snapshots/                # Intruder snapshots
│   ├── recordings/               # Video recordings
│   ├── images/                   # Processed images
│   ├── logs/                     # System logs
│   └── temp/                     # Temporary files
│
├── data/                          # Training data
│   └── known_faces/              # Authorized personnel faces
│       ├── farmer_Basava/        # 36 training images
│       ├── manager_prajwal/      # 21 training images
│       └── owner_rajasekhar/     # 30 training images
│
├── docs/                          # Documentation (cleaned up)
│   ├── ALL_3_PERSONS_PROTECTED.md
│   ├── CAMERA_DASHBOARD_INTEGRATION.md
│   ├── FALSE_POSITIVE_FIX.md
│   ├── FIX_POOR_FRAME_TOLERANCE.md
│   ├── HOW_INTRUDER_DETECTION_WORKS.md
│   ├── MEMORY_SYSTEM_ALL_PERSONS.md
│   ├── SECURITY_FIX_INTRUDER_ALERTS.md
│   ├── THRESHOLD_65_FIX.md
│   └── ... (other documentation)
│
├── tests/                         # Test scripts (cleaned up)
│   ├── test_face_detection.py
│   ├── test_activity_detection.py
│   ├── test_email_snapshots.py
│   ├── test_farm_security.py
│   ├── debug_face_recognition.py
│   └── diagnose_faces.py
│
├── scripts/                       # Utility scripts (cleaned up)
│   ├── configure_sendgrid.py
│   ├── retrain_model.py
│   ├── force_retrain.py
│   └── test_storage.ps1
│
├── multi_camera_surveillance.py   # Main surveillance system (PORT 5002)
├── app_simple.py                  # Simple Flask API (PORT 5000)
├── live_surveillance_system.py    # Live surveillance (legacy)
├── run_live_surveillance.py       # Live surveillance runner (legacy)
├── start_surveillance.bat         # Windows startup script
├── start_surveillance.sh          # Linux startup script
├── requirements.txt               # Python dependencies
├── requirements_surveillance.txt  # Surveillance dependencies
├── .env                           # Environment variables
└── README.md                      # Backend documentation
```

---

## ⚛️ **Frontend Directory**

```
src/
├── pages/                    # React pages
│   ├── dashboard/           # Dashboard page
│   ├── home/                # Home page
│   ├── login/               # Login page
│   ├── profile/             # Profile page
│   ├── settings/            # Settings page
│   ├── surveillance/        # Surveillance page
│   └── NotFound.tsx         # 404 page
│
├── hooks/                   # Custom React hooks
│   ├── useApi.ts           # API hook
│   └── useApiSimple.ts     # Simple API hook
│
├── i18n/                    # Internationalization
│   ├── index.ts
│   └── local/              # Translations
│
├── router/                  # React Router
│   ├── config.tsx          # Route configuration
│   └── index.ts            # Router setup
│
├── App.tsx                  # Main App component
├── main.tsx                 # Entry point
├── index.css                # Global styles
└── vite-env.d.ts           # Vite TypeScript declarations
```

---

## 🗄️ **Data & Storage**

### **Training Data:**
```
data/known_faces/
├── farmer_Basava/        # 36 images
├── manager_prajwal/      # 21 images
└── owner_rajasekhar/     # 30 images
```

### **Runtime Storage:**
```
storage/
├── database/             # JSON persistent storage
├── snapshots/            # Intruder detection snapshots
├── alerts/               # Alert history
├── recordings/           # Video recordings
└── logs/                 # System logs
```

---

## 🚀 **How to Run**

### **Backend (Surveillance System - Port 5002):**
```powershell
cd "C:\Users\prave\OneDrive\Desktop\AI eyes"
.\.venv_new\Scripts\Activate.ps1
cd backend
python multi_camera_surveillance.py
```

### **Backend (Simple API - Port 5000):**
```powershell
cd "C:\Users\prave\OneDrive\Desktop\AI eyes"
.\.venv_new\Scripts\Activate.ps1
cd backend
python app_simple.py
```

### **Frontend (React - Port 3000):**
```powershell
cd "C:\Users\prave\OneDrive\Desktop\AI eyes"
npm run dev
```

---

## 📊 **System Configuration**

### **Face Recognition:**
- **Threshold:** 65 (BALANCED)
- **Confidence Zones:**
  - 0-65: Authorized (excellent to good match)
  - 65-70: Borderline (3-frame grace period)
  - 70+: Intruder (different person)

### **Face Detection:**
- **Method:** Haar Cascade
- **Parameters:**
  - scaleFactor: 1.3
  - minNeighbors: 8
  - minSize: 60x60 pixels

### **Grace Periods:**
- **Face Not Visible:** 10 frames (~5 seconds)
- **Poor Frame Quality:** 3 frames (~1.5 seconds)

### **Alert System:**
- **Email:** SendGrid
- **Cooldown:** 5 minutes
- **Attachments:** Snapshot images

---

## ✅ **Clean Structure Benefits**

1. ✅ **Organized Documentation:** All .md files in `backend/docs/`
2. ✅ **Organized Tests:** All test scripts in `backend/tests/`
3. ✅ **Organized Scripts:** All utility scripts in `backend/scripts/`
4. ✅ **Removed Clutter:** Deleted temporary files, old venv, cache
5. ✅ **Clear Separation:** Backend, frontend, data clearly separated
6. ✅ **Easy Navigation:** Logical folder structure
7. ✅ **Production Ready:** Clean, professional project layout

---

**Date:** October 17, 2025  
**Status:** ✅ Clean and organized  
**Next Steps:** Continue development with clean structure
