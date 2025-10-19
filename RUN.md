# 🚀 How to Run AI Eyes Security Project

Quick guide to start the AI Eyes surveillance system.

---

## 📋 Prerequisites

- **Python 3.10** (required for MediaPipe compatibility)
- **Node.js** (v16 or higher)
- **MongoDB** (running on localhost:27017)

---

## ⚙️ Configuration Setup (First Time Only)

### Configure Email Addresses

1. Open `.env.local` file in the root directory
2. Update the email addresses for authorized persons:

```env
# Update these with ACTUAL email addresses
VITE_MANAGER_PRAJWAL_EMAIL=prajwal@example.com
VITE_FARMER_BASAVA_EMAIL=basava@example.com
VITE_OWNER_RAJASEKHAR_EMAIL=rajasekhar@example.com
```

3. **Save the file** and restart the frontend for changes to take effect

⚠️ **Important**: These emails will be used for sending alert notifications

---

## ⚡ Quick Start

### 1️⃣ Start Backend (Port 8000)

Open **Terminal 1** (PowerShell):

```powershell
cd backend
.\venv_py310\Scripts\python.exe multi_camera_surveillance.py
```

✅ Backend will start on: **http://localhost:8000**

---

### 2️⃣ Start Frontend (Port 3000)

Open **Terminal 2** (PowerShell):

```powershell
npm run dev
```

✅ Frontend will start on: **http://localhost:3000**

---

## 🎯 Access the Application

1. **Dashboard**: http://localhost:3000/dashboard
2. **Settings**: http://localhost:3000/settings
3. **Backend API**: http://localhost:8000/api

---

## 🧪 Test Webcam Recognition

Open **Terminal 3** (PowerShell):

```powershell
cd backend
.\venv_py310\Scripts\python.exe test_webcam.py
```

**Controls:**
- Press **'q'** to quit
- Press **'s'** to save screenshot

---

## 📹 Add Cameras

### Option 1: Via Dashboard UI
1. Go to http://localhost:3000/dashboard
2. Click **"+ Add Camera"** button
3. Enter camera details:
   - **Name**: e.g., "Front Door"
   - **IP**: e.g., "192.168.1.100"
   - **Port**: e.g., "8080"
   - **Username/Password**: (if required)
4. Select AI mode:
   - **Both**: Face Recognition + Activity Detection
   - **Face Only**: Face Recognition only
   - **Activity Only**: Activity Detection only

### Option 2: Via IP Webcam App
1. Install **IP Webcam** app on Android
2. Start server in app (note the URL shown)
3. Add camera in dashboard with that URL

---

## 🛑 Stop Services

### Stop Backend
Press **CTRL+C** in Terminal 1

### Stop Frontend
Press **CTRL+C** in Terminal 2

---

## 🔧 Troubleshooting

### Backend not connecting?
```powershell
# Check if port 8000 is already in use
netstat -ano | findstr :8000

# Kill process if needed (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Frontend not starting?
```powershell
# Clear node modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
npm run dev
```

### Python environment issues?
```powershell
# Recreate virtual environment
cd backend
py -3.10 -m venv venv_py310
.\venv_py310\Scripts\pip install -r requirements.txt
```

### MongoDB not running?
```powershell
# Start MongoDB service
net start MongoDB
```

---

## 📦 First Time Setup (If Virtual Environment Doesn't Exist)

```powershell
# 1. Create Python 3.10 virtual environment
cd backend
py -3.10 -m venv venv_py310

# 2. Activate virtual environment
.\venv_py310\Scripts\Activate.ps1

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Deactivate (optional)
deactivate

# 5. Install Node.js dependencies
cd ..
npm install
```

---

## 🎨 Project Structure

```
AI eyes/
├── backend/
│   ├── venv_py310/              # Python 3.10 virtual environment
│   ├── multi_camera_surveillance.py  # Main backend server
│   ├── test_webcam.py           # Webcam test script
│   ├── ai_models/
│   │   └── face_recognition/
│   │       ├── mobilenet_face_model_v2_classifier.h5  # Trained model
│   │       └── mobilenet_face_model_v2_data.pkl       # Model data
│   └── data/
│       └── known_faces/         # Training images
│           ├── farmer_Basava/
│           ├── manager_prajwal/
│           └── owner_rajasekhar/
├── src/                         # Frontend React source
├── package.json                 # Node.js dependencies
└── RUN.md                       # This file
```

---

## 🔐 Authorized Persons

The system is trained to recognize these 3 people:
- ✅ **farmer_Basava**
- ✅ **manager_prajwal**
- ✅ **owner_rajasekhar**

Any other person will be detected as **🚨 INTRUDER**

---

## 📊 Model Information

- **Face Recognition**: MobileNetV2 with Unknown class detection
- **Accuracy**: 100% training, 85% validation
- **Confidence Threshold**: 70%
- **Gap Requirement**: 20% between top 2 predictions
- **Activity Detection**: YOLOv9

---

## 💡 Tips

1. **Make sure MongoDB is running** before starting backend
2. **Start backend first**, then frontend
3. **Use good lighting** for better face recognition
4. **Camera should be at eye level** for optimal detection
5. **Clear face visibility** required (no masks/sunglasses)

---

## 📞 Support

For issues or questions:
- Check error messages in terminal
- Review logs in `backend/storage/logs/`
- Ensure all prerequisites are installed

---

**🎉 Happy Monitoring!**
