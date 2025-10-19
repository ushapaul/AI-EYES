"""
Database Models for AI Eyes Security System
MongoDB-only storage (no JSON fallback)
"""
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from database.config import get_database, is_db_connected, CAMERAS_COLLECTION, ALERTS_COLLECTION, LOGS_COLLECTION, SETTINGS_COLLECTION, USERS_COLLECTION

class BaseModel:
    """Base model with MongoDB-only operations"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
    
    @property
    def collection(self):
        """Get collection from database"""
        db = get_database()
        if db is not None:
            return db[self.collection_name]
        return None
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all documents"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - {self.collection_name}")
            return []
            
        try:
            documents = list(self.collection.find())
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if '_id' in doc:
                    doc['id'] = str(doc['_id'])
                    del doc['_id']
            return documents
        except Exception as e:
            print(f"❌ Database error in find_all: {e}")
            return []
    
    def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - {self.collection_name}")
            return None
            
        try:
            if isinstance(doc_id, str) and len(doc_id) == 24:
                # MongoDB ObjectId
                doc = self.collection.find_one({"_id": ObjectId(doc_id)})
            else:
                # Regular ID
                doc = self.collection.find_one({"id": int(doc_id) if doc_id.isdigit() else doc_id})
            
            if doc:
                doc['id'] = str(doc['_id']) if '_id' in doc else doc.get('id')
                if '_id' in doc:
                    del doc['_id']
                return doc
        except Exception as e:
            print(f"❌ Database error in find_by_id: {e}")
        
        return None
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert a document and return ID"""
        document['created_at'] = datetime.utcnow()
        document['updated_at'] = datetime.utcnow()
        
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot insert into {self.collection_name}")
            return ""
            
        try:
            result = self.collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Database error in insert_one: {e}")
            return ""
    
    def update_by_id(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update document by ID"""
        update_data['updated_at'] = datetime.utcnow()
        
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot update {self.collection_name}")
            return False
            
        try:
            if isinstance(doc_id, str) and len(doc_id) == 24:
                result = self.collection.update_one(
                    {"_id": ObjectId(doc_id)}, 
                    {"$set": update_data}
                )
            else:
                result = self.collection.update_one(
                    {"id": int(doc_id) if doc_id.isdigit() else doc_id}, 
                    {"$set": update_data}
                )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Database error in update_by_id: {e}")
            return False
    
    def delete_by_id(self, doc_id: str) -> bool:
        """Delete document by ID"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot delete from {self.collection_name}")
            return False
            
        try:
            if isinstance(doc_id, str) and len(doc_id) == 24:
                result = self.collection.delete_one({"_id": ObjectId(doc_id)})
            else:
                result = self.collection.delete_one({"id": int(doc_id) if doc_id.isdigit() else doc_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"❌ Database error in delete_by_id: {e}")
            return False

class CameraModel(BaseModel):
    """Camera model for managing IP cameras and webcams"""
    
    def __init__(self):
        super().__init__(CAMERAS_COLLECTION)
    
    def create_camera(self, name: str, location: str, url: str, camera_type: str, 
                     username: str = "", password: str = "", enabled: bool = True, 
                     ai_mode: str = "both") -> str:
        """Create a new camera
        
        Args:
            ai_mode: AI detection mode - 'lbph' (face recognition only), 
                    'yolov9' (activity detection only), or 'both' (default)
        """
        camera_data = {
            'name': name,
            'location': location,
            'url': url,
            'type': camera_type,
            'username': username,
            'password': password,
            'enabled': enabled,
            'status': 'online',
            'last_seen': datetime.utcnow(),
            'recording': False,
            'motion_detection': True,
            'ai_detection': True,
            'ai_mode': ai_mode  # 'lbph', 'yolov9', or 'both'
        }
        
        return self.insert_one(camera_data)
    
    def update_camera(self, camera_id: str, update_data: Dict[str, Any]) -> bool:
        """Update camera with provided data"""
        return self.update_by_id(camera_id, update_data)
    
    def get_online_cameras(self) -> List[Dict[str, Any]]:
        """Get all online cameras"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - {self.collection_name}")
            return []
            
        try:
            cameras = list(self.collection.find({"status": "online"}))
            for camera in cameras:
                if '_id' in camera:
                    camera['id'] = str(camera['_id'])
                    del camera['_id']
            return cameras
        except Exception as e:
            print(f"❌ Database error in get_online_cameras: {e}")
            return []
    
    def update_camera_status(self, camera_id: str, status: str) -> bool:
        """Update camera status"""
        return self.update_by_id(camera_id, {
            'status': status,
            'last_seen': datetime.utcnow()
        })

class AlertModel(BaseModel):
    """Alert model for security events"""
    
    def __init__(self):
        super().__init__(ALERTS_COLLECTION)
    
    def create_alert(self, camera_id: str, alert_type: str, message: str, 
                    severity: str = "medium", image_path: Optional[str] = None) -> str:
        """Create a new alert"""
        alert_data = {
            'camera_id': camera_id,
                'type': alert_type,
            'message': message,
            'severity': severity,  # low, medium, high, critical
            'image_path': image_path,
            'timestamp': datetime.utcnow(),
            'resolved': False,
            'acknowledged': False
        }
        
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot create alert")
            return ""
            
        try:
            # Check for duplicates in last 5 minutes
            from datetime import timedelta
            recent_time = datetime.utcnow() - timedelta(seconds=300)
            duplicate = self.collection.find_one({
                'camera_id': camera_id,
                'type': alert_type,
                'message': message,
                'timestamp': {'$gte': recent_time},
                'status': {'$ne': 'dismissed'}
            })
            
            if duplicate:
                print(f" Duplicate alert blocked: {alert_type} from {camera_id}")
                return ""
            
            alert_data['created_at'] = datetime.utcnow()
            alert_data['updated_at'] = datetime.utcnow()
            result = self.collection.insert_one(alert_data)
            print(f"💾 Alert saved to MongoDB: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ MongoDB save failed: {e}")
            return ""
    
    def get_recent_alerts(self, limit: int = 50, include_dismissed: bool = False) -> List[Dict[str, Any]]:
        """Get recent alerts
        
        Args:
            limit: Maximum number of alerts to return
            include_dismissed: If False, excludes dismissed and acknowledged alerts
        """
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot get alerts")
            return []
            
        try:
            # Build query to exclude dismissed/acknowledged alerts by default
            query = {}
            if not include_dismissed:
                query = {
                    "$or": [
                        {"status": {"$exists": False}},  # Old alerts without status field
                        {"status": {"$ne": "dismissed"}}  # All alerts except dismissed
                    ]
                }
            
            alerts = list(self.collection.find(query).sort("timestamp", -1).limit(limit))
            for alert in alerts:
                if '_id' in alert:
                    alert['id'] = str(alert['_id'])
                    del alert['_id']
            return alerts
        except Exception as e:
            print(f"❌ MongoDB query failed: {e}")
            return []
    
    def get_alerts_today(self) -> int:
        """Get count of alerts today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot count alerts")
            return 0
            
        try:
            return self.collection.count_documents({"timestamp": {"$gte": today_start}})
        except Exception as e:
            print(f"❌ MongoDB query failed: {e}")
            return 0

class LogModel(BaseModel):
    """Log model for system events"""
    
    def __init__(self):
        super().__init__(LOGS_COLLECTION)
    
    def create_log(self, camera_id: str, action: str, description: str, log_level: str = "info") -> str:
        """Create a new log entry"""
        log_data = {
            'camera_id': camera_id,
            'action': action,
            'description': description,
            'level': log_level,  # debug, info, warning, error, critical
            'timestamp': datetime.utcnow(),
            'user_agent': 'AI Eyes System'
        }
        
        return self.insert_one(log_data)
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot get logs")
            return []
            
        try:
            logs = list(self.collection.find().sort("timestamp", -1).limit(limit))
            for log in logs:
                if '_id' in log:
                    log['id'] = str(log['_id'])
                    del log['_id']
            return logs
        except Exception as e:
            print(f"❌ Database error in get_recent_logs: {e}")
            return []

class SettingsModel(BaseModel):
    """Settings model for system configuration"""
    
    def __init__(self):
        super().__init__(SETTINGS_COLLECTION)
    
    def get_settings(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get all settings or settings by category"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot get settings")
            return self._get_default_settings()
            
        try:
            if category:
                # Get specific category
                setting_doc = self.collection.find_one({'category': category})
                if setting_doc:
                    if '_id' in setting_doc:
                        setting_doc['id'] = str(setting_doc['_id'])
                        del setting_doc['_id']
                    return setting_doc
                else:
                    # Return defaults for this category
                    defaults = self._get_default_settings()
                    return {cat: data for cat, data in defaults.items() if cat == category}
            else:
                # Get all settings
                all_settings = {}
                settings_docs = list(self.collection.find())
                
                if not settings_docs:
                    # Initialize with defaults
                    return self._initialize_default_settings()
                
                for doc in settings_docs:
                    if '_id' in doc:
                        doc['id'] = str(doc['_id'])
                        del doc['_id']
                    category = doc.get('category', 'unknown')
                    all_settings[category] = doc.get('settings', {})
                
                return all_settings
        except Exception as e:
            print(f"❌ Database error in get_settings: {e}")
            return self._get_default_settings()
    
    def update_settings(self, category: str, settings: Dict[str, Any]) -> bool:
        """Update settings for a specific category"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot update settings")
            return False
            
        try:
            result = self.collection.update_one(
                {'category': category},
                {
                    '$set': {
                        'settings': settings,
                        'updated_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Log the settings update
            log_model.create_log(
                'system',
                'settings_updated',
                f'{category.capitalize()} settings updated',
                'info'
            )
            
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            print(f"❌ Database error in update_settings: {e}")
            return False
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings structure"""
        return {
            'system': {
                'systemName': 'AI Eyes Security System',
                'timezone': 'UTC',
                'language': 'en',
                'dateFormat': 'MM/DD/YYYY',
                'timeFormat': '12h',
                'autoBackup': True,
                'backupFrequency': 'daily',
                'backupRetention': '30',
                'systemUpdates': 'auto',
                'maintenanceMode': False,
                'debugMode': False,
                'logLevel': 'info'
            },
            'camera': {
                'defaultResolution': '1080p',
                'frameRate': '30',
                'compressionLevel': 'medium',
                'nightVision': True,
                'motionDetection': True,
                'motionSensitivity': '75',
                'recordingMode': 'motion',
                'recordingQuality': 'high',
                'storageLocation': 'local',
                'maxStorageSize': '500',
                'autoDelete': True,
                'retentionDays': '30',
                'streamingEnabled': True,
                'streamingQuality': 'medium',
                'bandwidthLimit': '10'
            },
            'ai': {
                'faceRecognition': True,
                'faceRecognitionModel': 'MobileNetV2',
                'faceRecognitionThreshold': '80',
                'objectDetection': True,
                'objectDetectionModel': 'YOLOv8',
                'objectDetectionThreshold': '75',
                'behaviorAnalysis': False,
                'behaviorSensitivity': '70',
                'realTimeProcessing': True,
                'batchProcessing': False,
                'gpuAcceleration': False,
                'modelUpdateFrequency': 'weekly',
                'trainingDataCollection': True,
                'anonymizeData': True,
                'confidenceThreshold': '85'
            },
            'alerts': {
                'emailNotifications': True,
                'emailAddress': os.getenv('SENDGRID_FROM_EMAIL', 'admin@company.com'),
                'smsNotifications': False,
                'smsNumber': '',
                'pushNotifications': True,
                'webhookUrl': '',
                'alertSeverityFilter': 'medium',
                'alertFrequencyLimit': '5',
                'alertCooldown': '60',
                'escalationEnabled': True,
                'escalationDelay': '30',
                'escalationContacts': os.getenv('SENDGRID_FROM_EMAIL', 'security@company.com'),
                'soundAlerts': True,
                'alertVolume': '80',
                'customAlertTones': False,
                'alertHistory': '90'
            },
            'security': {
                'twoFactorAuth': False,
                'sessionTimeout': '30',
                'passwordPolicy': 'strong',
                'loginAttempts': '3',
                'accountLockout': '15',
                'ipWhitelist': '',
                'sslEnabled': False,
                'encryptionLevel': 'AES256',
                'auditLogging': True,
                'accessLogging': True,
                'dataRetention': '365',
                'gdprCompliance': True,
                'anonymizePersonalData': True,
                'dataExportEnabled': True,
                'apiAccess': False
            },
            'network': {
                'networkInterface': 'eth0',
                'ipAddress': '192.168.1.100',
                'subnetMask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dnsServer': '8.8.8.8',
                'dhcpEnabled': True,
                'portRange': '8000-8100',
                'firewallEnabled': False,
                'vpnEnabled': False,
                'vpnServer': '',
                'bandwidthMonitoring': True,
                'networkDiagnostics': True,
                'connectionTimeout': '30',
                'retryAttempts': '3',
                'proxyEnabled': False
            }
        }
    
    def _initialize_default_settings(self) -> Dict[str, Any]:
        """Initialize database with default settings"""
        if self.collection is None:
            return self._get_default_settings()
            
        try:
            defaults = self._get_default_settings()
            
            for category, settings in defaults.items():
                self.collection.insert_one({
                    'category': category,
                    'settings': settings,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                })
            
            print("✅ Default settings initialized in MongoDB")
            return defaults
        except Exception as e:
            print(f"❌ Error initializing default settings: {e}")
            return self._get_default_settings()

class UserModel(BaseModel):
    """User model for authentication and user management"""
    
    def __init__(self):
        super().__init__(USERS_COLLECTION)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email: str, password: str, first_name: str, last_name: str = '', 
                   role: str = 'user', department: str = '', phone: str = '', 
                   location: str = '', timezone: str = 'UTC') -> Optional[str]:
        """Create a new user account"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot create user")
            return None
            
        try:
            # Check if email already exists
            existing_user = self.collection.find_one({'email': email})
            if existing_user:
                print(f"⚠️ User with email {email} already exists")
                return None
            
            user_data = {
                'email': email.lower().strip(),
                'password': self._hash_password(password),
                'first_name': first_name,
                'last_name': last_name,
                'role': role,  # admin, security_admin, user, viewer
                'department': department,
                'phone': phone,
                'location': location,
                'timezone': timezone,
                'status': 'active',  # active, inactive, suspended
                'email_verified': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'last_login': None,
                'login_count': 0
            }
            
            user_id = self.insert_one(user_data)
            
            # Log user creation
            log_model.create_log(
                'system',
                'user_created',
                f'New user account created: {email}',
                'info'
            )
            
            print(f"✅ User created successfully: {email}")
            return user_id
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        if self.collection is None:
            print(f"⚠️ MongoDB not connected - cannot authenticate")
            return None
            
        try:
            user = self.collection.find_one({
                'email': email.lower().strip(),
                'password': self._hash_password(password)
            })
            
            if user:
                # Update last login
                self.collection.update_one(
                    {'_id': user['_id']},
                    {
                        '$set': {'last_login': datetime.utcnow()},
                        '$inc': {'login_count': 1}
                    }
                )
                
                # Log successful login
                log_model.create_log(
                    'system',
                    'user_login',
                    f'User logged in: {email}',
                    'info'
                )
                
                # Remove password from returned data
                user['id'] = str(user['_id'])
                del user['_id']
                del user['password']
                
                # Convert snake_case to camelCase for frontend compatibility
                if 'first_name' in user:
                    user['firstName'] = user.pop('first_name')
                if 'last_name' in user:
                    user['lastName'] = user.pop('last_name')
                if 'email_verified' in user:
                    user['emailVerified'] = user.pop('email_verified')
                if 'created_at' in user:
                    user['createdAt'] = user.pop('created_at')
                if 'updated_at' in user:
                    user['updatedAt'] = user.pop('updated_at')
                if 'last_login' in user:
                    user['lastLogin'] = user.pop('last_login')
                if 'login_count' in user:
                    user['loginCount'] = user.pop('login_count')
                
                return user
            else:
                print(f"⚠️ Invalid credentials for: {email}")
                return None
                
        except Exception as e:
            print(f"❌ Error authenticating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email (without password)"""
        if self.collection is None:
            return None
            
        try:
            user = self.collection.find_one({'email': email.lower().strip()})
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
                del user['password']  # Never return password
                
                # Convert snake_case to camelCase for frontend compatibility
                if 'first_name' in user:
                    user['firstName'] = user.pop('first_name')
                if 'last_name' in user:
                    user['lastName'] = user.pop('last_name')
                if 'email_verified' in user:
                    user['emailVerified'] = user.pop('email_verified')
                if 'created_at' in user:
                    user['createdAt'] = user.pop('created_at')
                if 'updated_at' in user:
                    user['updatedAt'] = user.pop('updated_at')
                if 'last_login' in user:
                    user['lastLogin'] = user.pop('last_login')
                if 'login_count' in user:
                    user['loginCount'] = user.pop('login_count')
                    
                return user
            return None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID (without password)"""
        if self.collection is None:
            return None
            
        try:
            if len(user_id) == 24:
                user = self.collection.find_one({'_id': ObjectId(user_id)})
            else:
                user = self.collection.find_one({'_id': user_id})
                
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
                del user['password']  # Never return password
                
                # Convert snake_case to camelCase for frontend compatibility
                if 'first_name' in user:
                    user['firstName'] = user.pop('first_name')
                if 'last_name' in user:
                    user['lastName'] = user.pop('last_name')
                if 'email_verified' in user:
                    user['emailVerified'] = user.pop('email_verified')
                if 'created_at' in user:
                    user['createdAt'] = user.pop('created_at')
                if 'updated_at' in user:
                    user['updatedAt'] = user.pop('updated_at')
                if 'last_login' in user:
                    user['lastLogin'] = user.pop('last_login')
                if 'login_count' in user:
                    user['loginCount'] = user.pop('login_count')
                    
                return user
            return None
        except Exception as e:
            print(f"❌ Error getting user by ID: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user information"""
        if self.collection is None:
            return False
            
        try:
            # Convert camelCase to snake_case for database storage
            if 'firstName' in updates:
                updates['first_name'] = updates.pop('firstName')
            if 'lastName' in updates:
                updates['last_name'] = updates.pop('lastName')
            if 'emailVerified' in updates:
                updates['email_verified'] = updates.pop('emailVerified')
            if 'lastLogin' in updates:
                updates['last_login'] = updates.pop('lastLogin')
            if 'loginCount' in updates:
                updates['login_count'] = updates.pop('loginCount')
            if 'createdAt' in updates:
                updates['created_at'] = updates.pop('createdAt')
            if 'updatedAt' in updates:
                updates['updated_at'] = updates.pop('updatedAt')
            
            # Remove sensitive fields from updates
            sensitive_fields = ['password', '_id', 'id', 'created_at']
            for field in sensitive_fields:
                updates.pop(field, None)
            
            updates['updated_at'] = datetime.utcnow()
            
            if len(user_id) == 24:
                result = self.collection.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': updates}
                )
            else:
                result = self.collection.update_one(
                    {'_id': user_id},
                    {'$set': updates}
                )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return False
    
    def update_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Update user password"""
        if self.collection is None:
            return False
            
        try:
            # Verify old password
            if len(user_id) == 24:
                user = self.collection.find_one({
                    '_id': ObjectId(user_id),
                    'password': self._hash_password(old_password)
                })
            else:
                user = self.collection.find_one({
                    '_id': user_id,
                    'password': self._hash_password(old_password)
                })
            
            if not user:
                print("⚠️ Invalid old password")
                return False
            
            # Update to new password
            if len(user_id) == 24:
                result = self.collection.update_one(
                    {'_id': ObjectId(user_id)},
                    {
                        '$set': {
                            'password': self._hash_password(new_password),
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
            else:
                result = self.collection.update_one(
                    {'_id': user_id},
                    {
                        '$set': {
                            'password': self._hash_password(new_password),
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating password: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (without passwords)"""
        if self.collection is None:
            return []
            
        try:
            users = list(self.collection.find())
            for user in users:
                user['id'] = str(user['_id'])
                del user['_id']
                del user['password']
            return users
        except Exception as e:
            print(f"❌ Error getting users: {e}")
            return []

# Global model instances
camera_model = CameraModel()
alert_model = AlertModel()
log_model = LogModel()
settings_model = SettingsModel()
user_model = UserModel()