import { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';

interface Alert {
  id: number;
  type: string;
  location: string;
  timestamp: string;
  severity: string;
  confidence: number;
  description: string;
  image_path?: string;
  status: string;
}

interface CameraData {
  id: number;
  name: string;
  location: string;
  status: string;
  url: string;
  type: string;
}

interface SystemStats {
  total_cameras: number;
  active_cameras: number;
  total_alerts_today: number;
  detection_accuracy: number;
  uptime: string;
}

interface UseApiReturn {
  alerts: Alert[];
  cameras: CameraData[];
  stats: SystemStats | null;
  logs: any[];
  socket: Socket | null;
  refreshAlerts: () => Promise<void>;
  refreshCameras: () => Promise<void>;
  refreshStats: () => Promise<void>;
  acknowledgeAlert: (alertId: number) => Promise<void>;
  dismissAlert: (alertId: number) => Promise<void>;
  isConnected: boolean;
}

export const useApi = (): UseApiReturn => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [cameras, setCameras] = useState<CameraData[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [logs] = useState([]);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const API_BASE_URL = 'http://localhost:8000/api';

  useEffect(() => {
    // Initialize socket connection
    const socketInstance = io('http://localhost:8000');
    
    socketInstance.on('connect', () => {
      console.log('Connected to server');
      setIsConnected(true);
    });

    socketInstance.on('disconnect', () => {
      console.log('Disconnected from server');
      setIsConnected(false);
    });

    socketInstance.on('new_alert', (alertData: Alert) => {
      console.log('New alert received:', alertData);
      setAlerts(prev => [alertData, ...prev]);
      
      // Show browser notification if permission granted
      if (Notification.permission === 'granted') {
        new Notification('Security Alert', {
          body: alertData.description,
          icon: '/favicon.ico'
        });
      }
    });

    socketInstance.on('camera_status_update', (cameraData: any) => {
      setCameras(prev => 
        prev.map(camera => 
          camera.id === cameraData.id 
            ? { ...camera, status: cameraData.status }
            : camera
        )
      );
    });

    setSocket(socketInstance);

    // Initial data fetch
    refreshAlerts();
    refreshCameras();
    refreshStats();

    // Request notification permission
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }

    return () => {
      socketInstance.disconnect();
    };
  }, []);

  const refreshAlerts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/list`);
      const data = await response.json();
      setAlerts(data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const refreshCameras = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/camera/list`);
      const data = await response.json();
      setCameras(data);
    } catch (error) {
      console.error('Error fetching cameras:', error);
    }
  };

  const refreshStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const acknowledgeAlert = async (alertId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setAlerts(prev =>
          prev.map(alert =>
            alert.id === alertId
              ? { ...alert, status: 'acknowledged' }
              : alert
          )
        );
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const dismissAlert = async (alertId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/${alertId}/dismiss`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setAlerts(prev =>
          prev.map(alert =>
            alert.id === alertId
              ? { ...alert, status: 'dismissed' }
              : alert
          )
        );
      }
    } catch (error) {
      console.error('Error dismissing alert:', error);
    }
  };

  return {
    alerts,
    cameras,
    stats,
    logs,
    socket,
    refreshAlerts,
    refreshCameras,
    refreshStats,
    acknowledgeAlert,
    dismissAlert,
    isConnected,
  };
};