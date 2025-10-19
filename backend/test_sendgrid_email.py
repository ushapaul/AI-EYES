"""
Test SendGrid Email Configuration
Quick test to verify SendGrid is working correctly
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("🧪 TESTING SENDGRID EMAIL CONFIGURATION")
print("=" * 70)

# Check environment variables
api_key = os.getenv('SENDGRID_API_KEY')
from_email = os.getenv('SENDGRID_FROM_EMAIL')
from_name = os.getenv('SENDGRID_FROM_NAME')
recipients = os.getenv('ALERT_RECIPIENTS')
enabled = os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'

print("\n📋 Configuration Check:")
print(f"   ✅ API Key: {'SET (' + api_key[:20] + '...)' if api_key else '❌ NOT SET'}")
print(f"   ✅ From Email: {from_email}")
print(f"   ✅ From Name: {from_name}")
print(f"   ✅ Recipients: {recipients}")
print(f"   ✅ Email Alerts Enabled: {enabled}")

if not api_key:
    print("\n❌ ERROR: SENDGRID_API_KEY not found in .env file")
    exit(1)

if not from_email:
    print("\n❌ ERROR: SENDGRID_FROM_EMAIL not found in .env file")
    exit(1)

# Try to import SendGrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
    import base64
    print("\n✅ SendGrid library imported successfully")
except ImportError as e:
    print(f"\n❌ ERROR: Failed to import SendGrid: {e}")
    print("   Run: pip install sendgrid")
    exit(1)

# Create test email
print("\n📧 Creating test email...")

# Create a simple test image (1x1 pixel PNG)
test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

message = Mail(
    from_email=from_email,
    to_emails=recipients.split(','),
    subject='🧪 AI Eyes Security System - Test Alert',
    html_content=f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🔍 AI Eyes Security System</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Test Email Alert</p>
        </div>
        
        <div style="background: white; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">✅ SendGrid Configuration Test</h2>
            
            <p style="color: #666; line-height: 1.6;">
                This is a test email from your AI Eyes Security System. If you're receiving this, 
                your SendGrid email configuration is working correctly!
            </p>
            
            <div style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0;">
                <strong style="color: #1e40af;">Configuration Details:</strong>
                <ul style="margin: 10px 0; color: #475569;">
                    <li><strong>From:</strong> {from_name} &lt;{from_email}&gt;</li>
                    <li><strong>To:</strong> {recipients}</li>
                    <li><strong>API Status:</strong> ✅ Connected</li>
                    <li><strong>Timestamp:</strong> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                </ul>
            </div>
            
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                <strong style="color: #92400e;">📌 Next Steps:</strong>
                <ol style="margin: 10px 0; color: #78350f;">
                    <li>Verify sender email in SendGrid dashboard</li>
                    <li>Add cameras to start surveillance</li>
                    <li>Test real alert notifications</li>
                </ol>
            </div>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                <p style="color: #999; font-size: 12px; margin: 0;">
                    AI Eyes Security System | Powered by SendGrid<br>
                    © 2025 All Rights Reserved
                </p>
            </div>
        </div>
    </body>
    </html>
    """
)

# Add test image attachment
attachment = Attachment()
attachment.file_content = FileContent(test_image_b64)
attachment.file_name = FileName("test_image.png")
attachment.file_type = FileType("image/png")
attachment.disposition = Disposition("attachment")
message.attachment = attachment

print("   ✅ Email message created")

# Send email
try:
    print("\n📤 Sending test email...")
    print(f"   From: {from_name} <{from_email}>")
    print(f"   To: {recipients}")
    
    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    
    print(f"\n✅ SUCCESS! Email sent successfully!")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.body}")
    print(f"\n📬 Check your inbox: {recipients}")
    print("\n⚠️ IMPORTANT:")
    print("   1. Check your spam/junk folder if you don't see the email")
    print("   2. Verify sender email in SendGrid dashboard:")
    print("      https://app.sendgrid.com/settings/sender_auth/senders")
    print("   3. If email is not received, verify the sender email address")
    
except Exception as e:
    print(f"\n❌ ERROR: Failed to send email")
    print(f"   Error: {str(e)}")
    
    if "403" in str(e) or "Forbidden" in str(e):
        print("\n⚠️ SENDER EMAIL NOT VERIFIED!")
        print("   Go to: https://app.sendgrid.com/settings/sender_auth/senders")
        print("   Click 'Verify a Single Sender'")
        print(f"   Enter: {from_email}")
        print("   Check your inbox and click the verification link")
    
    elif "401" in str(e) or "Unauthorized" in str(e):
        print("\n⚠️ INVALID API KEY!")
        print("   Go to: https://app.sendgrid.com/settings/api_keys")
        print("   Create a new API key with 'Mail Send' permissions")
        print("   Update SENDGRID_API_KEY in backend/.env")
    
    exit(1)

print("\n" + "=" * 70)
print("✅ SendGrid email test completed successfully!")
print("=" * 70)
