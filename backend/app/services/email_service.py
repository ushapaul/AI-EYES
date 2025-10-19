import os
import base64
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId
from config.settings import *

class EmailAlertService:
    def __init__(self):
        # SendGrid Configuration
        self.api_key = os.getenv('SENDGRID_API_KEY', 'your_sendgrid_api_key_here')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'alerts@yourdomain.com')
        self.from_name = os.getenv('SENDGRID_FROM_NAME', 'AI Eyes Security System')
        self.recipients = os.getenv('ALERT_RECIPIENTS', 'admin@yourdomain.com').split(',')
        self.enabled = os.getenv('ENABLE_EMAIL_ALERTS', 'true').lower() == 'true'
        
        # Initialize SendGrid client
        try:
            self.sg = SendGridAPIClient(api_key=self.api_key)
        except Exception as e:
            print(f"⚠️ SendGrid initialization failed: {e}")
            self.sg = None
        
        # Email templates with enhanced styling
        self.templates = {
            'intruder': {
                'subject': '🚨 SECURITY ALERT: Unauthorized Person Detected',
                'priority': 'Critical',
                'color': '#dc3545',
                'icon': '👤'
            },
            'suspicious_activity': {
                'subject': '⚠️ SECURITY ALERT: Suspicious Activity Detected',
                'priority': 'High',
                'color': '#fd7e14',
                'icon': '⚠️'
            },
            'weapon_detected': {
                'subject': '🚨 CRITICAL ALERT: Weapon Detected',
                'priority': 'Critical',
                'color': '#dc3545',
                'icon': '🔫'
            },
            'armed_threat': {
                'subject': '🚨 EMERGENCY: Armed Threat Detected',
                'priority': 'Critical',
                'color': '#dc3545',
                'icon': '🚨'
            },
            'multiple_persons': {
                'subject': '👥 ALERT: Multiple Persons Detected',
                'priority': 'High',
                'color': '#fd7e14',
                'icon': '👥'
            }
        }
    
    def send_alert(self, alert_data):
        """Send email alert using SendGrid with enhanced formatting"""
        if not self.enabled or not self.sg:
            print("📧 Email alerts disabled or SendGrid not configured")
            return False
        
        try:
            # Get template based on alert type
            template = self.templates.get(alert_data['type'], self.templates['suspicious_activity'])
            
            # Modify subject if escalated
            subject = template['subject']
            if alert_data.get('escalated'):
                escalated_to = alert_data.get('escalated_to', 'Authorized Person')
                subject = f"⚡ ESCALATED: {template['subject']} → {escalated_to}"
            
            # Create email content
            html_content = self._create_modern_html_body(alert_data, template)
            
            # Create Mail object
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=self.recipients,
                subject=subject,
                html_content=html_content
            )
            
            # Add image attachment if available
            if 'image_path' in alert_data and os.path.exists(alert_data['image_path']):
                self._add_image_attachment(message, alert_data['image_path'])
            
            # Send email
            response = self.sg.send(message)
            
            if response.status_code == 202:
                print(f"✅ Alert email sent successfully for {alert_data['type']}")
                return True
            else:
                print(f"❌ Failed to send email. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending SendGrid email alert: {e}")
            return False
    
    def _add_image_attachment(self, message, image_path):
        """Add image as attachment and inline content"""
        try:
            with open(image_path, 'rb') as f:
                data = f.read()
                encoded = base64.b64encode(data).decode()
            
            # Add as attachment
            attachment = Attachment()
            attachment.file_content = FileContent(encoded)
            attachment.file_type = FileType('image/jpeg')
            attachment.file_name = FileName('security_alert.jpg')
            attachment.disposition = Disposition('inline')
            attachment.content_id = ContentId('alert_image')
            
            message.attachment = attachment
            
        except Exception as e:
            print(f"⚠️ Error adding image attachment: {e}")
    
    def _create_modern_html_body(self, alert_data, template):
        """Create modern, responsive HTML email body"""
        
        # Format timestamp
        timestamp = alert_data.get('timestamp', datetime.now().isoformat())
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        # Get detection details
        raw_confidence = alert_data.get('confidence', 0)
        # Convert to percentage if needed (handle both 0.5 format and 50 format)
        confidence = raw_confidence * 100 if raw_confidence <= 1.0 else raw_confidence
        location = alert_data.get('location', 'Camera Feed')
        camera_id = alert_data.get('camera_id', alert_data.get('camera', 'Unknown'))
        description = alert_data.get('description', f"Unauthorized person detected in {location}")
        
        html_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Eyes Security Alert</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: #ffffff;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, {template['color']}, {template['color']}dd);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    position: relative;
                }}
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
                }}
                .header-content {{
                    position: relative;
                    z-index: 1;
                }}
                .header-icon {{
                    width: 80px;
                    height: 80px;
                    margin: 0 auto 15px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    backdrop-filter: blur(10px);
                }}
                .header-icon svg {{
                    width: 40px;
                    height: 40px;
                    fill: white;
                }}
                .header h1 {{
                    font-size: 28px;
                    font-weight: 700;
                    margin-bottom: 10px;
                }}
                .priority-badge {{
                    display: inline-block;
                    background: rgba(255,255,255,0.2);
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: 600;
                    backdrop-filter: blur(10px);
                }}
                .content {{
                    padding: 30px;
                }}
                .alert-summary {{
                    background: {template['color']}10;
                    border-left: 4px solid {template['color']};
                    padding: 20px;
                    margin-bottom: 25px;
                    border-radius: 0 8px 8px 0;
                }}
                .alert-title {{
                    font-size: 20px;
                    font-weight: 600;
                    color: {template['color']};
                    margin-bottom: 8px;
                }}
                .alert-description {{
                    color: #666;
                    font-size: 16px;
                }}
                .details-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin: 25px 0;
                }}
                .detail-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #e9ecef;
                }}
                .detail-label {{
                    font-size: 12px;
                    text-transform: uppercase;
                    font-weight: 600;
                    color: #666;
                    margin-bottom: 5px;
                    letter-spacing: 0.5px;
                }}
                .detail-value {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #333;
                }}
                .confidence-container {{
                    margin: 20px 0;
                }}
                .confidence-bar {{
                    background: #e9ecef;
                    height: 25px;
                    border-radius: 12px;
                    overflow: hidden;
                    position: relative;
                }}
                .confidence-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, {template['color']}, {template['color']}cc);
                    width: {confidence}%;
                    border-radius: 12px;
                    position: relative;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .confidence-text {{
                    color: white;
                    font-weight: 600;
                    font-size: 12px;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                }}
                .image-container {{
                    text-align: center;
                    margin: 25px 0;
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                }}
                .alert-image {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                }}
                .action-required {{
                    background: linear-gradient(135deg, #fff3cd, #ffeeba);
                    border: 1px solid #ffd700;
                    color: #856404;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 25px 0;
                }}
                .action-title {{
                    font-weight: 700;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 25px;
                    text-align: center;
                    border-top: 1px solid #e9ecef;
                }}
                .footer-brand {{
                    font-weight: 700;
                    color: {template['color']};
                    margin-bottom: 8px;
                }}
                .footer-details {{
                    font-size: 12px;
                    color: #666;
                    line-height: 1.4;
                }}
                .status-indicators {{
                    display: flex;
                    justify-content: center;
                    gap: 20px;
                    margin-top: 15px;
                }}
                .status-item {{
                    display: flex;
                    align-items: center;
                    font-size: 12px;
                    color: #666;
                }}
                .status-dot {{
                    width: 8px;
                    height: 8px;
                    background: #28a745;
                    border-radius: 50%;
                    margin-right: 6px;
                }}
                @media (max-width: 600px) {{
                    .email-container {{
                        margin: 10px;
                        border-radius: 10px;
                    }}
                    .header {{
                        padding: 20px;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                    .details-grid {{
                        grid-template-columns: 1fr;
                        gap: 15px;
                    }}
                    .status-indicators {{
                        flex-direction: column;
                        gap: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="header-content">
                        <div class="header-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                <path d="M12 2L4 6v6c0 5.5 3.8 10.7 8 12 4.2-1.3 8-6.5 8-12V6l-8-4zm0 2.2l6 3V12c0 4.5-3.1 8.9-6 10.2-2.9-1.3-6-5.7-6-10.2V7.2l6-3zM12 7c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 2c1.7 0 3 1.3 3 3s-1.3 3-3 3-3-1.3-3-3 1.3-3 3-3z"/>
                            </svg>
                        </div>
                        <h1>{template['icon']} AI Eyes Security</h1>
                        <div class="priority-badge">{template['priority']} Priority Alert</div>
                    </div>
                </div>
                
                <div class="content">"""
        
        # Add escalation banner if this alert was manually escalated
        if alert_data.get('escalated'):
            escalated_to = alert_data.get('escalated_to', 'Authorized Person')
            escalated_by = alert_data.get('escalated_by', 'Security Team')
            html_body += f"""
                    <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 20px; margin-bottom: 20px; border-radius: 10px; border-left: 5px solid #b45309;">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <div style="font-size: 40px;">⚡</div>
                            <div>
                                <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">
                                    🔔 ESCALATED ALERT
                                </div>
                                <div style="font-size: 14px; opacity: 0.95;">
                                    This alert was <strong>manually escalated</strong> to you (<strong>{escalated_to}</strong>) by {escalated_by} via the Security Dashboard.
                                    <br>
                                    This indicates the situation requires <strong>immediate attention</strong> from authorized personnel.
                                </div>
                            </div>
                        </div>
                    </div>
"""
        
        html_body += f"""
                    <div class="alert-summary">
                        <div class="alert-title">{description}</div>
                        <div class="alert-description">
                            {"This security event was escalated for your immediate attention." if alert_data.get('escalated') else "Automated detection system has identified a security event requiring attention."}
                        </div>
                    </div>
                    
                    <div class="details-grid">
                        <div class="detail-card">
                            <div class="detail-label">Alert Type</div>
                            <div class="detail-value">{alert_data['type'].replace('_', ' ').title()}</div>
                        </div>
                        <div class="detail-card">
                            <div class="detail-label">Location</div>
                            <div class="detail-value">{location}</div>
                        </div>
                        <div class="detail-card">
                            <div class="detail-label">Timestamp</div>
                            <div class="detail-value">{formatted_time}</div>
                        </div>
                        <div class="detail-card">
                            <div class="detail-label">Camera ID</div>
                            <div class="detail-value">{camera_id}</div>
                        </div>
                    </div>
                    
                    <div class="confidence-container">
                        <div class="detail-label">Detection Confidence</div>
                        <div class="confidence-bar">
                            <div class="confidence-fill">
                                <span class="confidence-text">{confidence:.1f}%</span>
                            </div>
                        </div>
                    </div>
                    
                    {"<div class='image-container'><img src='cid:alert_image' alt='Security Alert Image' class='alert-image' /></div>" if 'image_path' in alert_data else ""}
                    
                    <div class="action-required">
                        <div class="action-title">
                            ⚠️ Immediate Action Required
                        </div>
                        <div>
                            Please review the security footage and assess the situation. If this represents a genuine threat, 
                            contact security personnel or authorities immediately. This alert was generated by AI analysis 
                            and should be verified by human assessment.
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="footer-brand">AI Eyes Security System</div>
                    <div class="footer-details">
                        Powered by Advanced Computer Vision & Deep Learning<br>
                        Real-time Intelligent Surveillance & Threat Detection
                    </div>
                    <div class="status-indicators">
                        <div class="status-item">
                            <div class="status-dot"></div>
                            System Active
                        </div>
                        <div class="status-item">
                            <div class="status-dot"></div>
                            AI Detection Online
                        </div>
                        <div class="status-item">
                            <div class="status-dot"></div>
                            Alert ID: {alert_data.get('id', 'N/A')}
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def send_test_alert(self):
        """Send a test alert using SendGrid to verify email configuration"""
        if not self.enabled or not self.sg:
            print("📧 Email alerts disabled or SendGrid not configured")
            return False
        
        test_alert = {
            'type': 'system_test',
            'description': 'AI Eyes Security System Test Alert',
            'location': 'System Configuration',
            'timestamp': datetime.now().isoformat(),
            'confidence': 100,
            'camera_id': 'TEST',
            'id': 'TEST-001'
        }
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; }}
                    .success-icon {{ font-size: 48px; margin-bottom: 15px; }}
                    .status-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }}
                    .status-item {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
                    .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="success-icon">✅</div>
                        <h1>AI Eyes Security System</h1>
                        <p>Email Configuration Test Successful</p>
                    </div>
                    <div class="content">
                        <h2>🎉 SendGrid Integration Working!</h2>
                        <p>This test email confirms that your AI Eyes Security System is successfully configured with SendGrid email alerts.</p>
                        
                        <div class="status-grid">
                            <div class="status-item">
                                <strong>✅ SendGrid API</strong><br>
                                <small>Connected Successfully</small>
                            </div>
                            <div class="status-item">
                                <strong>✅ Email Alerts</strong><br>
                                <small>Ready to Send</small>
                            </div>
                        </div>
                        
                        <p><strong>Test Details:</strong></p>
                        <ul>
                            <li><strong>Service:</strong> SendGrid Email API</li>
                            <li><strong>From:</strong> {self.from_name} &lt;{self.from_email}&gt;</li>
                            <li><strong>Recipients:</strong> {len(self.recipients)} configured</li>
                            <li><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>AI Eyes Security System • Powered by SendGrid<br>
                        Next-Generation Intelligent Surveillance</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=self.recipients,
                subject='✅ AI Eyes Security - SendGrid Test Successful',
                html_content=html_content
            )
            
            response = self.sg.send(message)
            
            if response.status_code == 202:
                print("✅ SendGrid test email sent successfully!")
                return True
            else:
                print(f"❌ Failed to send test email. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending SendGrid test email: {e}")
            return False
    
    def add_recipient(self, email):
        """Add new email recipient"""
        if email not in self.recipients:
            self.recipients.append(email)
            return True
        return False
    
    def remove_recipient(self, email):
        """Remove email recipient"""
        if email in self.recipients:
            self.recipients.remove(email)
            return True
        return False
    
    def get_configuration_status(self):
        """Get current email service configuration status"""
        return {
            'service': 'SendGrid',
            'enabled': self.enabled,
            'configured': self.sg is not None,
            'api_key_set': bool(self.api_key and self.api_key != 'your_sendgrid_api_key_here'),
            'from_email': self.from_email,
            'from_name': self.from_name,
            'recipients_count': len(self.recipients),
            'recipients': self.recipients if len(self.recipients) <= 3 else self.recipients[:3] + ['...']
        }