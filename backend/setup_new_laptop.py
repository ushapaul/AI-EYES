#!/usr/bin/env python3
"""
AI Eyes Security System - New Laptop/Computer Setup Script
Automates the setup process for deploying the system on a new machine
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

class SetupManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.os_type = platform.system()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)
        
    def print_step(self, step_num, text):
        """Print formatted step"""
        print(f"\n[Step {step_num}] {text}")
        
    def run_command(self, command, description):
        """Run a shell command and handle errors"""
        print(f"   Running: {description}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                print(f"   ✅ {description} - Success")
                return True
            else:
                print(f"   ❌ {description} - Failed")
                print(f"   Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ {description} - Error: {e}")
            return False
            
    def check_python_version(self):
        """Check if Python version is compatible"""
        self.print_step(1, "Checking Python Version")
        print(f"   Python version: {self.python_version}")
        
        major, minor = sys.version_info.major, sys.version_info.minor
        if major == 3 and minor >= 10:
            print(f"   ✅ Python {major}.{minor} is compatible")
            return True
        else:
            print(f"   ❌ Python {major}.{minor} is not compatible")
            print(f"   Required: Python 3.10 or higher")
            return False
            
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        self.print_step(2, "Creating Virtual Environment")
        
        venv_path = self.project_root / "venv_fresh_py310"
        
        if venv_path.exists():
            print(f"   ⚠️ Virtual environment already exists: {venv_path}")
            response = input("   Do you want to recreate it? (y/n): ").lower()
            if response == 'y':
                print(f"   Removing old virtual environment...")
                import shutil
                shutil.rmtree(venv_path)
            else:
                print(f"   ✅ Using existing virtual environment")
                return True
        
        # Create venv
        if self.os_type == "Windows":
            command = f"python -m venv venv_fresh_py310"
        else:
            command = f"python3 -m venv venv_fresh_py310"
            
        return self.run_command(command, "Creating virtual environment")
        
    def install_requirements(self):
        """Install Python dependencies"""
        self.print_step(3, "Installing Python Dependencies")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print(f"   ❌ requirements.txt not found!")
            return False
            
        # Determine pip command based on OS
        if self.os_type == "Windows":
            pip_cmd = str(self.project_root / "venv_fresh_py310" / "Scripts" / "pip.exe")
        else:
            pip_cmd = str(self.project_root / "venv_fresh_py310" / "bin" / "pip")
            
        # Upgrade pip first
        self.run_command(f'"{pip_cmd}" install --upgrade pip', "Upgrading pip")
        
        # Install requirements
        return self.run_command(
            f'"{pip_cmd}" install -r requirements.txt',
            "Installing dependencies (this may take 5-10 minutes)"
        )
        
    def create_env_file(self):
        """Create .env file from template"""
        self.print_step(4, "Creating Environment Configuration")
        
        env_file = self.project_root / ".env"
        env_template = self.project_root / ".env.template"
        
        if env_file.exists():
            print(f"   ⚠️ .env file already exists")
            response = input("   Do you want to overwrite it? (y/n): ").lower()
            if response != 'y':
                print(f"   ✅ Keeping existing .env file")
                return True
        
        # Create default .env content
        env_content = """# Backend Environment Configuration
# SendGrid Email Alert Configuration

# SendGrid API Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=your_email@example.com
SENDGRID_FROM_NAME=AI Eyes Security System

# Alert Recipients (comma-separated email addresses)
ALERT_RECIPIENTS=your_email@example.com

# Email Alerts Configuration
ENABLE_EMAIL_ALERTS=true

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=ai_eyes_security

# System Configuration
DEBUG=True
SECRET_KEY=ai-eyes-security-2025
"""
        
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            print(f"   ✅ Created .env file")
            print(f"   ⚠️ IMPORTANT: Edit .env file with your actual credentials!")
            return True
        except Exception as e:
            print(f"   ❌ Failed to create .env file: {e}")
            return False
            
    def setup_mongodb(self):
        """Guide for MongoDB setup"""
        self.print_step(5, "MongoDB Setup")
        
        print(f"   MongoDB is required for storing alerts and camera data")
        print(f"\n   Option 1: Install MongoDB Locally")
        print(f"   - Download from: https://www.mongodb.com/try/download/community")
        print(f"   - Install and start MongoDB service")
        print(f"\n   Option 2: Use MongoDB Atlas (Cloud)")
        print(f"   - Sign up at: https://www.mongodb.com/atlas")
        print(f"   - Create free cluster")
        print(f"   - Update MONGODB_URI in .env file")
        print(f"\n   To test MongoDB connection:")
        print(f"   python mongodb_setup.py")
        
        return True
        
    def test_system(self):
        """Test if system is working"""
        self.print_step(6, "Testing System")
        
        print(f"\n   Testing imports...")
        
        # Determine python command based on OS
        if self.os_type == "Windows":
            python_cmd = str(self.project_root / "venv_fresh_py310" / "Scripts" / "python.exe")
        else:
            python_cmd = str(self.project_root / "venv_fresh_py310" / "bin" / "python")
            
        # Test basic imports
        test_cmd = f'"{python_cmd}" -c "import cv2; import tensorflow; import flask; print(\'✅ All core libraries imported successfully\')"'
        
        result = self.run_command(test_cmd, "Testing core libraries")
        
        if result:
            print(f"\n   ✅ System test passed!")
            print(f"\n   Testing MobileNetV2 model...")
            
            # Test model loading
            model_test = f'"{python_cmd}" -c "from ai_models.face_recognition.mobilenet_face_recognition import MobileNetFaceRecognitionSystem; m = MobileNetFaceRecognitionSystem(); print(\'Model loaded:\', m.is_trained)"'
            self.run_command(model_test, "Testing face recognition model")
        
        return result
        
    def print_next_steps(self):
        """Print next steps for user"""
        self.print_header("🎉 SETUP COMPLETE!")
        
        print(f"\n✅ Your AI Eyes Security System is ready!")
        print(f"\n📝 Next Steps:")
        print(f"\n1. Configure Environment Variables:")
        print(f"   • Edit .env file in backend directory")
        print(f"   • Add your SendGrid API key")
        print(f"   • Add your email addresses")
        
        print(f"\n2. Setup MongoDB:")
        print(f"   • Install MongoDB locally OR use MongoDB Atlas")
        print(f"   • Test connection: python mongodb_setup.py")
        
        print(f"\n3. Train Face Recognition Model:")
        print(f"   • Add face images to data/known_faces/")
        print(f"   • Run: python capture_training_data.py")
        print(f"   • Run: python train_mobilenet_v2.py")
        
        print(f"\n4. Test System:")
        print(f"   • Test email: python test_sendgrid_email.py")
        print(f"   • Test model: python test_known_persons.py")
        print(f"   • Test webcam: python test_webcam_live.py")
        
        print(f"\n5. Run Surveillance System:")
        if self.os_type == "Windows":
            print(f"   • Activate venv: .\\venv_fresh_py310\\Scripts\\Activate.ps1")
        else:
            print(f"   • Activate venv: source venv_fresh_py310/bin/activate")
        print(f"   • Run system: python multi_camera_surveillance.py")
        print(f"   • Access dashboard: http://localhost:8001")
        
        print(f"\n📖 Documentation:")
        print(f"   • Setup Guide: SETUP_GUIDE.md")
        print(f"   • How to Run: RUN.md")
        print(f"   • Model Status: CURRENT_MODEL_STATUS.md")
        
        print(f"\n" + "=" * 70)
        
    def run_setup(self):
        """Run complete setup process"""
        self.print_header("🚀 AI Eyes Security System - New Laptop Setup")
        
        print(f"\nThis script will:")
        print(f"  1. Check Python version")
        print(f"  2. Create virtual environment")
        print(f"  3. Install dependencies")
        print(f"  4. Create configuration files")
        print(f"  5. Setup MongoDB (guide)")
        print(f"  6. Test system")
        
        print(f"\nDetected OS: {self.os_type}")
        print(f"Python Version: {self.python_version}")
        print(f"Project Directory: {self.project_root}")
        
        response = input("\n▶ Continue with setup? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return False
            
        # Run setup steps
        steps = [
            self.check_python_version,
            self.create_virtual_environment,
            self.install_requirements,
            self.create_env_file,
            self.setup_mongodb,
            self.test_system
        ]
        
        for step in steps:
            if not step():
                print(f"\n❌ Setup failed at: {step.__name__}")
                print(f"Please fix the error and run setup again.")
                return False
        
        # Print next steps
        self.print_next_steps()
        return True

def main():
    """Main entry point"""
    setup = SetupManager()
    success = setup.run_setup()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
