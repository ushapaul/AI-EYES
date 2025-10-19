#!/usr/bin/env python3
"""
SendGrid Email Alert Configuration Tool
Sets up SendGrid API for AI Eyes Security System
"""

import os
import sys
from datetime import datetime

def create_env_file():
    """Create .env file with SendGrid configuration"""
    
    print("🔧 AI Eyes Security - SendGrid Email Configuration")
    print("=" * 60)
    print()
    
    # Check if .env file already exists
    env_path = ".env"
    if os.path.exists(env_path):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Configuration cancelled.")
            return False
        print()
    
    print("📧 SendGrid Configuration Setup")
    print("To get your SendGrid API key:")
    print("1. Go to https://app.sendgrid.com/")
    print("2. Sign up or log in to your account")
    print("3. Go to Settings > API Keys")
    print("4. Create a new API key with 'Mail Send' permissions")
    print()
    
    # Get SendGrid API Key
    api_key = input("Enter your SendGrid API Key: ").strip()
    if not api_key:
        print("❌ API Key is required!")
        return False
    
    # Get From Email
    print()
    from_email = input("Enter 'From' email address (e.g., alerts@yourdomain.com): ").strip()
    if not from_email or '@' not in from_email:
        print("❌ Valid email address is required!")
        return False
    
    # Get From Name
    from_name = input("Enter 'From' name (default: AI Eyes Security): ").strip()
    if not from_name:
        from_name = "AI Eyes Security"
    
    # Get Recipients
    print()
    print("📬 Alert Recipients")
    recipients = []
    while True:
        email = input(f"Enter recipient email #{len(recipients) + 1} (or press Enter to finish): ").strip()
        if not email:
            break
        if '@' not in email:
            print("❌ Invalid email address, please try again.")
            continue
        recipients.append(email)
    
    if not recipients:
        print("❌ At least one recipient is required!")
        return False
    
    # Get Alert Settings
    print()
    enable_alerts = input("Enable email alerts? (Y/n): ").strip().lower()
    enable_alerts = enable_alerts != 'n'
    
    cooldown = input("Alert cooldown in minutes (default: 5): ").strip()
    try:
        cooldown = int(cooldown) if cooldown else 5
    except ValueError:
        cooldown = 5
    
    # Create .env content
    env_content = f"""# SendGrid Configuration for AI Eyes Security
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# SendGrid API Configuration
SENDGRID_API_KEY={api_key}
SENDGRID_FROM_EMAIL={from_email}
SENDGRID_FROM_NAME={from_name}

# Alert Recipients (comma-separated)
ALERT_RECIPIENTS={','.join(recipients)}

# Email Alert Settings
ENABLE_EMAIL_ALERTS={'true' if enable_alerts else 'false'}
ALERT_COOLDOWN_MINUTES={cooldown}

# MongoDB Configuration (if needed)
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
# MONGODB_DATABASE=ai_eyes_security
"""
    
    # Write .env file
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print()
        print("✅ Configuration saved successfully!")
        print(f"📄 Configuration file: {os.path.abspath(env_path)}")
        print()
        print("📧 Email Alert Configuration:")
        print(f"   • Service: SendGrid")
        print(f"   • From: {from_name} <{from_email}>")
        print(f"   • Recipients: {len(recipients)} configured")
        print(f"   • Alerts Enabled: {'Yes' if enable_alerts else 'No'}")
        print(f"   • Cooldown: {cooldown} minutes")
        print()
        print("🚀 Next Steps:")
        print("1. Start your surveillance system:")
        print("   python multi_camera_surveillance.py")
        print()
        print("2. Test email configuration:")
        print("   python test_sendgrid_config.py")
        print()
        print("3. Access dashboard at: http://localhost:5002")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def test_configuration():
    """Test the current SendGrid configuration"""
    
    print("🧪 Testing SendGrid Configuration...")
    print("=" * 40)
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import and test email service
        sys.path.append('.')
        from app.services.email_service import EmailAlertService
        
        email_service = EmailAlertService()
        status = email_service.get_configuration_status()
        
        print("📊 Configuration Status:")
        for key, value in status.items():
            icon = "✅" if value else "❌"
            print(f"   {icon} {key}: {value}")
        
        if status['configured'] and status['api_key_set']:
            print("\n🧪 Sending test email...")
            success = email_service.send_test_alert()
            
            if success:
                print("✅ Test email sent successfully!")
                print("📬 Check your email inbox for the test message.")
            else:
                print("❌ Failed to send test email.")
                print("Please check your SendGrid API key and settings.")
        else:
            print("\n❌ Configuration incomplete.")
            print("Please run the configuration setup first.")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure SendGrid is installed: pip install sendgrid")
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")

def main():
    """Main configuration interface"""
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_configuration()
        return
    
    print("🔧 AI Eyes Security - SendGrid Configuration")
    print("=" * 50)
    print()
    print("Choose an option:")
    print("1. Configure SendGrid Email Alerts")
    print("2. Test Current Configuration")
    print("3. Exit")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == '1':
        success = create_env_file()
        if success:
            print("\n🎉 Configuration complete!")
            test_config = input("\nTest the configuration now? (Y/n): ").strip().lower()
            if test_config != 'n':
                print()
                test_configuration()
    elif choice == '2':
        test_configuration()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()