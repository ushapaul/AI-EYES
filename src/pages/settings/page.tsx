import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../dashboard/components/Header';
import { useSettings } from '../../hooks/useSettings';

export default function Settings() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('system');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [testResults, setTestResults] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Use real settings hook
  const { 
    settings, 
    loading, 
    error, 
    updateSettings, 
    backupSettings, 
    restoreSettings, 
    testConnection 
  } = useSettings();

  // Local state for form inputs
  const [systemSettings, setSystemSettings] = useState<any>(settings.system || {});
  const [cameraSettings, setCameraSettings] = useState<any>(settings.camera || {});
  const [aiSettings, setAiSettings] = useState<any>(settings.ai || {});
  const [alertSettings, setAlertSettings] = useState<any>(settings.alerts || {});
  const [securitySettings, setSecuritySettings] = useState<any>(settings.security || {});
  const [networkSettings, setNetworkSettings] = useState<any>(settings.network || {});

  // Update local state when settings from API are loaded
  useEffect(() => {
    if (settings.system) setSystemSettings(settings.system);
    if (settings.camera) setCameraSettings(settings.camera);
    if (settings.ai) setAiSettings(settings.ai);
    if (settings.alerts) setAlertSettings(settings.alerts);
    if (settings.security) setSecuritySettings(settings.security);
    if (settings.network) setNetworkSettings(settings.network);
  }, [settings]);

  const handleSaveSettings = async () => {
    setIsSaving(true);
    try {
      const results = await Promise.all([
        updateSettings('system', systemSettings),
        updateSettings('camera', cameraSettings),
        updateSettings('ai', aiSettings),
        updateSettings('alerts', alertSettings),
        updateSettings('security', securitySettings),
        updateSettings('network', networkSettings),
      ]);

      const allSuccess = results.every(r => r === true);
      
      if (allSuccess) {
        setShowSaveModal(true);
        setTimeout(() => setShowSaveModal(false), 3000);
      } else {
        alert('Some settings failed to save. Please try again.');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleBackup = async () => {
    const result = await backupSettings();
    if (result.success && result.backup) {
      const dataStr = JSON.stringify(result.backup, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `ai-eyes-settings-${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      URL.revokeObjectURL(url);
      alert('✅ Settings backed up successfully!');
    } else {
      alert('❌ Failed to backup settings');
    }
  };

  const handleRestore = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = async (e: any) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = async (event) => {
          try {
            const backupData = JSON.parse(event.target?.result as string);
            const success = await restoreSettings(backupData);
            if (success) {
              alert('✅ Settings restored successfully!');
              window.location.reload();
            } else {
              alert('❌ Failed to restore settings');
            }
          } catch (error) {
            alert('❌ Invalid backup file');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const handleTestConnection = async () => {
    const result = await testConnection();
    if (result.success) {
      setTestResults(result.results);
      setShowTestModal(true);
    } else {
      alert('❌ Connection test failed');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header isConnected={false} />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <i className="ri-loader-4-line animate-spin text-4xl text-blue-600"></i>
            <p className="mt-4 text-gray-600">Loading settings from database...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header isConnected={false} />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <i className="ri-error-warning-line text-3xl text-red-600 mr-3"></i>
              <h2 className="text-xl font-semibold text-red-800">Failed to Load Settings</h2>
            </div>
            <p className="text-red-700 mb-2">{error}</p>
            <p className="text-sm text-red-600">Make sure the backend server is running on http://localhost:8000</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header isConnected={true} />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
              <p className="text-gray-600 mt-1">Configure your AI Eyes Security System</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={handleTestConnection}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center"
              >
                <i className="ri-wifi-line mr-2"></i>
                Test Connection
              </button>
              <button
                onClick={handleBackup}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center"
              >
                <i className="ri-download-line mr-2"></i>
                Backup Settings
              </button>
              <button
                onClick={handleRestore}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
              >
                <i className="ri-upload-line mr-2"></i>
                Restore Settings
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'system', icon: 'ri-settings-3-line', label: 'System' },
                { id: 'camera', icon: 'ri-camera-line', label: 'Camera' },
                { id: 'ai', icon: 'ri-robot-line', label: 'AI Detection' },
                { id: 'alerts', icon: 'ri-notification-line', label: 'Alerts' },
                { id: 'security', icon: 'ri-shield-line', label: 'Security' },
                { id: 'network', icon: 'ri-global-line', label: 'Network' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <i className={`${tab.icon} mr-2`}></i>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Settings Content */}
          <div className="p-6">
            {/* System Settings */}
            {activeTab === 'system' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">General System Settings</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      System Name
                    </label>
                    <input
                      type="text"
                      value={systemSettings.systemName || ''}
                      onChange={(e) => setSystemSettings({ ...systemSettings, systemName: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Timezone
                    </label>
                    <select
                      value={systemSettings.timezone || 'UTC'}
                      onChange={(e) => setSystemSettings({ ...systemSettings, timezone: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time (UTC-5)</option>
                      <option value="America/Chicago">Central Time (UTC-6)</option>
                      <option value="America/Denver">Mountain Time (UTC-7)</option>
                      <option value="America/Los_Angeles">Pacific Time (UTC-8)</option>
                      <option value="Asia/Kolkata">India Standard Time (UTC+5:30)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Language
                    </label>
                    <select
                      value={systemSettings.language || 'en'}
                      onChange={(e) => setSystemSettings({ ...systemSettings, language: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                      <option value="de">German</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date Format
                    </label>
                    <select
                      value={systemSettings.dateFormat || 'MM/DD/YYYY'}
                      onChange={(e) => setSystemSettings({ ...systemSettings, dateFormat: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    </select>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Backup & Maintenance</h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Enable Automatic Backup</label>
                        <p className="text-sm text-gray-500">Automatically backup settings and data</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={systemSettings.autoBackup || false}
                          onChange={(e) => setSystemSettings({ ...systemSettings, autoBackup: e.target.checked })}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Backup Frequency
                        </label>
                        <select
                          value={systemSettings.backupFrequency || 'daily'}
                          onChange={(e) => setSystemSettings({ ...systemSettings, backupFrequency: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                          disabled={!systemSettings.autoBackup}
                        >
                          <option value="hourly">Hourly</option>
                          <option value="daily">Daily</option>
                          <option value="weekly">Weekly</option>
                          <option value="monthly">Monthly</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Backup Retention (days)
                        </label>
                        <input
                          type="number"
                          value={systemSettings.backupRetention || '30'}
                          onChange={(e) => setSystemSettings({ ...systemSettings, backupRetention: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                          disabled={!systemSettings.autoBackup}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Camera Settings */}
            {activeTab === 'camera' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Camera Configuration</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Default Resolution
                    </label>
                    <select
                      value={cameraSettings.defaultResolution || '1080p'}
                      onChange={(e) => setCameraSettings({ ...cameraSettings, defaultResolution: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="720p">720p (HD)</option>
                      <option value="1080p">1080p (Full HD)</option>
                      <option value="1440p">1440p (2K)</option>
                      <option value="2160p">2160p (4K)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Frame Rate (FPS)
                    </label>
                    <select
                      value={cameraSettings.frameRate || '30'}
                      onChange={(e) => setCameraSettings({ ...cameraSettings, frameRate: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="15">15 FPS</option>
                      <option value="24">24 FPS</option>
                      <option value="30">30 FPS</option>
                      <option value="60">60 FPS</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Motion Sensitivity (%)
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={cameraSettings.motionSensitivity || '75'}
                      onChange={(e) => setCameraSettings({ ...cameraSettings, motionSensitivity: e.target.value })}
                      className="w-full"
                    />
                    <div className="text-sm text-gray-600 text-right">{cameraSettings.motionSensitivity || 75}%</div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Recording Quality
                    </label>
                    <select
                      value={cameraSettings.recordingQuality || 'high'}
                      onChange={(e) => setCameraSettings({ ...cameraSettings, recordingQuality: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="ultra">Ultra</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Night Vision</label>
                      <p className="text-sm text-gray-500">Enable infrared night vision mode</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={cameraSettings.nightVision || false}
                        onChange={(e) => setCameraSettings({ ...cameraSettings, nightVision: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Motion Detection</label>
                      <p className="text-sm text-gray-500">Detect motion in camera feed</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={cameraSettings.motionDetection || false}
                        onChange={(e) => setCameraSettings({ ...cameraSettings, motionDetection: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* AI Settings */}
            {activeTab === 'ai' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">AI Detection Settings</h2>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <div className="flex items-start">
                    <i className="ri-information-line text-blue-600 text-xl mr-3 mt-0.5"></i>
                    <div>
                      <p className="text-sm text-blue-800 font-medium">AI Models Active</p>
                      <p className="text-sm text-blue-700 mt-1">
                        Face Recognition: <strong>{aiSettings.faceRecognitionModel || 'MobileNetV2'}</strong> | 
                        Object Detection: <strong>{aiSettings.objectDetectionModel || 'YOLOv8'}</strong>
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Face Recognition</label>
                      <p className="text-sm text-gray-500">Identify known persons in camera feeds</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={aiSettings.faceRecognition || false}
                        onChange={(e) => setAiSettings({ ...aiSettings, faceRecognition: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Face Recognition Model
                      </label>
                      <select
                        value={aiSettings.faceRecognitionModel || 'MobileNetV2'}
                        onChange={(e) => setAiSettings({ ...aiSettings, faceRecognitionModel: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        disabled={!aiSettings.faceRecognition}
                      >
                        <option value="MobileNetV2">MobileNetV2 (Fast)</option>
                        <option value="EfficientNet">EfficientNet (Accurate)</option>
                        <option value="LBPH">LBPH (Lightweight)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Recognition Threshold (%)
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={aiSettings.faceRecognitionThreshold || '80'}
                        onChange={(e) => setAiSettings({ ...aiSettings, faceRecognitionThreshold: e.target.value })}
                        className="w-full"
                        disabled={!aiSettings.faceRecognition}
                      />
                      <div className="text-sm text-gray-600 text-right">{aiSettings.faceRecognitionThreshold || 80}%</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-6">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Object Detection</label>
                      <p className="text-sm text-gray-500">Detect objects and activities</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={aiSettings.objectDetection || false}
                        onChange={(e) => setAiSettings({ ...aiSettings, objectDetection: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Object Detection Model
                      </label>
                      <select
                        value={aiSettings.objectDetectionModel || 'YOLOv8'}
                        onChange={(e) => setAiSettings({ ...aiSettings, objectDetectionModel: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        disabled={!aiSettings.objectDetection}
                      >
                        <option value="YOLOv8">YOLOv8 (Latest)</option>
                        <option value="YOLOv5">YOLOv5 (Stable)</option>
                        <option value="SSD">SSD (Fast)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Detection Threshold (%)
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={aiSettings.objectDetectionThreshold || '75'}
                        onChange={(e) => setAiSettings({ ...aiSettings, objectDetectionThreshold: e.target.value })}
                        className="w-full"
                        disabled={!aiSettings.objectDetection}
                      />
                      <div className="text-sm text-gray-600 text-right">{aiSettings.objectDetectionThreshold || 75}%</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-6">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Real-Time Processing</label>
                      <p className="text-sm text-gray-500">Process video streams in real-time</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={aiSettings.realTimeProcessing || false}
                        onChange={(e) => setAiSettings({ ...aiSettings, realTimeProcessing: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Alerts Settings */}
            {activeTab === 'alerts' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Alert Configuration</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Email Notifications</label>
                      <p className="text-sm text-gray-500">Send alerts via email</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={alertSettings.emailNotifications || false}
                        onChange={(e) => setAlertSettings({ ...alertSettings, emailNotifications: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={alertSettings.emailAddress || ''}
                      onChange={(e) => setAlertSettings({ ...alertSettings, emailAddress: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      disabled={!alertSettings.emailNotifications}
                      placeholder="admin@company.com"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Alert Escalation</label>
                      <p className="text-sm text-gray-500">Enable manual alert escalation</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={alertSettings.escalationEnabled || false}
                        onChange={(e) => setAlertSettings({ ...alertSettings, escalationEnabled: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Escalation Contacts
                    </label>
                    <input
                      type="email"
                      value={alertSettings.escalationContacts || ''}
                      onChange={(e) => setAlertSettings({ ...alertSettings, escalationContacts: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      disabled={!alertSettings.escalationEnabled}
                      placeholder="security@company.com"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Alert Severity Filter
                      </label>
                      <select
                        value={alertSettings.alertSeverityFilter || 'medium'}
                        onChange={(e) => setAlertSettings({ ...alertSettings, alertSeverityFilter: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      >
                        <option value="low">Low and above</option>
                        <option value="medium">Medium and above</option>
                        <option value="high">High and above</option>
                        <option value="critical">Critical only</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Alert Cooldown (seconds)
                      </label>
                      <input
                        type="number"
                        value={alertSettings.alertCooldown || '60'}
                        onChange={(e) => setAlertSettings({ ...alertSettings, alertCooldown: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        min="0"
                        max="300"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Security Settings */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Security Settings</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Audit Logging</label>
                      <p className="text-sm text-gray-500">Log all system activities</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={securitySettings.auditLogging || false}
                        onChange={(e) => setSecuritySettings({ ...securitySettings, auditLogging: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">GDPR Compliance</label>
                      <p className="text-sm text-gray-500">Enable GDPR data protection features</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={securitySettings.gdprCompliance || false}
                        onChange={(e) => setSecuritySettings({ ...securitySettings, gdprCompliance: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Session Timeout (minutes)
                      </label>
                      <input
                        type="number"
                        value={securitySettings.sessionTimeout || '30'}
                        onChange={(e) => setSecuritySettings({ ...securitySettings, sessionTimeout: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        min="5"
                        max="120"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Data Retention (days)
                      </label>
                      <input
                        type="number"
                        value={securitySettings.dataRetention || '365'}
                        onChange={(e) => setSecuritySettings({ ...securitySettings, dataRetention: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        min="30"
                        max="3650"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Network Settings */}
            {activeTab === 'network' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Network Configuration</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      IP Address
                    </label>
                    <input
                      type="text"
                      value={networkSettings.ipAddress || ''}
                      onChange={(e) => setNetworkSettings({ ...networkSettings, ipAddress: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="192.168.1.100"
                      disabled={networkSettings.dhcpEnabled}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Gateway
                    </label>
                    <input
                      type="text"
                      value={networkSettings.gateway || ''}
                      onChange={(e) => setNetworkSettings({ ...networkSettings, gateway: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="192.168.1.1"
                      disabled={networkSettings.dhcpEnabled}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      DNS Server
                    </label>
                    <input
                      type="text"
                      value={networkSettings.dnsServer || ''}
                      onChange={(e) => setNetworkSettings({ ...networkSettings, dnsServer: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="8.8.8.8"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Port Range
                    </label>
                    <input
                      type="text"
                      value={networkSettings.portRange || ''}
                      onChange={(e) => setNetworkSettings({ ...networkSettings, portRange: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="8000-8100"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">DHCP Enabled</label>
                      <p className="text-sm text-gray-500">Automatically obtain IP address</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={networkSettings.dhcpEnabled || false}
                        onChange={(e) => setNetworkSettings({ ...networkSettings, dhcpEnabled: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Bandwidth Monitoring</label>
                      <p className="text-sm text-gray-500">Monitor network bandwidth usage</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={networkSettings.bandwidthMonitoring || false}
                        onChange={(e) => setNetworkSettings({ ...networkSettings, bandwidthMonitoring: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end space-x-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSaveSettings}
            disabled={isSaving}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isSaving ? (
              <>
                <i className="ri-loader-4-line animate-spin mr-2"></i>
                Saving...
              </>
            ) : (
              <>
                <i className="ri-save-line mr-2"></i>
                Save Settings
              </>
            )}
          </button>
        </div>
      </div>

      {/* Success Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
                <i className="ri-check-line text-2xl text-green-600"></i>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Settings Saved!</h3>
              <p className="text-sm text-gray-500">Your settings have been saved to the database.</p>
            </div>
          </div>
        </div>
      )}

      {/* Test Connection Modal */}
      {showTestModal && testResults && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Connection Test Results</h3>
              <button
                onClick={() => setShowTestModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <i className="ri-close-line text-2xl"></i>
              </button>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Database</span>
                <span className={`text-sm ${testResults.database ? 'text-green-600' : 'text-red-600'}`}>
                  {testResults.database ? '✓ Connected' : '✗ Disconnected'}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Storage</span>
                <span className={`text-sm ${testResults.storage ? 'text-green-600' : 'text-red-600'}`}>
                  {testResults.storage ? '✓ Available' : '✗ Unavailable'}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Email Service</span>
                <span className={`text-sm ${testResults.email ? 'text-green-600' : 'text-red-600'}`}>
                  {testResults.email ? '✓ Configured' : '✗ Not Configured'}
                </span>
              </div>
            </div>
            <button
              onClick={() => setShowTestModal(false)}
              className="mt-6 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
