import { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

export interface SettingsData {
  system?: {
    systemName: string;
    timezone: string;
    language: string;
    dateFormat: string;
    timeFormat: string;
    autoBackup: boolean;
    backupFrequency: string;
    backupRetention: string;
    systemUpdates: string;
    maintenanceMode: boolean;
    debugMode: boolean;
    logLevel: string;
  };
  camera?: {
    defaultResolution: string;
    frameRate: string;
    compressionLevel: string;
    nightVision: boolean;
    motionDetection: boolean;
    motionSensitivity: string;
    recordingMode: string;
    recordingQuality: string;
    storageLocation: string;
    maxStorageSize: string;
    autoDelete: boolean;
    retentionDays: string;
    streamingEnabled: boolean;
    streamingQuality: string;
    bandwidthLimit: string;
  };
  ai?: {
    faceRecognition: boolean;
    faceRecognitionModel: string;
    faceRecognitionThreshold: string;
    objectDetection: boolean;
    objectDetectionModel: string;
    objectDetectionThreshold: string;
    behaviorAnalysis: boolean;
    behaviorSensitivity: string;
    realTimeProcessing: boolean;
    batchProcessing: boolean;
    gpuAcceleration: boolean;
    modelUpdateFrequency: string;
    trainingDataCollection: boolean;
    anonymizeData: boolean;
    confidenceThreshold: string;
  };
  alerts?: {
    emailNotifications: boolean;
    emailAddress: string;
    smsNotifications: boolean;
    smsNumber: string;
    pushNotifications: boolean;
    webhookUrl: string;
    alertSeverityFilter: string;
    alertFrequencyLimit: string;
    alertCooldown: string;
    escalationEnabled: boolean;
    escalationDelay: string;
    escalationContacts: string;
    soundAlerts: boolean;
    alertVolume: string;
    customAlertTones: boolean;
    alertHistory: string;
  };
  security?: {
    twoFactorAuth: boolean;
    sessionTimeout: string;
    passwordPolicy: string;
    loginAttempts: string;
    accountLockout: string;
    ipWhitelist: string;
    sslEnabled: boolean;
    encryptionLevel: string;
    auditLogging: boolean;
    accessLogging: boolean;
    dataRetention: string;
    gdprCompliance: boolean;
    anonymizePersonalData: boolean;
    dataExportEnabled: boolean;
    apiAccess: boolean;
  };
  network?: {
    networkInterface: string;
    ipAddress: string;
    subnetMask: string;
    gateway: string;
    dnsServer: string;
    dhcpEnabled: boolean;
    portRange: string;
    firewallEnabled: boolean;
    vpnEnabled: boolean;
    vpnServer: string;
    bandwidthMonitoring: boolean;
    networkDiagnostics: boolean;
    connectionTimeout: string;
    retryAttempts: string;
    proxyEnabled: boolean;
  };
}

export const useSettings = () => {
  const [settings, setSettings] = useState<SettingsData>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/settings`);
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
        setError(null);
      } else {
        setError('Failed to fetch settings');
      }
    } catch (err) {
      setError('Failed to connect to backend');
      console.error('Error fetching settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = async (category: string, data: any): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/${category}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        // Refresh settings after update
        await fetchSettings();
        return true;
      }
      return false;
    } catch (err) {
      console.error(`Error updating ${category} settings:`, err);
      return false;
    }
  };

  const backupSettings = async (): Promise<{ success: boolean; backup?: any }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/backup`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        return { success: true, backup: data.backup };
      }
      return { success: false };
    } catch (err) {
      console.error('Error backing up settings:', err);
      return { success: false };
    }
  };

  const restoreSettings = async (backupData: any): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/restore`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backupData),
      });

      if (response.ok) {
        await fetchSettings();
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error restoring settings:', err);
      return false;
    }
  };

  const testConnection = async (): Promise<{ success: boolean; results?: any }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/test-connection`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        return { success: true, results: data.results };
      }
      return { success: false };
    } catch (err) {
      console.error('Error testing connection:', err);
      return { success: false };
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  return {
    settings,
    loading,
    error,
    updateSettings,
    backupSettings,
    restoreSettings,
    testConnection,
    refreshSettings: fetchSettings,
  };
};
