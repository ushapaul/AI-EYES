import { useState, useEffect } from 'react';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Type definitions
interface Alert {
  id: number | string; // Support both MongoDB ObjectId (string) and integer IDs
  type: string;
  location: string;
  timestamp: string;
  severity: string;
  confidence?: number;
  description?: string;
  status?: string;
  image?: string;
}

interface Camera {
  id: string | number;  // Support both MongoDB ObjectId (string) and simple IDs (number)
  name: string;
  location: string;
  status: string;
  url: string;
  type: string;
  image?: string;
}

interface Stats {
  total_cameras?: number;
  active_cameras?: number;
  total_alerts_today?: number;
  detection_accuracy?: number;
  uptime?: string;
}

interface Log {
  id: string | number;
  timestamp: string;
  action: string;
  camera_id: string;
  description?: string;
  level?: string;
  user_agent?: string;
  created_at?: string;
  updated_at?: string;
}

// Simple API hook without WebSocket for now
export const useApi = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  const [cameras, setCameras] = useState<Camera[]>([]);

  const [stats, setStats] = useState<Stats>({});

  const [logs, setLogs] = useState<Log[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Fetch data from backend API
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Test connection to backend
        const response = await fetch('http://localhost:8000/api/status');
        if (response.ok) {
          setIsConnected(true);
          
          // Fetch real data from backend
          const [alertsRes, camerasRes, statsRes, logsRes] = await Promise.all([
            fetch('http://localhost:8000/api/alerts/list'),
            fetch('http://localhost:8000/api/cameras/list'),
            fetch('http://localhost:8000/api/stats'),
            fetch('http://localhost:8000/api/logs')
          ]);

          if (alertsRes.ok) {
            const alertsData = await alertsRes.json();
            setAlerts(alertsData);
          }

          if (camerasRes.ok) {
            const camerasData = await camerasRes.json();
            setCameras(camerasData);
          }

          if (statsRes.ok) {
            const statsData = await statsRes.json();
            setStats(statsData);
          }

          if (logsRes.ok) {
            const logsData = await logsRes.json();
            setLogs(logsData);
          }
        }
      } catch (error) {
        console.log('Backend not available, clearing all data');
        setIsConnected(false);
        // Clear all data when backend is not available
        setAlerts([]);
        setCameras([]);
        setStats({});
        setLogs([]);
      }
    };

    fetchData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const refreshAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/alerts/list');
      if (response.ok) {
        const data = await response.json();
        setAlerts(data);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const refreshCameras = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/cameras/list');
      if (response.ok) {
        const data = await response.json();
        setCameras(data);
      }
    } catch (error) {
      console.error('Error fetching cameras:', error);
    }
  };

  const refreshStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const refreshLogs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/logs');
      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      }
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  const acknowledgeAlert = async (alertId: number | string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Remove acknowledged alert from the list
        setAlerts(prev => prev.filter(alert => alert.id !== alertId));
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const dismissAlert = async (alertId: number | string) => {
    try {
      console.log('Dismissing alert:', alertId);
      const response = await fetch(`http://localhost:8000/api/alerts/${alertId}/dismiss`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Dismiss response status:', response.status);
      const data = await response.json();
      console.log('Dismiss response data:', data);

      if (response.ok) {
        console.log('Alert dismissed successfully, removing from UI');
        // Remove the dismissed alert from the list entirely
        setAlerts(prev => prev.filter(alert => alert.id !== alertId));
      } else {
        console.error('Failed to dismiss alert:', data);
      }
    } catch (error) {
      console.error('Error dismissing alert:', error);
    }
  };

  const escalateAlert = async (alertId: number | string, recipientEmail: string, recipientName: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/alerts/${alertId}/escalate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: recipientEmail,
          name: recipientName,
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        console.log('Alert escalated successfully:', alertId);
        return true;
      } else {
        console.error('Failed to escalate alert:', data);
        return false;
      }
    } catch (error) {
      console.error('Error escalating alert:', error);
      return false;
    }
  };

  return {
    alerts,
    cameras,
    stats,
    logs,
    socket: null,
    refreshAlerts,
    refreshCameras,
    refreshStats,
    refreshLogs,
    acknowledgeAlert,
    dismissAlert,
    escalateAlert,
    isConnected,
  };
};
