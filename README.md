# AI-EYES — Simple Run Guide (Easy for kids)

Hello! This guide will help you run the AI-EYES project on a Windows computer. I wrote it so a 10-year-old can follow it. Take your time and copy the commands into PowerShell when asked.

## What is this project?
- AI-EYES watches video (from cameras) and tries to notice faces and people.
- There are two parts: a Python backend (does the brainy work) and a web frontend (the website you open in the browser).

## What you need before we start
- A Windows computer.
- Internet (to download things).
- Python 3.10.1 (we want this exact version so the project works well).
- Node.js and npm (so the website can run).

If you already have Python but it's a different version (like 3.14), that's OK — we'll still create a special Python environment that uses 3.10.1 only for this project.

---

## Step 1 — Open PowerShell in the project folder
1. Open PowerShell.
2. Change to this project folder. If your project is on the Desktop, run (copy-paste this):

```powershell
cd "C:\Users\Lenovo\Desktop\AI eyes"
```

Now you are in the right folder.

## Step 2 — Install Python 3.10.1 (only if you don't have it)
If you're not sure, type:

```powershell
py -3.10 --version
```


# AI-EYES — Run Guide (clean & simple)

This short guide explains how to run the AI-EYES project on Windows (PowerShell). Follow the sections in order. Copy-paste the commands into PowerShell.

Prerequisites
- Windows
- Python 3.10.x (recommended 3.10.1) — we use a virtual environment so system Python won't be changed
- Node.js (LTS) and npm

Quick overview
- Backend (Python): located in `backend/` — runs the API and AI code
- Surveillance process: `backend/multi_camera_surveillance.py` — reads camera(s)
- Frontend (web): run with `npm run dev` from project root

1) Open PowerShell and go to the project folder

```powershell
cd "C:\Users\Lenovo\Desktop\AI eyes"
```

2) Create and activate a Python virtual environment
- Use the `py` launcher if available (recommended):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
py -3.10 -m venv .venv
. .\.venv\Scripts\Activate.ps1
python --version   # should show 3.10.x
```

If `py -3.10` is not available, replace `py -3.10` with the full path to a Python 3.10 executable.

3) Install Python dependencies

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt
```

Note: `backend/requirements.txt` uses loose versions to avoid pin conflicts. If you need exact reproducibility, use `backend/requirements_exact.txt` but be prepared to resolve version conflicts.

4) Install Node dependencies (frontend)

```powershell
npm install
```

5) Start the backend and surveillance processes (two terminals)

- Terminal A — backend (API / web server)

```powershell
cd "C:\Users\Lenovo\Desktop\AI eyes"
(.venv) & .\.venv\Scripts\python.exe backend\app_simple.py
```

- Terminal B — surveillance process

```powershell
cd "C:\Users\Lenovo\Desktop\AI eyes"
(.venv) & .\.venv\Scripts\python.exe backend\multi_camera_surveillance.py
```

Start each in its own PowerShell window so you can see logs and stop them independently (Ctrl+C stops them).

6) Run the frontend (separate terminal)

```powershell
cd "C:\Users\Lenovo\Desktop\AI eyes"
npm run dev
# Open the browser to the address shown (usually http://localhost:5173)
```

Environment variables
- The project can use a `.env` file in the repo root. Copy `.env.example` to `.env` and update values (Mongo URI, API keys, etc.) before starting if required.

Common troubleshooting
- Execution policy errors when activating venv: run the `Set-ExecutionPolicy` command above (it applies only to this PowerShell session).
- Dependency conflicts (protobuf / mediapipe / tensorflow): prefer `backend/requirements.txt` which is looser. If you must use `requirements_exact.txt` and pip fails, read the error and adjust pins or ask for help.
- Missing package errors: install the specific package inside the activated venv, for example:

```powershell
pip install PyJWT
```

- If you already have a prepared venv folder `venv_fresh_py310/`, you can run Python from there explicitly:

```powershell
   ```bash
```

Stopping processes
- Press Ctrl+C in the PowerShell window running the script.

If you want automation
- I can add a PowerShell script to create a `.venv`, install Python deps, and start the backend and surveillance processes together.

That's it — follow the steps in order and you should have the backend, surveillance process, and frontend running.

   cd backend
   pip install -r requirements.txt
   ```

3. **Start the surveillance system**
   ```bash
   python multi_camera_surveillance.py
   ```

4. **Access the dashboard**
   Open your browser to `http://localhost:5002`

## 📁 Project Structure

```
AI-Eyes-on-Security/
├── backend/                    # Backend surveillance system
│   ├── surveillance/           # AI surveillance modules
│   │   ├── detector.py         # YOLOv9 object detection
│   │   ├── face_recognition.py # LBPH face recognition
│   │   ├── activity_analyzer.py # Suspicious activity detection
│   │   ├── surveillance_manager.py # Main coordinator
│   │   └── alert_manager.py    # Alert and notification system
│   ├── app/                    # Flask application
│   ├── config/                 # Configuration files
│   ├── database/               # Database models
│   ├── storage/                # File storage management
│   ├── multi_camera_surveillance.py # Main application
│   ├── live_surveillance_system.py  # Single camera system
│   └── requirements.txt        # Python dependencies
├── src/                        # Frontend React application
├── data/                       # Training data and known faces
└── README.md                   # This file
```

## 🔧 Configuration

### Adding Authorized Faces
1. Create folders in `data/known_faces/`
2. Add 3-5 photos per person:
   ```
   data/known_faces/
   ├── john_doe/
   │   ├── photo1.jpg
   │   ├── photo2.jpg
   │   └── photo3.jpg
   └── jane_smith/
       ├── photo1.jpg
       └── photo2.jpg
   ```

### Camera Setup
The system automatically detects IP cameras on your network. Supported formats:
- `http://IP:PORT/video`
- `http://IP:PORT/stream`

## 🎮 Usage

### Multi-Camera Surveillance
```bash
cd backend
python multi_camera_surveillance.py
```
- Automatically detects all available IP cameras
- Provides unified web dashboard at `http://localhost:5002`
- Start/stop individual cameras or all cameras

### Single Camera Surveillance
```bash
cd backend
python live_surveillance_system.py
```
- Processes single IP camera feed
- Real-time AI detection and activity analysis

## 🚨 Alert Types

- **🔴 CRITICAL**: Weapon detection, unauthorized access
- **🟡 WARNING**: Loitering, abandoned objects, crowd detection
- **🟢 INFO**: Normal monitoring, object detection updates

## 🛠️ API Endpoints

- `GET /api/status` - System status and statistics
- `POST /api/start_all` - Start surveillance on all cameras
- `POST /api/stop_all` - Stop all surveillance
- `GET /video_feed/<camera_name>` - Live video stream

## 📊 System Requirements

- **CPU**: Multi-core processor (Intel i5+ or AMD equivalent)
- **RAM**: 8GB+ recommended for multiple cameras
- **GPU**: CUDA-compatible GPU optional for faster inference
- **Network**: Stable connection to IP cameras
- **Storage**: 10GB+ for logs and snapshots

## 🔒 Security Features

1. **Real-time Object Detection**: YOLOv9 model for accurate detection
2. **Face Recognition**: LBPH algorithm for intruder identification
3. **Activity Monitoring**: Advanced behavioral analysis
4. **Multi-Camera Correlation**: Cross-camera activity tracking
5. **Alert System**: Instant notifications and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Future Enhancements

- [ ] Mobile app integration
- [ ] Cloud storage support
- [ ] Advanced AI models (YOLOv10, Transformer-based)
- [ ] Voice alerts
- [ ] Integration with security systems
- [ ] Advanced analytics dashboard

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review configuration settings

---

**AI Eyes - Keeping watch with artificial intelligence 👁️🤖**
