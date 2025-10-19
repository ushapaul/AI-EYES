# AI Eyes - Setup Instructions

## ⚠️ Important: Virtual Environment

**DO NOT commit the virtual environment to Git!**

The virtual environment (`backend/venv_fresh_py310/`) is now properly excluded via `.gitignore`.

## Setting Up on a New Machine

### 1. Clone the Repository

```bash
git clone https://github.com/ushapaul/AI-EYES.git
cd AI-EYES
```

### 2. Create Python Virtual Environment

```bash
cd backend
python -m venv venv_fresh_py310
```

### 3. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv_fresh_py310\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv_fresh_py310\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv_fresh_py310/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Frontend Dependencies

```bash
cd ..
npm install
```

### 6. Run the Application

**Backend:**
```bash
cd backend
python run.py
```

**Frontend:**
```bash
npm run dev
```

## Project Structure

```
AI-EYES/
├── backend/
│   ├── venv_fresh_py310/     # Virtual environment (NOT in Git)
│   ├── app/                   # Flask application
│   ├── surveillance/          # Surveillance modules
│   ├── database/              # Database models
│   └── requirements.txt       # Python dependencies
├── src/                       # React frontend
├── .gitignore                 # Git ignore rules
└── package.json               # Node.js dependencies
```

## Key Files Excluded from Git

- `backend/venv_fresh_py310/` - Virtual environment
- `node_modules/` - Node.js packages
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python files
- `.env` - Environment variables
- `backend/storage/` - Local storage directories
- `*.db`, `*.sqlite` - Database files

## Notes

1. Always activate the virtual environment before running Python commands
2. Never commit large binary files or dependencies to Git
3. Use the provided requirements.txt to recreate the environment
4. For large model files, consider using Git LFS or external storage
