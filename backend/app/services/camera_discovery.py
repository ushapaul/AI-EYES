"""
Camera Discovery Service
Auto-discovers IP cameras on the network using multiple protocols
MongoDB storage only (no JSON fallback)
"""

import socket
import requests
import threading
import time
from typing import List, Dict, Optional
from datetime import datetime
import ipaddress
from database.config import get_database

class CameraDiscovery:
    """Auto-discover IP cameras on the network"""
    
    def __init__(self):
        self.discovered_cameras = []
        self.scanning = False
        self.load_discovered_cameras()
        
    @property
    def cameras_collection(self):
        """Get MongoDB cameras collection"""
        db = get_database()
        if db is not None:
            return db['discovered_cameras']
        return None
        
    def load_discovered_cameras(self):
        """Load previously discovered cameras from MongoDB"""
        try:
            if self.cameras_collection is not None:
                cameras = list(self.cameras_collection.find())
                # Convert ObjectId to string
                for camera in cameras:
                    if '_id' in camera:
                        camera['id'] = str(camera['_id'])
                        del camera['_id']
                self.discovered_cameras = cameras
                print(f"📂 Loaded {len(self.discovered_cameras)} previously discovered cameras from MongoDB")
            else:
                print("⚠️ MongoDB not connected - cannot load cameras")
                self.discovered_cameras = []
        except Exception as e:
            print(f"❌ Could not load discovered cameras: {e}")
            self.discovered_cameras = []
    
    def save_discovered_cameras(self):
        """Save discovered cameras to MongoDB"""
        try:
            if self.cameras_collection is None:
                print("⚠️ MongoDB not connected - cannot save cameras")
                return
                
            # Clear existing and insert all
            self.cameras_collection.delete_many({})
            if self.discovered_cameras:
                # Remove any _id fields before inserting
                cameras_to_insert = []
                for camera in self.discovered_cameras:
                    cam_copy = camera.copy()
                    if '_id' in cam_copy:
                        del cam_copy['_id']
                    cameras_to_insert.append(cam_copy)
                
                self.cameras_collection.insert_many(cameras_to_insert)
                print(f"💾 Saved {len(self.discovered_cameras)} discovered cameras to MongoDB")
        except Exception as e:
            print(f"❌ Could not save discovered cameras: {e}")
    
    def get_local_ip(self) -> str:
        """Get local IP address of this machine"""
        try:
            # Connect to Google DNS to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "192.168.1.1"  # Fallback
    
    def get_network_range(self) -> str:
        """Get network range to scan (e.g., 192.168.1.0/24)"""
        local_ip = self.get_local_ip()
        # Convert to network (e.g., 192.168.1.0/24)
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        return str(network)
    
    def check_ip_webcam(self, ip: str, timeout: float = 0.5) -> Optional[Dict]:
        """Check if IP Webcam app is running on this IP"""
        # Common IP Webcam ports
        ports = [8080, 8081, 4747]
        
        for port in ports:
            try:
                # Try to connect to IP Webcam video endpoint
                url = f"http://{ip}:{port}/video"
                response = requests.head(url, timeout=timeout)
                
                if response.status_code in [200, 302]:
                    print(f"📱 Found IP Webcam at {ip}:{port}")
                    return {
                        'id': f'camera_{ip.replace(".", "_")}_{port}',
                        'name': f'IP Webcam {ip}',
                        'ip': ip,
                        'port': port,
                        'url': url,
                        'type': 'ip_webcam',
                        'status': 'online',
                        'last_seen': datetime.now().isoformat(),
                        'discovered_at': datetime.now().isoformat()
                    }
            except:
                continue
        
        return None
    
    def check_rtsp_camera(self, ip: str, timeout: float = 0.5) -> Optional[Dict]:
        """Check if RTSP camera is available on this IP"""
        # Common RTSP ports
        ports = [554, 8554]
        
        for port in ports:
            try:
                # Try to connect to RTSP port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    print(f"📹 Found RTSP camera at {ip}:{port}")
                    return {
                        'id': f'camera_{ip.replace(".", "_")}_{port}',
                        'name': f'RTSP Camera {ip}',
                        'ip': ip,
                        'port': port,
                        'url': f'rtsp://{ip}:{port}/stream',
                        'type': 'rtsp',
                        'status': 'online',
                        'last_seen': datetime.now().isoformat(),
                        'discovered_at': datetime.now().isoformat()
                    }
            except:
                continue
        
        return None
    
    def check_http_camera(self, ip: str, timeout: float = 0.5) -> Optional[Dict]:
        """Check if HTTP camera is available on this IP"""
        # Common HTTP camera endpoints
        endpoints = [
            (80, '/video'),
            (80, '/mjpeg'),
            (8080, '/'),
        ]
        
        for port, path in endpoints:
            try:
                url = f"http://{ip}:{port}{path}"
                response = requests.head(url, timeout=timeout)
                
                if response.status_code in [200, 302]:
                    print(f"🎥 Found HTTP camera at {url}")
                    return {
                        'id': f'camera_{ip.replace(".", "_")}_{port}',
                        'name': f'HTTP Camera {ip}',
                        'ip': ip,
                        'port': port,
                        'url': url,
                        'type': 'http',
                        'status': 'online',
                        'last_seen': datetime.now().isoformat(),
                        'discovered_at': datetime.now().isoformat()
                    }
            except:
                continue
        
        return None
    
    def scan_ip(self, ip: str):
        """Scan a single IP for cameras"""
        # Skip local machine
        local_ip = self.get_local_ip()
        if ip == local_ip:
            return
        
        # Check for different camera types
        camera = None
        
        # 1. Try IP Webcam first (most common)
        camera = self.check_ip_webcam(ip, timeout=0.3)
        
        # 2. Try RTSP camera
        if not camera:
            camera = self.check_rtsp_camera(ip, timeout=0.3)
        
        # 3. Try HTTP camera
        if not camera:
            camera = self.check_http_camera(ip, timeout=0.3)
        
        # Add to discovered cameras if found
        if camera:
            # Check if camera already exists
            existing = next((c for c in self.discovered_cameras if c['id'] == camera['id']), None)
            
            if existing:
                # Update existing camera
                existing.update(camera)
            else:
                # Add new camera
                self.discovered_cameras.append(camera)
            
            self.save_discovered_cameras()
    
    def scan_network(self, network_range: Optional[str] = None):
        """Scan entire network for cameras"""
        if self.scanning:
            print("⚠️ Scan already in progress")
            return
        
        self.scanning = True
        
        try:
            if not network_range:
                network_range = self.get_network_range()
            
            print(f"🔍 Scanning network {network_range} for cameras...")
            print(f"📍 Local IP: {self.get_local_ip()}")
            
            network = ipaddress.IPv4Network(network_range)
            threads = []
            
            # Scan all IPs in network
            for ip in network.hosts():
                ip_str = str(ip)
                thread = threading.Thread(target=self.scan_ip, args=(ip_str,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                
                # Limit concurrent threads
                if len(threads) >= 50:
                    for t in threads:
                        t.join()
                    threads = []
            
            # Wait for remaining threads
            for t in threads:
                t.join()
            
            print(f"✅ Scan complete. Found {len(self.discovered_cameras)} cameras")
            
        except Exception as e:
            print(f"❌ Error scanning network: {e}")
        
        finally:
            self.scanning = False
    
    def start_background_scan(self, interval: int = 300):
        """Start periodic background scanning (every 5 minutes by default)"""
        def scan_loop():
            while True:
                print(f"🔄 Starting periodic network scan...")
                self.scan_network()
                print(f"⏰ Next scan in {interval} seconds")
                time.sleep(interval)
        
        thread = threading.Thread(target=scan_loop, daemon=True)
        thread.start()
        print(f"🚀 Background camera scanning started (interval: {interval}s)")
    
    def get_cameras(self) -> List[Dict]:
        """Get all discovered cameras"""
        return self.discovered_cameras
    
    def add_manual_camera(self, name: str, url: str, camera_type: str = 'manual'):
        """Manually add a camera"""
        # Extract IP and port from URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            ip = parsed.hostname
            port = parsed.port or 8080
            
            camera = {
                'id': f'camera_{ip.replace(".", "_")}_{port}',
                'name': name,
                'ip': ip,
                'port': port,
                'url': url,
                'type': camera_type,
                'status': 'online',
                'last_seen': datetime.now().isoformat(),
                'discovered_at': datetime.now().isoformat(),
                'manual': True
            }
            
            # Check if camera already exists
            existing = next((c for c in self.discovered_cameras if c['id'] == camera['id']), None)
            
            if existing:
                existing.update(camera)
            else:
                self.discovered_cameras.append(camera)
            
            self.save_discovered_cameras()
            print(f"✅ Manually added camera: {name} ({url})")
            return camera
            
        except Exception as e:
            print(f"❌ Error adding manual camera: {e}")
            return None
    
    def remove_camera(self, camera_id: str):
        """Remove a camera"""
        self.discovered_cameras = [c for c in self.discovered_cameras if c['id'] != camera_id]
        self.save_discovered_cameras()
        print(f"🗑️ Removed camera: {camera_id}")
    
    def check_camera_connectivity(self, camera: Dict) -> bool:
        """Check if a camera is reachable"""
        try:
            url = camera['url']
            response = requests.head(url, timeout=2)
            return response.status_code in [200, 302]
        except:
            return False
    
    def update_camera_status(self):
        """Update status of all cameras (online/offline)"""
        print("🔄 Updating camera connectivity status...")
        
        for camera in self.discovered_cameras:
            is_online = self.check_camera_connectivity(camera)
            
            if is_online:
                camera['status'] = 'online'
                camera['last_seen'] = datetime.now().isoformat()
            else:
                camera['status'] = 'offline'
        
        self.save_discovered_cameras()
        print("✅ Camera status updated")
    
    def start_status_monitor(self, interval: int = 30):
        """Start periodic status monitoring (every 30 seconds by default)"""
        def monitor_loop():
            while True:
                self.update_camera_status()
                time.sleep(interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        print(f"🚀 Camera status monitoring started (interval: {interval}s)")


# Singleton instance
camera_discovery = CameraDiscovery()
