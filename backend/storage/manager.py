"""
Storage Management for AI Eyes Security System
Handles local file storage for images, videos, and snapshots
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image
import io
from typing import Optional, Dict, Any

# Try to import OpenCV, but make it optional
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV not available. Webcam capture will be limited.")

class StorageManager:
    """Manages local storage for security system files"""
    
    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            # Default to storage folder in backend directory
            self.base_path = Path(__file__).parent.parent / "storage"
        else:
            self.base_path = Path(base_path)
        
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary storage directories"""
        directories = [
            'images',           # General images
            'snapshots',        # Camera snapshots
            'recordings',       # Video recordings
            'alerts',          # Alert-related images
            'temp',            # Temporary files
            'logs'             # Log files
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
        print(f"✅ Storage directories created at: {self.base_path}")
    
    @property
    def images_path(self) -> Path:
        """Get images directory path"""
        return self.base_path / "images"
    
    @property
    def snapshots_path(self) -> Path:
        """Get snapshots directory path"""
        return self.base_path / "snapshots"
    
    @property
    def recordings_path(self) -> Path:
        """Get recordings directory path"""
        return self.base_path / "recordings"
    
    @property
    def alerts_path(self) -> Path:
        """Get alerts directory path"""
        return self.base_path / "alerts"
    
    @property
    def temp_path(self) -> Path:
        """Get temporary files directory path"""
        return self.base_path / "temp"
    
    def save_snapshot(self, camera_id: str, image_data: bytes, 
                     file_format: str = "jpg") -> Optional[str]:
        """Save a camera snapshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"camera_{camera_id}_{timestamp}.{file_format}"
        file_path = self.snapshots_path / filename
        
        try:
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            print(f"📸 Snapshot saved: {filename}")
            return str(file_path)
        except Exception as e:
            print(f"❌ Error saving snapshot: {e}")
            return None
    
    def save_alert_image(self, camera_id: str, alert_id: str, 
                        image_data: bytes, file_format: str = "jpg") -> Optional[str]:
        """Save an alert-related image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alert_{alert_id}_camera_{camera_id}_{timestamp}.{file_format}"
        file_path = self.alerts_path / filename
        
        try:
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            print(f"🚨 Alert image saved: {filename}")
            return str(file_path)
        except Exception as e:
            print(f"❌ Error saving alert image: {e}")
            return None
    
    def capture_from_ip_camera(self, camera_url: str, camera_id: str, 
                              username: str = "", password: str = "") -> Optional[str]:
        """Capture image from IP camera - Fast snapshot method"""
        try:
            print(f"📸 Fast snapshot from: {camera_url}")
            
            # For IP Webcam, directly use /shot.jpg which is instant
            # Try most likely URLs first with shorter timeout
            snapshot_urls = []
            
            if '/video' in camera_url:
                # Replace /video with /shot.jpg for IP Webcam
                snapshot_urls.append(camera_url.replace('/video', '/shot.jpg'))
            
            # Add other common snapshot endpoints
            base_url = camera_url.rstrip('/video').rstrip('/')
            snapshot_urls.extend([
                f"{base_url}/shot.jpg",
                f"{base_url}/snapshot.jpg",
                f"{base_url}/image.jpg",
                camera_url  # Original URL as fallback
            ])
            
            # Remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in snapshot_urls:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)
            
            # Try each URL with short timeout (2 seconds max)
            for url in unique_urls:
                try:
                    print(f"  🔍 Trying: {url}")
                    
                    # Setup authentication if provided
                    auth = None
                    if username and password:
                        auth = (username, password)
                    
                    # Use shorter timeout for faster response
                    response = requests.get(url, auth=auth, timeout=2, stream=False)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'image' in content_type or len(response.content) > 1000:
                            # Got an image, save it
                            print(f"  ✅ Snapshot captured from: {url}")
                            return self.save_snapshot(camera_id, response.content)
                    
                except requests.RequestException as e:
                    print(f"  ⏭️  Skipping {url}: {str(e)[:50]}")
                    continue
            
            # If all direct methods fail, try OpenCV as last resort (but with timeout)
            print(f"  🔄 Trying OpenCV capture...")
            return self.capture_with_opencv_fast(camera_url, camera_id)
            
        except Exception as e:
            print(f"❌ Error capturing from IP camera {camera_id}: {e}")
            return None
    
    def capture_with_opencv_fast(self, camera_url: str, camera_id: str, timeout_seconds: int = 5) -> Optional[str]:
        """Capture image using OpenCV with timeout"""
        if not OPENCV_AVAILABLE:
            print("❌ OpenCV not available for camera capture")
            return None
            
        try:
            import threading
            import time
            
            result = {'frame': None, 'success': False}
            
            def capture_frame():
                try:
                    # Convert URL for OpenCV if needed
                    if camera_url == "0" or camera_url == "0/video":
                        cap = cv2.VideoCapture(0)  # Default webcam
                    else:
                        cap = cv2.VideoCapture(camera_url)
                    
                    if cap.isOpened():
                        # Read a frame
                        ret, frame = cap.read()
                        if ret:
                            result['frame'] = frame
                            result['success'] = True
                    
                    cap.release()
                except Exception as e:
                    print(f"  ⚠️ OpenCV capture error: {e}")
            
            # Run capture in thread with timeout
            capture_thread = threading.Thread(target=capture_frame)
            capture_thread.daemon = True
            capture_thread.start()
            capture_thread.join(timeout=timeout_seconds)
            
            if result['success'] and result['frame'] is not None:
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', result['frame'])
                image_data = buffer.tobytes()
                print(f"  ✅ OpenCV snapshot captured")
                return self.save_snapshot(camera_id, image_data)
            else:
                print(f"  ❌ OpenCV capture timeout or failed")
                return None
                
        except Exception as e:
            print(f"❌ Error with OpenCV capture: {e}")
            return None
    
    def capture_with_opencv(self, camera_url: str, camera_id: str) -> Optional[str]:
        """Legacy OpenCV capture - redirects to fast version"""
        return self.capture_with_opencv_fast(camera_url, camera_id)
    
    def resize_image(self, image_path: str, max_width: int = 1920, 
                    max_height: int = 1080) -> str:
        """Resize image to optimize storage"""
        try:
            with Image.open(image_path) as img:
                # Calculate new size maintaining aspect ratio
                ratio = min(max_width / img.width, max_height / img.height)
                if ratio < 1:
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Save resized image
                    img.save(image_path, optimize=True, quality=85)
                    print(f"🔄 Image resized: {image_path}")
            
            return image_path
        except Exception as e:
            print(f"❌ Error resizing image: {e}")
            return image_path
    
    def cleanup_old_files(self, days_old: int = 7):
        """Clean up files older than specified days"""
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        directories_to_clean = [
            self.snapshots_path,
            self.temp_path,
            self.alerts_path
        ]
        
        files_deleted = 0
        for directory in directories_to_clean:
            for file_path in directory.glob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        files_deleted += 1
                    except Exception as e:
                        print(f"❌ Error deleting {file_path}: {e}")
        
        print(f"🧹 Cleaned up {files_deleted} old files")
        return files_deleted
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        stats = {}
        
        for directory in ['images', 'snapshots', 'recordings', 'alerts', 'temp']:
            dir_path = self.base_path / directory
            
            if dir_path.exists():
                file_count = len(list(dir_path.glob("*")))
                total_size = sum(f.stat().st_size for f in dir_path.glob("*") if f.is_file())
                
                stats[directory] = {
                    'file_count': file_count,
                    'size_bytes': total_size,
                    'size_mb': round(total_size / (1024 * 1024), 2)
                }
            else:
                stats[directory] = {'file_count': 0, 'size_bytes': 0, 'size_mb': 0}
        
        return stats

# Global storage manager instance
storage_manager = StorageManager()