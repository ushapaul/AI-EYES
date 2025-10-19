import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../dashboard/components/Header';

export default function Settings() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('system');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showResetModal, setShowResetModal] = useState(false);
  const [showBackupModal, setShowBackupModal] = useState(false);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);

  // System Settings State
  const [systemSettings, setSystemSettings] = useState({
    systemName: 'AI Eyes Security System',
    timezone: 'America/New_York',
    language: 'en',
    dateFormat: 'MM/DD/YYYY',
    timeFormat: '12h',
    autoBackup: true,
    backupFrequency: 'daily',
    backupRetention: '30',
    systemUpdates: 'auto',
    maintenanceMode: false,
    debugMode: false,
    logLevel: 'info'
  });

  // Camera Settings State
  const [cameraSettings, setCameraSettings] = useState({
    defaultResolution: '1080p',
    frameRate: '30',
    compressionLevel: 'medium',
    nightVision: true,
    motionDetection: true,
    motionSensitivity: '75',
    recordingMode: 'motion',
    recordingQuality: 'high',
    storageLocation: 'local',
    maxStorageSize: '500',
    autoDelete: true,
    retentionDays: '30',
    streamingEnabled: true,
    streamingQuality: 'medium',
    bandwidthLimit: '10'
  });

  // AI Settings State
  const [aiSettings, setAiSettings] = useState({
    faceRecognition: true,
    faceRecognitionModel: 'MobileNetV2',
    faceRecognitionThreshold: '80',
    objectDetection: true,
    objectDetectionModel: 'YOLOv9',
    objectDetectionThreshold: '75',
    behaviorAnalysis: true,
    behaviorSensitivity: '70',
    realTimeProcessing: true,
    batchProcessing: false,
    gpuAcceleration: true,
    modelUpdateFrequency: 'weekly',
    trainingDataCollection: true,
    anonymizeData: true,
    confidenceThreshold: '85'
  });

  // Alert Settings State
  const [alertSettings, setAlertSettings] = useState({
    emailNotifications: true,
    emailAddress: 'admin@company.com',
    smsNotifications: true,
    smsNumber: '+1234567890',
    pushNotifications: true,
    webhookUrl: '',
    alertSeverityFilter: 'medium',
    alertFrequencyLimit: '5',
    alertCooldown: '60',
    escalationEnabled: true,
    escalationDelay: '30',
    escalationContacts: 'security@company.com',
    soundAlerts: true,
    alertVolume: '80',
    customAlertTones: false,
    alertHistory: '90'
  });

  // Security Settings State
  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: true,
    sessionTimeout: '30',
    passwordPolicy: 'strong',
    loginAttempts: '3',
    accountLockout: '15',
    ipWhitelist: '',
    sslEnabled: true,
    encryptionLevel: 'AES256',
    auditLogging: true,
    accessLogging: true,
    dataRetention: '365',
    gdprCompliance: true,
    anonymizePersonalData: true,
    dataExportEnabled: true,
    apiAccess: false
  });

  // Network Settings State
  const [networkSettings, setNetworkSettings] = useState({
    networkInterface: 'eth0',
    ipAddress: '192.168.1.100',
    subnetMask: '255.255.255.0',
    gateway: '192.168.1.1',
    dnsServer: '8.8.8.8',
    dhcpEnabled: true,
    portRange: '8000-8100',
    firewallEnabled: true,
    vpnEnabled: false,
    vpnServer: '',
    bandwidthMonitoring: true,
    networkDiagnostics: true,
    connectionTimeout: '30',
    retryAttempts: '3',
    proxyEnabled: false
  });

  const handleSaveSettings = () => {
    console.log('Saving all settings:', {
      system: systemSettings,
      camera: cameraSettings,
      ai: aiSettings,
      alerts: alertSettings,
      security: securitySettings,
      network: networkSettings
    });
    setShowSaveModal(true);
  };

  const handleResetSettings = () => {
    setShowResetModal(true);
  };

  const confirmReset = () => {
    // Reset all settings to defaults
    console.log('Resetting all settings to defaults');
    setShowResetModal(false);
    alert('All settings have been reset to default values.');
  };

  const handleBackup = () => {
    const backupData = {
      timestamp: new Date().toISOString(),
      version: '1.0',
      settings: {
        system: systemSettings,
        camera: cameraSettings,
        ai: aiSettings,
        alerts: alertSettings,
        security: securitySettings,
        network: networkSettings
      }
    };

    const blob = new Blob([JSON.stringify(backupData, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai_eyes_backup_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    setShowBackupModal(false);
    alert('Settings backup downloaded successfully!');
  };

  const handleRestore = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const backupData = JSON.parse(e.target?.result as string);
          if (backupData.settings) {
            setSystemSettings(backupData.settings.system || systemSettings);
            setCameraSettings(backupData.settings.camera || cameraSettings);
            setAiSettings(backupData.settings.ai || aiSettings);
            setAlertSettings(backupData.settings.alerts || alertSettings);
            setSecuritySettings(backupData.settings.security || securitySettings);
            setNetworkSettings(backupData.settings.network || networkSettings);
            alert('Settings restored successfully!');
          }
        } catch (error) {
          alert('Invalid backup file format.');
        }
      };
      reader.readAsText(file);
    }
    setShowRestoreModal(false);
  };

  const testConnection = () => {
    setShowTestModal(true);
    // Simulate connection test
    setTimeout(() => {
      setShowTestModal(false);
      alert('System connection test completed successfully!');
    }, 2000);
  };

  const renderSystemSettings = () => (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">General System Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">System Name</label>
            <input
              type="text"
              value={systemSettings.systemName}
              onChange={(e) => setSystemSettings({...systemSettings, systemName: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
            <select
              value={systemSettings.timezone}
              onChange={(e) => setSystemSettings({...systemSettings, timezone: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="America/New_York">Eastern Time (UTC-5)</option>
              <option value="America/Chicago">Central Time (UTC-6)</option>
              <option value="America/Denver">Mountain Time (UTC-7)</option>
              <option value="America/Los_Angeles">Pacific Time (UTC-8)</option>
              <option value="UTC">UTC</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
            <select
              value={systemSettings.language}
              onChange={(e) => setSystemSettings({...systemSettings, language: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="zh">Chinese</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date Format</label>
            <select
              value={systemSettings.dateFormat}
              onChange={(e) => setSystemSettings({...systemSettings, dateFormat: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Backup & Maintenance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="flex items-center mb-4">
              <input
                type="checkbox"
                checked={systemSettings.autoBackup}
                onChange={(e) => setSystemSettings({...systemSettings, autoBackup: e.target.checked})}
                className="mr-3"
              />
              <span className="text-sm font-medium text-gray-700">Enable Automatic Backup</span>
            </label>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Backup Frequency</label>
              <select
                value={systemSettings.backupFrequency}
                onChange={(e) => setSystemSettings({...systemSettings, backupFrequency: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
                disabled={!systemSettings.autoBackup}
              >
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Backup Retention (days)</label>
            <input
              type="number"
              value={systemSettings.backupRetention}
              onChange={(e) => setSystemSettings({...systemSettings, backupRetention: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              min="1"
              max="365"
            />
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Maintenance</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={systemSettings.maintenanceMode}
              onChange={(e) => setSystemSettings({...systemSettings, maintenanceMode: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Maintenance Mode</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={systemSettings.debugMode}
              onChange={(e) => setSystemSettings({...systemSettings, debugMode: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Debug Mode</span>
          </label>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Log Level</label>
            <select
              value={systemSettings.logLevel}
              onChange={(e) => setSystemSettings({...systemSettings, logLevel: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="error">Error</option>
              <option value="warn">Warning</option>
              <option value="info">Info</option>
              <option value="debug">Debug</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCameraSettings = () => (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Camera Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Default Resolution</label>
            <select
              value={cameraSettings.defaultResolution}
              onChange={(e) => setCameraSettings({...cameraSettings, defaultResolution: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="4K">4K (3840x2160)</option>
              <option value="1080p">1080p (1920x1080)</option>
              <option value="720p">720p (1280x720)</option>
              <option value="480p">480p (854x480)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Frame Rate (FPS)</label>
            <select
              value={cameraSettings.frameRate}
              onChange={(e) => setCameraSettings({...cameraSettings, frameRate: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="60">60 FPS</option>
              <option value="30">30 FPS</option>
              <option value="24">24 FPS</option>
              <option value="15">15 FPS</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Compression Level</label>
            <select
              value={cameraSettings.compressionLevel}
              onChange={(e) => setCameraSettings({...cameraSettings, compressionLevel: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="low">Low (Best Quality)</option>
              <option value="medium">Medium</option>
              <option value="high">High (Smaller Files)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Motion Sensitivity (%)</label>
            <input
              type="range"
              min="0"
              max="100"
              value={cameraSettings.motionSensitivity}
              onChange={(e) => setCameraSettings({...cameraSettings, motionSensitivity: e.target.value})}
              className="w-full"
            />
            <div className="text-sm text-gray-600 mt-1">{cameraSettings.motionSensitivity}%</div>
          </div>
        </div>
        <div className="mt-6 space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={cameraSettings.nightVision}
              onChange={(e) => setCameraSettings({...cameraSettings, nightVision: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Enable Night Vision</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={cameraSettings.motionDetection}
              onChange={(e) => setCameraSettings({...cameraSettings, motionDetection: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Enable Motion Detection</span>
          </label>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recording Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Recording Mode</label>
            <select
              value={cameraSettings.recordingMode}
              onChange={(e) => setCameraSettings({...cameraSettings, recordingMode: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="continuous">Continuous</option>
              <option value="motion">Motion Triggered</option>
              <option value="scheduled">Scheduled</option>
              <option value="manual">Manual Only</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Recording Quality</label>
            <select
              value={cameraSettings.recordingQuality}
              onChange={(e) => setCameraSettings({...cameraSettings, recordingQuality: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="high">High Quality</option>
              <option value="medium">Medium Quality</option>
              <option value="low">Low Quality</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Max Storage Size (GB)</label>
            <input
              type="number"
              value={cameraSettings.maxStorageSize}
              onChange={(e) => setCameraSettings({...cameraSettings, maxStorageSize: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              min="10"
              max="10000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Retention Period (days)</label>
            <input
              type="number"
              value={cameraSettings.retentionDays}
              onChange={(e) => setCameraSettings({...cameraSettings, retentionDays: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              min="1"
              max="365"
            />
          </div>
        </div>
        <div className="mt-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={cameraSettings.autoDelete}
              onChange={(e) => setCameraSettings({...cameraSettings, autoDelete: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Auto-delete old recordings</span>
          </label>
        </div>
      </div>
    </div>
  );

  const renderAISettings = () => (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Face Recognition</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={aiSettings.faceRecognition}
              onChange={(e) => setAiSettings({...aiSettings, faceRecognition: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Enable Face Recognition</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Recognition Model</label>
              <select
                value={aiSettings.faceRecognitionModel}
                onChange={(e) => setAiSettings({...aiSettings, faceRecognitionModel: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
                disabled={!aiSettings.faceRecognition}
              >
                <option value="MobileNetV2">MobileNetV2 (High Accuracy)</option>
                <option value="EfficientNet B7">EfficientNet B7 (Advanced Deep Learning)</option>
                <option value="FaceNet">FaceNet (Alternative)</option>
                <option value="DeepFace">DeepFace Neural Network</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Recognition Threshold (%)</label>
              <input
                type="range"
                min="50"
                max="100"
                value={aiSettings.faceRecognitionThreshold}
                onChange={(e) => setAiSettings({...aiSettings, faceRecognitionThreshold: e.target.value})}
                className="w-full"
                disabled={!aiSettings.faceRecognition}
              />
              <div className="text-sm text-gray-600 mt-1">{aiSettings.faceRecognitionThreshold}%</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Object Detection</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={aiSettings.objectDetection}
              onChange={(e) => setAiSettings({...aiSettings, objectDetection: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Enable Object Detection</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Detection Model</label>
              <select
                value={aiSettings.objectDetectionModel}
                onChange={(e) => setAiSettings({...aiSettings, objectDetectionModel: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
                disabled={!aiSettings.objectDetection}
              >
                <option value="YOLOv9">YOLOv9 (Latest)</option>
                <option value="YOLOv8">YOLOv8</option>
                <option value="YOLOv5">YOLOv5</option>
                <option value="SSD">SSD MobileNet</option>
                <option value="RCNN">Faster R-CNN</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Detection Threshold (%)</label>
              <input
                type="range"
                min="50"
                max="100"
                value={aiSettings.objectDetectionThreshold}
                onChange={(e) => setAiSettings({...aiSettings, objectDetectionThreshold: e.target.value})}
                className="w-full"
                disabled={!aiSettings.objectDetection}
              />
              <div className="text-sm text-gray-600 mt-1">{aiSettings.objectDetectionThreshold}%</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Behavior Analysis</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={aiSettings.behaviorAnalysis}
              onChange={(e) => setAiSettings({...aiSettings, behaviorAnalysis: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Enable Behavior Analysis</span>
          </label>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Behavior Sensitivity (%)</label>
            <input
              type="range"
              min="0"
              max="100"
              value={aiSettings.behaviorSensitivity}
              onChange={(e) => setAiSettings({...aiSettings, behaviorSensitivity: e.target.value})}
              className="w-full"
              disabled={!aiSettings.behaviorAnalysis}
            />
            <div className="text-sm text-gray-600 mt-1">{aiSettings.behaviorSensitivity}%</div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Settings</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={aiSettings.realTimeProcessing}
              onChange={(e) => setAiSettings({...aiSettings, realTimeProcessing: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Real-time Processing</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={aiSettings.gpuAcceleration}
              onChange={(e) => setAiSettings({...aiSettings, gpuAcceleration: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">GPU Acceleration</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={aiSettings.trainingDataCollection}
              onChange={(e) => setAiSettings({...aiSettings, trainingDataCollection: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Collect Training Data</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={aiSettings.anonymizeData}
              onChange={(e) => setAiSettings({...aiSettings, anonymizeData: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Anonymize Personal Data</span>
          </label>
        </div>
      </div>
    </div>
  );

  const renderAlertSettings = () => (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Methods</h3>
        <div className="space-y-6">
          <div>
            <label className="flex items-center mb-3">
              <input
                type="checkbox"
                checked={alertSettings.emailNotifications}
                onChange={(e) => setAlertSettings({...alertSettings, emailNotifications: e.target.checked})}
                className="mr-3"
              />
              <span className="text-sm font-medium text-gray-700">Email Notifications</span>
            </label>
            <input
              type="email"
              value={alertSettings.emailAddress}
              onChange={(e) => setAlertSettings({...alertSettings, emailAddress: e.target.value})}
              placeholder="admin@company.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              disabled={!alertSettings.emailNotifications}
            />
          </div>
          <div>
            <label className="flex items-center mb-3">
              <input
                type="checkbox"
                checked={alertSettings.smsNotifications}
                onChange={(e) => setAlertSettings({...alertSettings, smsNotifications: e.target.checked})}
                className="mr-3"
              />
              <span className="text-sm font-medium text-gray-700">SMS Notifications</span>
            </label>
            <input
              type="tel"
              value={alertSettings.smsNumber}
              onChange={(e) => setAlertSettings({...alertSettings, smsNumber: e.target.value})}
              placeholder="+1234567890"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              disabled={!alertSettings.smsNotifications}
            />
          </div>
          <div>
            <label className="flex items-center mb-3">
              <input
                type="checkbox"
                checked={alertSettings.pushNotifications}
                onChange={(e) => setAlertSettings({...alertSettings, pushNotifications: e.target.checked})}
                className="mr-3"
              />
              <span className="text-sm font-medium text-gray-700">Push Notifications</span>
            </label>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Alert Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Minimum Severity Level</label>
            <select
              value={alertSettings.alertSeverityFilter}
              onChange={(e) => setAlertSettings({...alertSettings, alertSeverityFilter: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="low">Low and above</option>
              <option value="medium">Medium and above</option>
              <option value="high">High and above</option>
              <option value="critical">Critical only</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Alert Frequency Limit (per hour)</label>
            <input
              type="number"
              value={alertSettings.alertFrequencyLimit}
              onChange={(e) => setAlertSettings({...alertSettings, alertFrequencyLimit: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              min="1"
              max="100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Alert Cooldown (minutes)</label>
            <input
              type="number"
              value={alertSettings.alertCooldown}
              onChange={(e) => setAlertSettings({...alertSettings, alertCooldown: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              min="1"
              max="1440"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Alert Volume (%)</label>
            <input
              type="range"
              min="0"
              max="100"
              value={alertSettings.alertVolume}
              onChange={(e) => setAlertSettings({...alertSettings, alertVolume: e.target.value})}
              className="w-full"
            />
            <div className="text-sm text-gray-600 mt-1">{alertSettings.alertVolume}%</div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Escalation Settings</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={alertSettings.escalationEnabled}
              onChange={(e) => setAlertSettings({...alertSettings, escalationEnabled: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Enable Alert Escalation</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Escalation Delay (minutes)</label>
              <input
                type="number"
                value={alertSettings.escalationDelay}
                onChange={(e) => setAlertSettings({...alertSettings, escalationDelay: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                min="1"
                max="1440"
                disabled={!alertSettings.escalationEnabled}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Escalation Contacts</label>
              <input
                type="email"
                value={alertSettings.escalationContacts}
                onChange={(e) => setAlertSettings({...alertSettings, escalationContacts: e.target.value})}
                placeholder="security@company.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                disabled={!alertSettings.escalationEnabled}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Authentication & Access</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={securitySettings.twoFactorAuth}
              onChange={(e) => setSecuritySettings({...securitySettings, twoFactorAuth: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Two-Factor Authentication</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout (minutes)</label>
              <input
                type="number"
                value={securitySettings.sessionTimeout}
                onChange={(e) => setSecuritySettings({...securitySettings, sessionTimeout: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                min="5"
                max="1440"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password Policy</label>
              <select
                value={securitySettings.passwordPolicy}
                onChange={(e) => setSecuritySettings({...securitySettings, passwordPolicy: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
              >
                <option value="basic">Basic (8+ characters)</option>
                <option value="strong">Strong (12+ chars, mixed case, numbers)</option>
                <option value="complex">Complex (16+ chars, symbols required)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Max Login Attempts</label>
              <input
                type="number"
                value={securitySettings.loginAttempts}
                onChange={(e) => setSecuritySettings({...securitySettings, loginAttempts: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                min="1"
                max="10"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Account Lockout (minutes)</label>
              <input
                type="number"
                value={securitySettings.accountLockout}
                onChange={(e) => setSecuritySettings({...securitySettings, accountLockout: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                min="1"
                max="1440"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Protection</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={securitySettings.sslEnabled}
              onChange={(e) => setSecuritySettings({...securitySettings, sslEnabled: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">SSL/TLS Encryption</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={securitySettings.auditLogging}
              onChange={(e) => setSecuritySettings({...securitySettings, auditLogging: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Audit Logging</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={securitySettings.gdprCompliance}
              onChange={(e) => setSecuritySettings({...securitySettings, gdprCompliance: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">GDPR Compliance Mode</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Encryption Level</label>
              <select
                value={securitySettings.encryptionLevel}
                onChange={(e) => setSecuritySettings({...securitySettings, encryptionLevel: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
              >
                <option value="AES128">AES-128</option>
                <option value="AES256">AES-256</option>
                <option value="RSA2048">RSA-2048</option>
                <option value="RSA4096">RSA-4096</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Data Retention (days)</label>
              <input
                type="number"
                value={securitySettings.dataRetention}
                onChange={(e) => setSecuritySettings({...securitySettings, dataRetention: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                min="1"
                max="3650"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Network Security</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">IP Whitelist</label>
            <textarea
              value={securitySettings.ipWhitelist}
              onChange={(e) => setSecuritySettings({...securitySettings, ipWhitelist: e.target.value})}
              placeholder="192.168.1.0/24&#10;10.0.0.0/8"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              rows={3}
            />
            <p className="text-xs text-gray-500 mt-1">Enter IP addresses or CIDR blocks, one per line</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNetworkSettings = () => (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Network Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Network Interface</label>
            <select
              value={networkSettings.networkInterface}
              onChange={(e) => setNetworkSettings({...networkSettings, networkInterface: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="eth0">Ethernet (eth0)</option>
              <option value="wlan0">WiFi (wlan0)</option>
              <option value="eth1">Ethernet 2 (eth1)</option>
            </select>
          </div>
          <div>
            <label className="flex items-center mb-2">
              <input
                type="checkbox"
                checked={networkSettings.dhcpEnabled}
                onChange={(e) => setNetworkSettings({...networkSettings, dhcpEnabled: e.target.checked})}
                className="mr-2"
              />
              <span className="text-sm font-medium text-gray-700">Enable DHCP</span>
            </label>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">IP Address</label>
            <input
              type="text"
              value={networkSettings.ipAddress}
              onChange={(e) => setNetworkSettings({...networkSettings, ipAddress: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              disabled={networkSettings.dhcpEnabled}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Subnet Mask</label>
            <input
              type="text"
              value={networkSettings.subnetMask}
              onChange={(e) => setNetworkSettings({...networkSettings, subnetMask: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              disabled={networkSettings.dhcpEnabled}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Gateway</label>
            <input
              type="text"
              value={networkSettings.gateway}
              onChange={(e) => setNetworkSettings({...networkSettings, gateway: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              disabled={networkSettings.dhcpEnabled}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">DNS Server</label>
            <input
              type="text"
              value={networkSettings.dnsServer}
              onChange={(e) => setNetworkSettings({...networkSettings, dnsServer: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Port & Firewall Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Port Range</label>
            <input
              type="text"
              value={networkSettings.portRange}
              onChange={(e) => setNetworkSettings({...networkSettings, portRange: e.target.value})}
              placeholder="8000-8100"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={networkSettings.firewallEnabled}
                onChange={(e) => setNetworkSettings({...networkSettings, firewallEnabled: e.target.checked})}
                className="mr-3"
              />
              <span className="text-sm font-medium text-gray-700">Enable Firewall</span>
            </label>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Connection Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Connection Timeout (seconds)</label>
            <input
              type="number"
              value={networkSettings.connectionTimeout}
              onChange={(e) => setNetworkSettings({...networkSettings, connectionTimeout: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              min="5"
              max="300"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Retry Attempts</label>
            <input
              type="number"
              value={networkSettings.retryAttempts}
              onChange={(e) => setNetworkSettings({...networkSettings, retryAttempts: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              min="1"
              max="10"
            />
          </div>
        </div>
        <div className="mt-4 space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={networkSettings.bandwidthMonitoring}
              onChange={(e) => setNetworkSettings({...networkSettings, bandwidthMonitoring: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Enable Bandwidth Monitoring</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={networkSettings.networkDiagnostics}
              onChange={(e) => setNetworkSettings({...networkSettings, networkDiagnostics: e.target.checked})}
              className="mr-3"
            />
            <span className="text-sm font-medium text-gray-700">Enable Network Diagnostics</span>
          </label>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">System Settings</h1>
              <p className="text-gray-600">Configure your AI Eyes Security System</p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={testConnection}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
              >
                <i className="ri-wifi-line mr-2"></i>
                Test Connection
              </button>
              <button
                onClick={() => setShowBackupModal(true)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 whitespace-nowrap"
              >
                <i className="ri-download-line mr-2"></i>
                Backup Settings
              </button>
              <button
                onClick={() => setShowRestoreModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 whitespace-nowrap"
              >
                <i className="ri-upload-line mr-2"></i>
                Restore Settings
              </button>
            </div>
          </div>
        </div>

        {/* Test Connection Modal */}
        {showTestModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <i className="ri-wifi-line text-3xl text-blue-600 animate-pulse"></i>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Testing System Connection</h3>
                <p className="text-gray-600 mb-4">Please wait while we verify all system components...</p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{width: '75%'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Backup Modal */}
        {showBackupModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                  <i className="ri-download-line text-2xl text-green-600"></i>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Backup Settings</h3>
                  <p className="text-sm text-gray-600">Download current system configuration</p>
                </div>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-800">
                  This will create a complete backup of all your system settings including camera configurations, AI models, and security preferences.
                </p>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowBackupModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBackup}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 whitespace-nowrap"
                >
                  <i className="ri-download-line mr-2"></i>
                  Download Backup
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Restore Modal */}
        {showRestoreModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                  <i className="ri-upload-line text-2xl text-blue-600"></i>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Restore Settings</h3>
                  <p className="text-sm text-gray-600">Upload a settings backup file</p>
                </div>
              </div>
              
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <div className="flex items-center mb-2">
                  <i className="ri-alert-line text-yellow-600 mr-2"></i>
                  <span className="font-medium text-yellow-800">Warning</span>
                </div>
                <p className="text-sm text-yellow-700">
                  Restoring settings will overwrite your current configuration. Make sure to backup your current settings first.
                </p>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Backup File</label>
                <input
                  type="file"
                  accept=".json"
                  onChange={handleRestore}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowRestoreModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Save Confirmation Modal */}
        {showSaveModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <i className="ri-check-line text-3xl text-green-600"></i>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Settings Saved Successfully</h3>
                <p className="text-gray-600 mb-6">All configuration changes have been applied to your system.</p>
                <button
                  onClick={() => setShowSaveModal(false)}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 whitespace-nowrap"
                >
                  Continue
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Reset Confirmation Modal */}
        {showResetModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-4">
                  <i className="ri-refresh-line text-2xl text-red-600"></i>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Reset All Settings</h3>
                  <p className="text-sm text-gray-600">This action cannot be undone</p>
                </div>
              </div>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-center mb-2">
                  <i className="ri-alert-line text-red-600 mr-2"></i>
                  <span className="font-medium text-red-800">Critical Warning</span>
                </div>
                <p className="text-sm text-red-700">
                  This will reset ALL system settings to their default values. All custom configurations, camera settings, AI models, and preferences will be lost.
                </p>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowResetModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmReset}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 whitespace-nowrap"
                >
                  <i className="ri-refresh-line mr-2"></i>
                  Reset All Settings
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6 overflow-x-auto">
              <button
                onClick={() => setActiveTab('system')}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'system'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className="ri-settings-3-line mr-2"></i>
                System
              </button>
              <button
                onClick={() => setActiveTab('camera')}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'camera'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className="ri-camera-line mr-2"></i>
                Camera
              </button>
              <button
                onClick={() => setActiveTab('ai')}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'ai'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className="ri-brain-line mr-2"></i>
                AI Detection
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'alerts'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className="ri-notification-3-line mr-2"></i>
                Alerts
              </button>
              <button
                onClick={() => setActiveTab('security')}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'security'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className="ri-shield-check-line mr-2"></i>
                Security
              </button>
              <button
                onClick={() => setActiveTab('network')}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'network'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <i className="ri-wifi-line mr-2"></i>
                Network
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'system' && renderSystemSettings()}
            {activeTab === 'camera' && renderCameraSettings()}
            {activeTab === 'ai' && renderAISettings()}
            {activeTab === 'alerts' && renderAlertSettings()}
            {activeTab === 'security' && renderSecuritySettings()}
            {activeTab === 'network' && renderNetworkSettings()}
          </div>

          <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleResetSettings}
                  className="px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 whitespace-nowrap"
                >
                  <i className="ri-refresh-line mr-2"></i>
                  Reset to Defaults
                </button>
                <span className="text-sm text-gray-500">
                  Last saved: {new Date().toLocaleString()}
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveSettings}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 whitespace-nowrap"
                >
                  <i className="ri-save-line mr-2"></i>
                  Save All Settings
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}