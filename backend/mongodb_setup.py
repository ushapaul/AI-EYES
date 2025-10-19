"""
MongoDB Atlas Setup and Configuration Guide
Fixes SSL and connection issues
"""

# Step 1: Whitelist Your IP Address in MongoDB Atlas
# ====================================================
# 1. Go to: https://cloud.mongodb.com/
# 2. Login with your credentials
# 3. Select your cluster (Cluster0)
# 4. Click "Network Access" in left sidebar
# 5. Click "Add IP Address"
# 6. Add your current IP: 192.168.137.29 OR click "Allow Access from Anywhere" (0.0.0.0/0)
# 7. Click "Confirm"
# 8. Wait 2-3 minutes for changes to take effect

# Step 2: Verify Database User
# =============================
# 1. Click "Database Access" in left sidebar
# 2. Verify user exists: praveenkumarnaik14_db_user
# 3. Password: qnwUOOrDJ0RgBwp7
# 4. Verify "Read and write to any database" is enabled

# Step 3: Test Connection
# ========================
# Run this file to test MongoDB connection:
# python mongodb_setup.py

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv('MONGODB_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'ai_eyes_security')

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    print("=" * 60)
    print("🧪 Testing MongoDB Atlas Connection")
    print("=" * 60)
    
    print(f"\n📍 Connection String: {MONGODB_URL[:30]}...{MONGODB_URL[-20:]}")
    print(f"📊 Database Name: {DATABASE_NAME}")
    
    try:
        print(f"\n🔌 Connecting to MongoDB...")
        
        # Determine if this is local or Atlas
        mongodb_url_str = MONGODB_URL or ""
        is_local = 'localhost' in mongodb_url_str or '127.0.0.1' in mongodb_url_str
        
        if is_local:
            # Local MongoDB - no SSL needed
            print("📍 Target: MongoDB Local Server")
            client = MongoClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
        else:
            # MongoDB Atlas - needs SSL
            print("📍 Target: MongoDB Atlas (Cloud)")
            client = MongoClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=15000,
                connectTimeoutMS=15000,
                socketTimeoutMS=30000,
                tls=True,
                tlsAllowInvalidCertificates=True
            )
        
        # Test connection
        print("📡 Pinging MongoDB server...")
        client.admin.command('ping')
        
        # Get database
        db = client[DATABASE_NAME]
        
        # List collections
        print("📂 Fetching collections...")
        collections = db.list_collection_names()
        
        print("\n" + "=" * 60)
        print("✅ MongoDB Atlas Connection Successful!")
        print("=" * 60)
        
        print(f"\n📊 Database: {DATABASE_NAME}")
        print(f"📁 Collections: {len(collections)}")
        
        if collections:
            print("\n📋 Available collections:")
            for col in collections:
                count = db[col].count_documents({})
                print(f"   • {col}: {count} documents")
        else:
            print("\n📝 No collections yet (will be created automatically)")
        
        # Test write operation
        print("\n✍️ Testing write operation...")
        test_collection = db['test_connection']
        result = test_collection.insert_one({'test': 'success', 'timestamp': 'now'})
        print(f"✅ Write successful! Document ID: {result.inserted_id}")
        
        # Clean up test
        test_collection.delete_one({'_id': result.inserted_id})
        print("🧹 Test document cleaned up")
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! MongoDB is ready to use!")
        print("=" * 60)
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print("\n" + "=" * 60)
        print("❌ MongoDB Connection Failed")
        print("=" * 60)
        print(f"\n⚠️ Error: {str(e)}")
        
        print("\n🔧 Troubleshooting Steps:")
        print("\n1. Check Network Access:")
        print("   • Go to MongoDB Atlas → Network Access")
        print("   • Add IP: 192.168.137.29 OR 0.0.0.0/0 (allow all)")
        print("   • Wait 2-3 minutes for changes")
        
        print("\n2. Check Database User:")
        print("   • Go to MongoDB Atlas → Database Access")
        print("   • Verify user: praveenkumarnaik14_db_user")
        print("   • Verify password is correct")
        
        print("\n3. Check Internet Connection:")
        print("   • Test: ping mongodb.net")
        print("   • Check firewall settings")
        
        print("\n4. Check Connection String:")
        print("   • Verify MONGODB_URL in .env file")
        print("   • Get new connection string from Atlas if needed")
        
        return False
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ Unexpected Error")
        print("=" * 60)
        print(f"\n⚠️ Error: {str(e)}")
        print(f"⚠️ Type: {type(e).__name__}")
        
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    
    if success:
        print("\n✅ You can now use MongoDB in your application!")
        print("🚀 Start backend: python app_simple.py")
    else:
        print("\n⚠️ MongoDB not available - will use JSON storage")
        print("📝 JSON storage works perfectly for your use case!")
        print("🚀 Start backend anyway: python app_simple.py")
    
    sys.exit(0 if success else 1)
