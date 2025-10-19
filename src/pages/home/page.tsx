
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();
  const [showDemoModal, setShowDemoModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(180); // 3 minutes demo
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [showSubtitles, setShowSubtitles] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [uploadedVideo, setUploadedVideo] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoMetadata, setVideoMetadata] = useState({
    title: '',
    description: '',
    duration: 0,
    size: 0
  });

  // Demo video segments with timestamps and subtitles
  const demoSegments = [
    {
      start: 0,
      end: 15,
      title: "Welcome to AI Eyes Security",
      subtitle: "Welcome to AI Eyes Security System - the most advanced AI-powered surveillance solution for farms and banks.",
      scene: "intro"
    },
    {
      start: 15,
      end: 35,
      title: "Dashboard Overview",
      subtitle: "Our comprehensive dashboard provides real-time monitoring with live camera feeds and instant alerts.",
      scene: "dashboard"
    },
    {
      start: 35,
      end: 55,
      title: "Live Camera Feeds",
      subtitle: "Monitor multiple locations simultaneously with HD video streams from IP cameras and mobile devices.",
      scene: "cameras"
    },
    {
      start: 55,
      end: 75,
      title: "AI Detection in Action",
      subtitle: "Watch as our MobileNetV2 Face Recognition and YOLOv9 models detect intruders and suspicious activities in real-time.",
      scene: "detection"
    },
    {
      start: 75,
      end: 95,
      title: "Instant Alert System",
      subtitle: "When threats are detected, the system immediately sends alerts with snapshots and detailed information.",
      scene: "alerts"
    },
    {
      start: 95,
      end: 115,
      title: "Security Management",
      subtitle: "Manage camera settings, configure AI models, and customize alert preferences from one central location.",
      scene: "settings"
    },
    {
      start: 115,
      end: 135,
      title: "Event Logs & Reports",
      subtitle: "Access detailed logs of all security events with filtering, search, and export capabilities.",
      scene: "logs"
    },
    {
      start: 135,
      end: 155,
      title: "Mobile Compatibility",
      subtitle: "Access your security system from any device - desktop, tablet, or smartphone with responsive design.",
      scene: "mobile"
    },
    {
      start: 155,
      end: 180,
      title: "Get Started Today",
      subtitle: "Ready to protect your property? Sign up now and experience the future of AI-powered security.",
      scene: "cta"
    }
  ];

  const getCurrentSegment = () => {
    return demoSegments.find(segment => currentTime >= segment.start && currentTime < segment.end) || demoSegments[0];
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (newTime: number) => {
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const toggleSubtitles = () => {
    setShowSubtitles(!showSubtitles);
  };

  const changePlaybackSpeed = (speed: number) => {
    setPlaybackSpeed(speed);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('video/')) {
        setUploadError('Please select a valid video file');
        return;
      }

      // Validate file size (max 500MB)
      if (file.size > 500 * 1024 * 1024) {
        setUploadError('Video file size must be less than 500MB');
        return;
      }

      setVideoFile(file);
      setUploadError('');

      // Get video metadata
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.onloadedmetadata = () => {
        setVideoMetadata({
          title: file.name.replace(/\.[^/.]+$/, ''),
          description: '',
          duration: video.duration,
          size: file.size
        });
        setDuration(video.duration);
      };
      video.src = URL.createObjectURL(file);
    }
  };

  const handleVideoUpload = async () => {
    if (!videoFile) return;

    setIsUploading(true);
    setUploadProgress(0);
    setUploadError('');

    try {
      // Simulate upload progress
      const uploadInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 95) {
            clearInterval(uploadInterval);
            return 95;
          }
          return prev + Math.random() * 10;
        });
      }, 200);

      // Create video URL for preview
      const videoUrl = URL.createObjectURL(videoFile);
      
      // Simulate upload completion after 3 seconds
      setTimeout(() => {
        clearInterval(uploadInterval);
        setUploadProgress(100);
        setUploadedVideo(videoUrl);
        setIsUploading(false);
        setShowUploadModal(false);
        
        // Show success message
        setTimeout(() => {
          alert('Video uploaded successfully! You can now use your custom demo video.');
        }, 500);
      }, 3000);

    } catch (error) {
      setIsUploading(false);
      setUploadError('Upload failed. Please try again.');
      console.error('Upload error:', error);
    }
  };

  const removeUploadedVideo = () => {
    if (uploadedVideo) {
      URL.revokeObjectURL(uploadedVideo);
    }
    setUploadedVideo(null);
    setVideoFile(null);
    setVideoMetadata({
      title: '',
      description: '',
      duration: 0,
      size: 0
    });
    setDuration(180); // Reset to default demo duration
    setCurrentTime(0);
    setIsPlaying(false);
  };

  const getSceneImage = (scene: string) => {
    const sceneImages = {
      intro: 'https://readdy.ai/api/search-image?query=AI%20Eyes%20Security%20System%20logo%20animation%20with%20modern%20tech%20background%2C%20professional%20security%20branding%2C%20futuristic%20surveillance%20technology%20introduction&width=800&height=450&seq=demo1&orientation=landscape',
      dashboard: 'https://readdy.ai/api/search-image?query=comprehensive%20security%20dashboard%20interface%20with%20multiple%20camera%20feeds%2C%20real-time%20monitoring%20system%2C%20professional%20surveillance%20control%20center&width=800&height=450&seq=demo2&orientation=landscape',
      cameras: 'https://readdy.ai/api/search-image?query=multiple%20live%20camera%20feeds%20showing%20farm%20and%20bank%20locations%2C%20HD%20video%20streams%2C%20professional%20surveillance%20monitoring%20grid%20layout&width=800&height=450&seq=demo3&orientation=landscape',
      detection: 'https://readdy.ai/api/search-image?query=AI%20detection%20system%20in%20action%20with%20person%20detection%20overlay%2C%20face%20recognition%20technology%2C%20real-time%20threat%20identification%20with%20bounding%20boxes&width=800&height=450&seq=demo4&orientation=landscape',
      alerts: 'https://readdy.ai/api/search-image?query=security%20alert%20notification%20system%20with%20red%20warning%20indicators%2C%20instant%20alert%20popup%20with%20threat%20details%2C%20emergency%20response%20interface&width=800&height=450&seq=demo5&orientation=landscape',
      settings: 'https://readdy.ai/api/search-image?query=security%20system%20configuration%20panel%20with%20camera%20settings%2C%20AI%20model%20options%2C%20professional%20admin%20interface%20for%20surveillance%20management&width=800&height=450&seq=demo6&orientation=landscape',
      logs: 'https://readdy.ai/api/search-image?query=detailed%20security%20event%20logs%20table%20with%20timestamps%2C%20filtering%20options%2C%20professional%20data%20management%20interface%20for%20surveillance%20records&width=800&height=450&seq=demo7&orientation=landscape',
      mobile: 'https://readdy.ai/api/search-image?query=responsive%20security%20system%20interface%20on%20mobile%20devices%2C%20smartphone%20and%20tablet%20surveillance%20monitoring%2C%20mobile-friendly%20dashboard%20design&width=800&height=450&seq=demo8&orientation=landscape',
      cta: 'https://readdy.ai/api/search-image?query=call%20to%20action%20screen%20with%20get%20started%20button%2C%20professional%20security%20system%20signup%20interface%2C%20modern%20tech%20company%20landing%20page&width=800&height=450&seq=demo9&orientation=landscape'
    };
    return sceneImages[scene as keyof typeof sceneImages] || sceneImages.intro;
  };

  // Simulate video playback
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying && showDemoModal) {
      interval = setInterval(() => {
        setCurrentTime(prev => {
          if (prev >= duration) {
            setIsPlaying(false);
            return duration;
          }
          return prev + playbackSpeed;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, showDemoModal, playbackSpeed, duration]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDownloadDocumentation = () => {
    // Generate comprehensive documentation
    const documentation = `
# AI Eyes Security System - Complete Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Installation Guide](#installation-guide)
3. [Getting Started](#getting-started)
4. [Dashboard Features](#dashboard-features)
5. [Camera Setup](#camera-setup)
6. [AI Detection Models](#ai-detection-models)
7. [Alert Configuration](#alert-configuration)
8. [User Management](#user-management)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)
11. [Support](#support)

---

## System Overview

AI Eyes Security System is an advanced surveillance solution that uses artificial intelligence to detect intruders and suspicious activities in real-time. The system is designed for:

- **Farm Security**: Protect agricultural areas from unauthorized access
- **Bank Security**: Monitor banking facilities for suspicious activities
- **General Surveillance**: Adapt to various security scenarios

### Key Features
- ✅ MobileNetV2 Face Recognition for intruder detection
- ✅ YOLOv9 Activity Detection for suspicious behavior analysis
- ✅ Real-time alerts with email notifications
- ✅ Multi-camera support (IP cameras, webcams, mobile devices)
- ✅ Web-based dashboard for monitoring and management
- ✅ Event logging with filtering and export capabilities
- ✅ Secure user authentication and access control

---

## Installation Guide

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux Ubuntu 18.04+
- **Hardware**: 
  - CPU: Intel i5 or AMD Ryzen 5 (minimum)
  - RAM: 8GB (16GB recommended)
  - Storage: 50GB free space
  - GPU: NVIDIA GTX 1050+ (optional, for better performance)
- **Network**: Stable internet connection for alerts and updates
- **Cameras**: IP cameras, USB webcams, or mobile devices with camera access

### Quick Installation
1. **Download the System**
   - Visit our official website
   - Download the installer for your operating system
   - Run the installer as administrator

2. **Initial Setup**
   - Launch AI Eyes Security System
   - Complete the setup wizard
   - Create your admin account
   - Configure network settings

3. **Camera Connection**
   - Connect IP cameras to your network
   - Add camera sources in the dashboard
   - Test camera feeds and detection

---

## Getting Started

### First Login
1. Open your web browser and navigate to: \`http://localhost:8080\`
2. Login with your admin credentials
3. Complete the initial system configuration

### Quick Start Checklist
- [ ] Add at least one camera source
- [ ] Configure detection zones
- [ ] Set up email notifications
- [ ] Test alert system
- [ ] Review security settings

---

## Dashboard Features

### Live Camera Feeds
- **Multi-camera View**: Monitor up to 16 cameras simultaneously
- **Full-screen Mode**: Focus on individual camera feeds
- **Recording Controls**: Start/stop recording with one click
- **Snapshot Capture**: Take instant screenshots of events

### Real-time Alerts
- **Instant Notifications**: Immediate alerts when threats are detected
- **Alert Details**: Comprehensive information including location, time, and confidence level
- **Quick Actions**: Dismiss, escalate, or export alerts directly from the interface

### Event Logs
- **Comprehensive Logging**: All security events are automatically logged
- **Advanced Filtering**: Filter by date, location, event type, and severity
- **Export Options**: Export logs in CSV, PDF, or JSON formats
- **Search Functionality**: Quick search through historical events

---

## Camera Setup

### Supported Camera Types
1. **IP Cameras**
   - RTSP/HTTP streams
   - Most major brands supported (Hikvision, Dahua, Axis, etc.)
   - Configuration via web interface

2. **USB Webcams**
   - Plug-and-play compatibility
   - Automatic detection and configuration
   - Resolution and frame rate adjustment

3. **Mobile Devices**
   - Use smartphones as security cameras
   - Remote monitoring capabilities
   - WiFi and cellular connectivity

### Adding Cameras
1. **Navigate to Camera Management**
   - Go to Dashboard → Live Streams
   - Click "Add Camera" button

2. **Configure Camera Settings**
   - Enter camera name and location
   - Provide IP address (for IP cameras)
   - Select AI detection model
   - Test connection

3. **Position and Calibrate**
   - Adjust camera angles for optimal coverage
   - Define detection zones
   - Set sensitivity levels

---

## AI Detection Models

### MobileNetV2 Face Recognition
**Use Case**: Intruder detection in farm areas

**Features**:
- Recognizes known vs unknown faces
- High accuracy (95%+) in various lighting conditions
- Fast processing (< 0.5 seconds per frame)
- Privacy-focused (no cloud processing)

**Configuration**:
- Training data: Upload photos of authorized personnel
- Sensitivity: Adjust detection threshold
- Alert triggers: Configure when to send notifications

### YOLOv9 Activity Detection
**Use Case**: Suspicious activity monitoring in banks

**Features**:
- Real-time object and activity detection
- Behavior analysis and pattern recognition
- Multi-class detection (person, vehicle, weapon, etc.)
- Advanced anomaly detection

**Configuration**:
- Activity zones: Define areas to monitor
- Behavior patterns: Set normal vs suspicious activities
- Time-based rules: Different settings for business hours

---

## Alert Configuration

### Email Notifications
1. **SMTP Setup**
   - Configure email server settings
   - Test email delivery
   - Set up multiple recipients

2. **Alert Templates**
   - Customize email content
   - Include snapshots and location data
   - Set urgency levels and response protocols

### SMS Alerts (Premium Feature)
- Instant text message notifications
- Critical alert escalation
- Multiple phone number support

### Push Notifications
- Real-time mobile notifications
- Cross-platform compatibility
- Customizable alert sounds

---

## User Management

### User Roles
1. **Administrator**
   - Full system access
   - User management capabilities
   - System configuration rights

2. **Security Officer**
   - Monitor live feeds
   - Manage alerts and events
   - Generate reports

3. **Viewer**
   - View-only access
   - Live feed monitoring
   - Limited alert visibility

### Adding Users
1. Navigate to Settings → User Management
2. Click "Add New User"
3. Fill in user details and assign role
4. Send login credentials securely

---

## API Reference

### Authentication
\`\`\`
POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
\`\`\`

### Camera Management
\`\`\`
GET /api/cameras
Authorization: Bearer <token>

Response: List of all cameras with status
\`\`\`

### Alert System
\`\`\`
POST /api/alerts
Authorization: Bearer <token>

{
  "camera_id": 1,
  "event_type": "intruder_detected",
  "confidence": 0.95,
  "timestamp": "2024-01-15T10:30:00Z"
}
\`\`\`

### Event Logs
\`\`\`
GET /api/logs?date_from=2024-01-01&date_to=2024-01-31
Authorization: Bearer <token>

Response: Filtered list of security events
\`\`\`

---

## Troubleshooting

### Common Issues

**Camera Not Connecting**
- Check network connectivity
- Verify IP address and port
- Ensure camera is powered on
- Test with camera manufacturer's software

**AI Detection Not Working**
- Verify camera positioning and lighting
- Check detection sensitivity settings
- Ensure adequate processing power
- Update AI models if available

**Alerts Not Sending**
- Test email server configuration
- Check internet connectivity
- Verify recipient email addresses
- Review alert trigger settings

**Performance Issues**
- Monitor CPU and memory usage
- Reduce camera resolution if needed
- Close unnecessary applications
- Consider hardware upgrade

### Log Files
System logs are located at:
- Windows: \`C:\\ProgramData\\AIEyes\\logs\`
- macOS: \`/Library/Application Support/AIEyes/logs\`
- Linux: \`/var/log/aieyes/\`

---

## Support

### Getting Help
- **Email Support**: support@aieyes-security.com
- **Knowledge Base**: https://docs.aieyes-security.com
- **Community Forum**: https://community.aieyes-security.com
- **Video Tutorials**: https://youtube.com/aieyes-security

### Contact Information
- **Technical Support**: Available 24/7
- **Sales Inquiries**: sales@aieyes-security.com
- **Partnership Opportunities**: partners@aieyes-security.com

### System Updates
- Automatic updates are enabled by default
- Manual update check: Settings → System → Check for Updates
- Release notes available at: https://releases.aieyes-security.com

---

## Appendix

### Supported Camera Brands
- Hikvision
- Dahua Technology
- Axis Communications
- Bosch Security
- Hanwha Techwin
- FLIR Systems
- Uniview
- Generic ONVIF cameras

### Technical Specifications
- **Maximum Cameras**: 64 per system
- **Recording Resolution**: Up to 4K (3840x2160)
- **Frame Rate**: Up to 60 FPS per camera
- **Storage**: Local and cloud options available
- **Bandwidth**: Optimized for low-bandwidth environments

### License Information
AI Eyes Security System is proprietary software. See license agreement for full terms and conditions.

---

**Document Version**: 2.1
**Last Updated**: ${new Date().toLocaleDateString()}
**System Version**: 2.5.0

For the most up-to-date documentation, visit: https://docs.aieyes-security.com
`;

    // Create and download the documentation file
    const blob = new Blob([documentation], { type: 'text/markdown' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `AI_Eyes_Security_Documentation_v2.1_${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    // Show success notification
    setTimeout(() => {
      alert(`📚 Documentation Downloaded Successfully!

✅ File: AI_Eyes_Security_Documentation_v2.1_${new Date().toISOString().split('T')[0]}.md
✅ Size: ~${Math.round(blob.size / 1024)} KB
✅ Format: Markdown (.md)

The complete documentation includes:
• Installation and setup guides
• Camera configuration instructions
• AI detection model details
• API reference and troubleshooting
• User management and security settings

You can view this file with any text editor or Markdown viewer.`);
    }, 500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="w-full h-full bg-repeat" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.3'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
      </div>
      
      <div className="relative z-10">
        {/* Header - Mobile Responsive */}
        <header className="px-4 sm:px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                <i className="ri-eye-line text-white text-lg sm:text-xl"></i>
              </div>
              <h1 className="text-lg sm:text-xl font-bold text-white">AI Eyes Security</h1>
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <button
                onClick={() => navigate('/login')}
                className="px-3 sm:px-4 py-2 border border-gray-400 text-white rounded-lg hover:bg-white/10 transition-colors whitespace-nowrap text-sm sm:text-base"
              >
                <i className="ri-login-box-line mr-1 sm:mr-2"></i>
                Login
              </button>
              <button
                onClick={() => navigate('/signup')}
                className="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors whitespace-nowrap text-sm sm:text-base"
              >
                <i className="ri-user-add-line mr-1 sm:mr-2"></i>
                Sign Up
              </button>
            </div>
          </div>
        </header>

        {/* Hero Section - Mobile Responsive */}
        <div className="px-4 sm:px-6 py-10 sm:py-20">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
              <div className="text-white order-2 lg:order-1">
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 sm:mb-6 leading-tight">
                  Smart Surveillance with
                  <span className="text-blue-400"> AI-Powered Detection</span>
                </h1>
                <p className="text-lg sm:text-xl text-gray-300 mb-6 sm:mb-8 leading-relaxed">
                  Advanced security system using Deep Learning for real-time intruder detection, 
                  suspicious activity monitoring, and instant alerts. Protect your farm and bank 
                  with cutting-edge AI technology.
                </p>
                <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                  <button
                    onClick={() => navigate('/dashboard')}
                    className="px-6 sm:px-8 py-3 sm:py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold whitespace-nowrap text-sm sm:text-base"
                  >
                    <i className="ri-dashboard-line mr-2"></i>
                    View Dashboard
                  </button>
                  <button 
                    onClick={() => setShowDemoModal(true)}
                    className="px-6 sm:px-8 py-3 sm:py-4 border border-gray-400 text-white rounded-lg hover:bg-white/10 transition-colors font-semibold whitespace-nowrap text-sm sm:text-base"
                  >
                    <i className="ri-play-circle-line mr-2"></i>
                    Watch Demo
                  </button>
                </div>
                
                {/* Video Management Section - Mobile Responsive */}
                <div className="mt-6 sm:mt-8 p-3 sm:p-4 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-base sm:text-lg font-semibold text-white">Demo Video</h3>
                    <div className="flex items-center space-x-2">
                      {uploadedVideo ? (
                        <span className="text-green-400 text-xs sm:text-sm flex items-center">
                          <i className="ri-check-circle-line mr-1"></i>
                          <span className="hidden sm:inline">Custom Video Active</span>
                          <span className="sm:hidden">Custom</span>
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs sm:text-sm flex items-center">
                          <i className="ri-image-line mr-1"></i>
                          <span className="hidden sm:inline">Using Default Demo</span>
                          <span className="sm:hidden">Default</span>
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
                    <button
                      onClick={() => setShowUploadModal(true)}
                      className="px-3 sm:px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium whitespace-nowrap text-xs sm:text-sm"
                    >
                      <i className="ri-upload-cloud-line mr-1 sm:mr-2"></i>
                      <span className="hidden sm:inline">Upload Your Video</span>
                      <span className="sm:hidden">Upload Video</span>
                    </button>
                    
                    {uploadedVideo && (
                      <button
                        onClick={removeUploadedVideo}
                        className="px-3 sm:px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium whitespace-nowrap text-xs sm:text-sm"
                      >
                        <i className="ri-delete-bin-line mr-1 sm:mr-2"></i>
                        <span className="hidden sm:inline">Remove Custom Video</span>
                        <span className="sm:hidden">Remove</span>
                      </button>
                    )}
                  </div>
                  
                  {uploadedVideo && videoMetadata.title && (
                    <div className="mt-3 text-xs sm:text-sm text-gray-300">
                      <p><strong>Title:</strong> {videoMetadata.title}</p>
                      <p><strong>Duration:</strong> {formatTime(videoMetadata.duration)}</p>
                      <p><strong>Size:</strong> {formatFileSize(videoMetadata.size)}</p>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="relative order-1 lg:order-2">
                <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-2xl p-4 sm:p-8 backdrop-blur-sm border border-white/10">
                  <img
                    src="https://readdy.ai/api/search-image?query=modern%20AI%20surveillance%20security%20system%20dashboard%20with%20multiple%20camera%20feeds%20showing%20farm%20and%20bank%20monitoring%2C%20futuristic%20technology%20interface%20with%20detection%20overlays%2C%20professional%20security%20control%20room%20setup&width=600&height=400&seq=hero1&orientation=landscape"
                    alt="AI Security Dashboard"
                    className="w-full h-48 sm:h-64 lg:h-80 object-cover rounded-xl"
                  />
                  <div className="absolute -top-2 -right-2 sm:-top-4 sm:-right-4 bg-green-500 text-white px-2 sm:px-4 py-1 sm:py-2 rounded-lg font-semibold text-xs sm:text-sm">
                    <i className="ri-shield-check-line mr-1 sm:mr-2"></i>
                    99.8% Uptime
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Upload Modal - Mobile Responsive */}
        {showUploadModal && (
          <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="p-4 sm:p-6">
                <div className="flex items-center justify-between mb-4 sm:mb-6">
                  <div className="flex items-center">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 rounded-lg flex items-center justify-center mr-3 sm:mr-4">
                      <i className="ri-upload-cloud-line text-xl sm:text-2xl text-green-600"></i>
                    </div>
                    <div>
                      <h3 className="text-lg sm:text-xl font-bold text-gray-900">Upload Demo Video</h3>
                      <p className="text-xs sm:text-sm text-gray-600">Upload your own AI Eyes Security System demo video</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setShowUploadModal(false)}
                    className="text-gray-400 hover:text-gray-600 p-1"
                  >
                    <i className="ri-close-line text-xl sm:text-2xl"></i>
                  </button>
                </div>

                {/* Upload Guidelines - Mobile Responsive */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 sm:p-4 mb-4 sm:mb-6">
                  <div className="flex items-center mb-2 sm:mb-3">
                    <i className="ri-information-line text-blue-600 mr-2"></i>
                    <h4 className="font-medium text-blue-800 text-sm sm:text-base">Video Guidelines</h4>
                  </div>
                  <div className="text-xs sm:text-sm text-blue-700 space-y-2">
                    <p><strong>Recommended Content for Your AI Security Demo:</strong></p>
                    <ul className="list-disc list-inside space-y-1 ml-2 sm:ml-4">
                      <li>Screen recording of your actual AI Eyes Security dashboard</li>
                      <li>Live camera feeds showing detection in action</li>
                      <li>Alert system demonstrations</li>
                      <li>Face recognition and activity detection examples</li>
                      <li>Mobile app usage and responsiveness</li>
                    </ul>
                    <p className="mt-3"><strong>Technical Requirements:</strong></p>
                    <ul className="list-disc list-inside space-y-1 ml-2 sm:ml-4">
                      <li>Format: MP4, WebM, AVI, MOV</li>
                      <li>Maximum size: 500MB</li>
                      <li>Recommended resolution: 1920x1080 (Full HD)</li>
                      <li>Duration: 1-10 minutes optimal</li>
                    </ul>
                  </div>
                </div>

                {/* Upload Area - Mobile Responsive */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 sm:p-8 text-center mb-4 sm:mb-6">
                  {!videoFile ? (
                    <div>
                      <i className="ri-video-line text-4xl sm:text-6xl text-gray-400 mb-2 sm:mb-4"></i>
                      <h4 className="text-base sm:text-lg font-medium text-gray-900 mb-2">Select Your Demo Video</h4>
                      <p className="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4">Drag and drop your video file here, or click to browse</p>
                      <input
                        type="file"
                        accept="video/*"
                        onChange={handleFileSelect}
                        className="hidden"
                        id="video-upload"
                      />
                      <label
                        htmlFor="video-upload"
                        className="px-4 sm:px-6 py-2 sm:py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer inline-block whitespace-nowrap text-sm sm:text-base"
                      >
                        <i className="ri-folder-open-line mr-1 sm:mr-2"></i>
                        Choose Video File
                      </label>
                    </div>
                  ) : (
                    <div>
                      <i className="ri-video-fill text-4xl sm:text-6xl text-green-600 mb-2 sm:mb-4"></i>
                      <h4 className="text-base sm:text-lg font-medium text-gray-900 mb-2">Video Selected</h4>
                      <p className="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4 break-all">{videoFile.name}</p>
                      <div className="bg-gray-100 rounded-lg p-3 sm:p-4 text-left max-w-md mx-auto">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4 text-xs sm:text-sm">
                          <div>
                            <span className="text-gray-600">Size:</span>
                            <span className="ml-2 font-medium">{formatFileSize(videoFile.size)}</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Type:</span>
                            <span className="ml-2 font-medium">{videoFile.type}</span>
                          </div>
                          {videoMetadata.duration > 0 && (
                            <>
                              <div>
                                <span className="text-gray-600">Duration:</span>
                                <span className="ml-2 font-medium">{formatTime(videoMetadata.duration)}</span>
                              </div>
                              <div>
                                <span className="text-gray-600">Status:</span>
                                <span className="ml-2 font-medium text-green-600">Ready to Upload</span>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          setVideoFile(null);
                          setVideoMetadata({
                            title: '',
                            description: '',
                            duration: 0,
                            size: 0
                          });
                        }}
                        className="mt-3 sm:mt-4 text-red-600 hover:text-red-800 text-xs sm:text-sm"
                      >
                        <i className="ri-delete-bin-line mr-1"></i>
                        Remove File
                      </button>
                    </div>
                  )}
                </div>

                {/* Video Metadata - Mobile Responsive */}
                {videoFile && (
                  <div className="space-y-3 sm:space-y-4 mb-4 sm:mb-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Video Title</label>
                      <input
                        type="text"
                        value={videoMetadata.title}
                        onChange={(e) => setVideoMetadata({...videoMetadata, title: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        placeholder="Enter a title for your demo video"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Description (Optional)</label>
                      <textarea
                        value={videoMetadata.description}
                        onChange={(e) => setVideoMetadata({...videoMetadata, description: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        rows={3}
                        placeholder="Describe what your demo video shows..."
                      />
                    </div>
                  </div>
                )}

                {/* Upload Progress - Mobile Responsive */}
                {isUploading && (
                  <div className="mb-4 sm:mb-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Uploading...</span>
                      <span className="text-sm text-gray-600">{Math.round(uploadProgress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Error Message */}
                {uploadError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 sm:p-4 mb-4 sm:mb-6">
                    <div className="flex items-center">
                      <i className="ri-error-warning-line text-red-600 mr-2"></i>
                      <span className="text-red-800 text-sm">{uploadError}</span>
                    </div>
                  </div>
                )}

                {/* Video Creation Tips - Mobile Responsive */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 sm:p-4 mb-4 sm:mb-6">
                  <div className="flex items-center mb-2 sm:mb-3">
                    <i className="ri-lightbulb-line text-yellow-600 mr-2"></i>
                    <h4 className="font-medium text-yellow-800 text-sm sm:text-base">Don't Have a Video Yet? Here’s How to Create One:</h4>
                  </div>
                  <div className="text-xs sm:text-sm text-yellow-700 space-y-2">
                    <p><strong>Option 1: Screen Recording</strong></p>
                    <ul className="list-disc list-inside space-y-1 ml-2 sm:ml-4">
                      <li>Use OBS Studio, Camtasia, or built-in screen recording</li>
                      <li>Record your AI Eyes Security dashboard in action</li>
                      <li>Show live camera feeds and detection features</li>
                      <li>Demonstrate alert notifications and responses</li>
                    </ul>
                    <p className="mt-3"><strong>Option 2: Mobile Recording</strong></p>
                    <ul className="list-disc list-inside space-y-1 ml-2 sm:ml-4">
                      <li>Record your security system setup with a phone</li>
                      <li>Show cameras detecting movement or faces</li>
                      <li>Capture the dashboard responding to real events</li>
                      <li>Include mobile app usage demonstrations</li>
                    </ul>
                    <p className="mt-3"><strong>Option 3: Presentation Style</strong></p>
                    <ul className="list-disc list-inside space-y-1 ml-2 sm:ml-4">
                      <li>Create slides explaining your AI security features</li>
                      <li>Add voiceover explaining the technology</li>
                      <li>Include screenshots of your actual system</li>
                      <li>Show before/after security improvements</li>
                    </ul>
                  </div>
                </div>

                {/* Action Buttons - Mobile Responsive */}
                <div className="flex flex-col sm:flex-row justify-between items-center pt-4 sm:pt-6 border-t border-gray-200 gap-3 sm:gap-0">
                  <button
                    onClick={() => setShowUploadModal(false)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap text-sm sm:text-base order-2 sm:order-1"
                  >
                    Cancel
                  </button>
                  <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 order-1 sm:order-2">
                    {videoFile && !isUploading && (
                      <button
                        onClick={() => {
                          const videoUrl = URL.createObjectURL(videoFile);
                          const video = document.createElement('video');
                          video.src = videoUrl;
                          video.controls = true;
                          video.style.maxWidth = '100%';
                          video.style.maxHeight = '400px';
                          
                          const previewWindow = window.open('', '_blank', 'width=800,height=600');
                          if (previewWindow) {
                            previewWindow.document.write(`
                              <html>
                                <head><title>Video Preview - ${videoMetadata.title}</title></head>
                                <body style="margin: 20px; font-family: Arial, sans-serif;">
                                  <h2>${videoMetadata.title}</h2>
                                  <div style="text-align: center;">
                                    ${video.outerHTML}
                                  </div>
                                  <p><strong>Duration:</strong> ${formatTime(videoMetadata.duration)}</p>
                                  <p><strong>Size:</strong> ${formatFileSize(videoFile.size)}</p>
                                  ${videoMetadata.description ? `<p><strong>Description:</strong> ${videoMetadata.description}</p>` : ''}
                                </body>
                              </html>
                            `);
                          }
                        }}
                        className="px-3 sm:px-4 py-2 border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 whitespace-nowrap text-sm sm:text-base"
                      >
                        <i className="ri-eye-line mr-1 sm:mr-2"></i>
                        Preview Video
                      </button>
                    )}
                    <button
                      onClick={handleVideoUpload}
                      disabled={!videoFile || isUploading || !videoMetadata.title}
                      className="px-4 sm:px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap text-sm sm:text-base"
                    >
                      {isUploading ? (
                        <>
                          <i className="ri-loader-4-line mr-1 sm:mr-2 animate-spin"></i>
                          Uploading...
                        </>
                      ) : (
                        <>
                          <i className="ri-upload-cloud-line mr-1 sm:mr-2"></i>
                          Upload Video
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Demo Video Modal - Mobile Responsive */}
        {showDemoModal && (
          <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-2 sm:p-4">
            <div className={`bg-black rounded-lg overflow-hidden ${isFullscreen ? 'w-full h-full' : 'w-full max-w-6xl max-h-[95vh] sm:max-h-[90vh]'}`}>
              {/* Video Header - Mobile Responsive */}
              <div className="bg-gray-900 px-3 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
                <div className="flex items-center space-x-2 sm:space-x-4">
                  <div className="w-6 h-6 sm:w-8 sm:h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <i className="ri-eye-line text-white text-sm sm:text-base"></i>
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-sm sm:text-base">
                      {uploadedVideo ? videoMetadata.title || 'Custom Demo Video' : 'AI Eyes Security System Demo'}
                    </h3>
                    <p className="text-gray-400 text-xs sm:text-sm">
                      {uploadedVideo ? 'Your Custom Demo' : 'Complete Product Walkthrough'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-1 sm:space-x-2">
                  <button
                    onClick={toggleFullscreen}
                    className="text-gray-400 hover:text-white p-1 sm:p-2"
                    title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
                  >
                    <i className={`${isFullscreen ? 'ri-fullscreen-exit-line' : 'ri-fullscreen-line'} text-base sm:text-lg`}></i>
                  </button>
                  <button
                    onClick={() => {
                      setShowDemoModal(false);
                      setIsPlaying(false);
                      setCurrentTime(0);
                    }}
                    className="text-gray-400 hover:text-white p-1 sm:p-2"
                  >
                    <i className="ri-close-line text-lg sm:text-xl"></i>
                  </button>
                </div>
              </div>

              {/* Video Player - Mobile Responsive */}
              <div className="relative bg-black">
                <div className={`relative ${isFullscreen ? 'h-screen' : 'h-48 sm:h-64 md:h-96 lg:h-[500px]'}`}>
                  {uploadedVideo ? (
                    <video
                      src={uploadedVideo}
                      className="w-full h-full object-contain"
                      controls={false}
                      autoPlay={isPlaying}
                      muted={isMuted}
                      onTimeUpdate={(e) => {
                        const video = e.target as HTMLVideoElement;
                        setCurrentTime(video.currentTime);
                      }}
                      onLoadedMetadata={(e) => {
                        const video = e.target as HTMLVideoElement;
                        setDuration(video.duration);
                      }}
                      onEnded={() => setIsPlaying(false)}
                    />
                  ) : (
                    <>
                      <img
                        src={getSceneImage(getCurrentSegment().scene)}
                        alt={getCurrentSegment().title}
                        className="w-full h-full object-cover"
                      />
                      
                      {/* Play/Pause Overlay - Mobile Responsive */}
                      {!isPlaying && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30">
                          <button
                            onClick={handlePlayPause}
                            className="w-12 h-12 sm:w-16 sm:h-16 lg:w-20 lg:h-20 bg-blue-600 rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors"
                          >
                            <i className="ri-play-fill text-white text-xl sm:text-2xl lg:text-3xl ml-1"></i>
                          </button>
                        </div>
                      )}
                    </>
                  )}

                  {/* Subtitles - Mobile Responsive - only for default demo */}
                  {!uploadedVideo && showSubtitles && (
                    <div className="absolute bottom-12 sm:bottom-16 lg:bottom-20 left-2 right-2 sm:left-4 sm:right-4 lg:left-8 lg:right-8">
                      <div className="bg-black bg-opacity-80 text-white p-2 sm:p-3 lg:p-4 rounded-lg text-center">
                        <p className="text-sm sm:text-base lg:text-lg leading-relaxed">{getCurrentSegment().subtitle}</p>
                      </div>
                    </div>
                  )}

                  {/* Current Scene Title - Mobile Responsive - only for default demo */}
                  {!uploadedVideo && (
                    <div className="absolute top-2 sm:top-4 left-2 sm:left-4 bg-black bg-opacity-70 text-white px-2 sm:px-3 lg:px-4 py-1 sm:py-2 rounded-lg">
                      <h4 className="font-semibold text-xs sm:text-sm lg:text-base">{getCurrentSegment().title}</h4>
                    </div>
                  )}

                  {/* Video Type Indicator */}
                  <div className="absolute top-2 sm:top-4 right-2 sm:right-4 bg-red-600 text-white px-2 sm:px-3 py-1 rounded-lg flex items-center text-xs sm:text-sm">
                    <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-white rounded-full mr-1 sm:mr-2 animate-pulse"></div>
                    {uploadedVideo ? 'CUSTOM' : 'DEMO'}
                  </div>
                </div>

                {/* Video Controls - Mobile Responsive */}
                <div className="bg-gray-900 p-2 sm:p-4">
                  {/* Progress Bar */}
                  <div className="mb-2 sm:mb-4">
                    <div className="flex items-center space-x-2 text-white text-xs sm:text-sm mb-2">
                      <span>{formatTime(currentTime)}</span>
                      <div className="flex-1 relative">
                        <div className="w-full h-1.5 sm:h-2 bg-gray-700 rounded-full">
                          <div 
                            className="h-1.5 sm:h-2 bg-blue-600 rounded-full transition-all duration-300"
                            style={{ width: `${(currentTime / duration) * 100}%` }}
                          ></div>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max={duration}
                          value={currentTime}
                          onChange={(e) => handleSeek(Number(e.target.value))}
                          className="absolute inset-0 w-full h-1.5 sm:h-2 opacity-0 cursor-pointer"
                        />
                      </div>
                      <span>{formatTime(duration)}</span>
                    </div>
                  </div>

                  {/* Control Buttons */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 sm:space-x-4">
                      {/* Play/Pause */}
                      <button
                        onClick={handlePlayPause}
                        className="text-white hover:text-blue-400 transition-colors"
                      >
                        <i className={`${isPlaying ? 'ri-pause-fill' : 'ri-play-fill'} text-lg sm:text-2xl`}></i>
                      </button>

                      {/* Skip Backward */}
                      <button
                        onClick={() => handleSeek(Math.max(0, currentTime - 10))}
                        className="text-white hover:text-blue-400 transition-colors"
                      >
                        <i className="ri-skip-back-line text-base sm:text-xl"></i>
                      </button>

                      {/* Skip Forward */}
                      <button
                        onClick={() => handleSeek(Math.min(duration, currentTime + 10))}
                        className="text-white hover:text-blue-400 transition-colors"
                      >
                        <i className="ri-skip-forward-line text-base sm:text-xl"></i>
                      </button>

                      {/* Volume Controls */}
                      <div className="flex items-center space-x-1 sm:space-x-2">
                        <button
                          onClick={toggleMute}
                          className="text-white hover:text-blue-400 transition-colors"
                        >
                          <i className={`${isMuted || volume === 0 ? 'ri-volume-mute-line' : volume < 0.5 ? 'ri-volume-down-line' : 'ri-volume-up-line'} text-base sm:text-xl`}></i>
                        </button>
                        <div className="w-12 sm:w-20 relative">
                          <div className="w-full h-1 bg-gray-700 rounded-full">
                            <div 
                              className="h-1 bg-white rounded-full"
                              style={{ width: `${isMuted ? 0 : volume * 100}%` }}
                            ></div>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={isMuted ? 0 : volume}
                            onChange={(e) => handleVolumeChange(Number(e.target.value))}
                            className="absolute inset-0 w-full h-1 opacity-0 cursor-pointer"
                          />
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 sm:space-x-4">
                      {/* Playback Speed */}
                      <div className="relative">
                        <select
                          value={playbackSpeed}
                          onChange={(e) => changePlaybackSpeed(Number(e.target.value))}
                          className="bg-gray-800 text-white text-xs sm:text-sm px-1 sm:px-2 py-1 rounded border-none pr-4 sm:pr-6"
                        >
                          <option value={0.5}>0.5x</option>
                          <option value={0.75}>0.75x</option>
                          <option value={1}>1x</option>
                          <option value={1.25}>1.25x</option>
                          <option value={1.5}>1.5x</option>
                          <option value={2}>2x</option>
                        </select>
                      </div>

                      {/* Subtitles Toggle */}
                      {!uploadedVideo && (
                        <button
                          onClick={toggleSubtitles}
                          className={`text-white hover:text-blue-400 transition-colors ${showSubtitles ? 'text-blue-400' : ''}`}
                          title="Toggle Subtitles"
                        >
                          <i className="ri-closed-captioning-line text-base sm:text-xl"></i>
                        </button>
                      )}

                      {/* Quality Selector */}
                      <select className="bg-gray-800 text-white text-xs sm:text-sm px-1 sm:px-2 py-1 rounded border-none pr-4 sm:pr-6">
                        <option value="1080p">1080p</option>
                        <option value="720p">720p</option>
                        <option value="480p">480p</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Demo Chapters */}
                {!uploadedVideo && (
                  <div className="bg-gray-800 p-3 sm:p-4">
                    <h4 className="text-white font-semibold mb-2 sm:mb-3 text-sm sm:text-base">Demo Chapters</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-1 sm:gap-2">
                      {demoSegments.map((segment, index) => (
                        <button
                          key={index}
                          onClick={() => handleSeek(segment.start)}
                          className={`text-left p-2 rounded text-xs sm:text-sm transition-colors ${
                            currentTime >= segment.start && currentTime < segment.end
                              ? 'bg-blue-600 text-white'
                              : 'text-gray-300 hover:bg-gray-700'
                          }`}
                        >
                          <div className="font-medium">{segment.title}</div>
                          <div className="text-xs opacity-75">{formatTime(segment.start)} - {formatTime(segment.end)}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Features Section - Mobile Responsive */}
        <div className="px-4 sm:px-6 py-12 sm:py-20 bg-white/5 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-12 sm:mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Advanced AI Detection Features</h2>
              <p className="text-lg sm:text-xl text-gray-300">Powered by MobileNetV2 Face Recognition and YOLOv9 Activity Detection</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 sm:p-8 border border-white/20">
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-blue-600 rounded-xl flex items-center justify-center mb-4 sm:mb-6">
                  <i className="ri-user-forbid-line text-white text-xl sm:text-2xl"></i>
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Intruder Detection</h3>
                <p className="text-sm sm:text-base text-gray-300">
                  MobileNetV2 face recognition technology identifies unauthorized personnel in farm areas with 100% accuracy.
                </p>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 sm:p-8 border border-white/20">
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-purple-600 rounded-xl flex items-center justify-center mb-4 sm:mb-6">
                  <i className="ri-alarm-warning-line text-white text-xl sm:text-2xl"></i>
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Suspicious Activity</h3>
                <p className="text-sm sm:text-base text-gray-300">
                  YOLOv9 model detects unusual behaviors and potential threats in bank environments in real-time.
                </p>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 sm:p-8 border border-white/20">
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-green-600 rounded-xl flex items-center justify-center mb-4 sm:mb-6">
                  <i className="ri-notification-3-line text-white text-xl sm:text-2xl"></i>
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Instant Alerts</h3>
                <p className="text-sm sm:text-base text-gray-300">
                  Immediate email notifications with snapshots and event details when threats are detected.
                </p>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 sm:p-8 border border-white/20">
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-red-600 rounded-xl flex items-center justify-center mb-4 sm:mb-6">
                  <i className="ri-camera-line text-white text-xl sm:text-2xl"></i>
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Multi-Camera Support</h3>
                <p className="text-sm sm:text-base text-gray-300">
                  Monitor multiple locations simultaneously with live video feeds from IP webcams and mobile devices.
                </p>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 sm:p-8 border border-white/20">
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-yellow-600 rounded-xl flex items-center justify-center mb-4 sm:mb-6">
                  <i className="ri-dashboard-3-line text-white text-xl sm:text-2xl"></i>
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Web Dashboard</h3>
                <p className="text-sm sm:text-base text-gray-300">
                  Comprehensive monitoring interface with logs, filters, and export capabilities for security management.
                </p>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 sm:p-8 border border-white/20">
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-indigo-600 rounded-xl flex items-center justify-center mb-4 sm:mb-6">
                  <i className="ri-shield-check-line text-white text-xl sm:text-2xl"></i>
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Secure Access</h3>
                <p className="text-sm sm:text-base text-gray-300">
                  Protected login system with role-based access control for authorized security personnel only.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section - Mobile Responsive */}
        <div className="px-4 sm:px-6 py-12 sm:py-20">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 sm:mb-6">Ready to Secure Your Property?</h2>
            <p className="text-lg sm:text-xl text-gray-300 mb-6 sm:mb-8">
              Get started with our AI-powered surveillance system today. No expensive CCTV required - 
              works with standard laptops and IP webcams.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
              <button
                onClick={() => navigate('/signup')}
                className="px-6 sm:px-8 py-3 sm:py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold whitespace-nowrap text-sm sm:text-base"
              >
                <i className="ri-rocket-line mr-2"></i>
                Get Started Now
              </button>
              <button 
                onClick={handleDownloadDocumentation}
                className="px-6 sm:px-8 py-3 sm:py-4 border border-gray-400 text-white rounded-lg hover:bg-white/10 transition-colors font-semibold whitespace-nowrap text-sm sm:text-base"
              >
                <i className="ri-download-line mr-2"></i>
                Download Documentation
              </button>
            </div>
          </div>
        </div>

        {/* Footer - Mobile Responsive */}
        <footer className="px-4 sm:px-6 py-6 sm:py-8 border-t border-white/10">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="flex items-center space-x-2 md:space-x-3">
              <div className="w-6 h-6 md:w-8 md:h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <i className="ri-eye-line text-white text-sm md:text-base"></i>
              </div>
              <span className="text-white font-semibold text-sm md:text-base">AI Eyes Security System</span>
            </div>
            <div className="text-gray-400 text-xs md:text-sm text-center md:text-left">
              © 2024 AI Eyes Security. All rights reserved. | 
              <a href="https://readdy.ai/?origin=logo" className="hover:text-white ml-1">Powered by Readdy</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
