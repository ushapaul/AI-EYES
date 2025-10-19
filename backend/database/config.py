"""
MongoDB Configuration for AI Eyes Security System
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'ai_eyes_security')

# Collection Names
CAMERAS_COLLECTION = 'cameras'
ALERTS_COLLECTION = 'alerts'
LOGS_COLLECTION = 'logs'
USERS_COLLECTION = 'users'
SETTINGS_COLLECTION = 'settings'

class DatabaseConnection:
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Connect to MongoDB database"""
        try:
            print(f"🔌 Connecting to MongoDB...")
            
            # Simple connection for local MongoDB (no SSL needed)
            self._client = MongoClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            
            # Test the connection
            self._client.admin.command('ping')
            self._database = self._client[DATABASE_NAME]
            
            # Check if this is MongoDB Atlas or Local
            is_local = 'localhost' in MONGODB_URL or '127.0.0.1' in MONGODB_URL
            db_type = "MongoDB Local" if is_local else "MongoDB Atlas (Cloud)"
            
            print(f"✅ Connected to {db_type}: {DATABASE_NAME}")
            self._create_indexes()
            
        except Exception as e:
            print(f"⚠️ MongoDB connection failed: {str(e)[:80]}")
            print("🔄 Using JSON storage as fallback...")
            self._client = None
            self._database = None
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        if self._database is None:
            return
            
        try:
            # Cameras collection indexes
            self._database[CAMERAS_COLLECTION].create_index("name")
            self._database[CAMERAS_COLLECTION].create_index("status")
            
            # Alerts collection indexes
            self._database[ALERTS_COLLECTION].create_index("timestamp")
            self._database[ALERTS_COLLECTION].create_index("camera_id")
            self._database[ALERTS_COLLECTION].create_index("severity")
            
            # Logs collection indexes
            self._database[LOGS_COLLECTION].create_index("timestamp")
            self._database[LOGS_COLLECTION].create_index("camera_id")
            
            print("✅ Database indexes created successfully")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")
    
    @property
    def database(self):
        """Get database instance"""
        if self._database is None:
            self.connect()
        return self._database
    
    @property
    def is_connected(self):
        """Check if connected to database"""
        return self._client is not None and self._database is not None
    
    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            print("🔌 MongoDB connection closed")

# Global database instance - will be initialized when first accessed
db_connection = None

def get_database():
    """Get database instance with lazy initialization"""
    global db_connection
    if db_connection is None:
        db_connection = DatabaseConnection()
    return db_connection.database

def is_db_connected():
    """Check if database is connected"""
    global db_connection
    if db_connection is None:
        db_connection = DatabaseConnection()
    return db_connection.is_connected