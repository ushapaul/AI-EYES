import React, { useState, useEffect, useRef } from 'react';
import './SurveillanceDashboard.css';

interface SurveillanceStats {
  active: boolean;
  fps: number;
  persons_detected: number;
  faces_recognized: number;
  activities_detected: number;
  active_tracks: number;
}

interface DetectionActivity {
  id: string;
  timestamp: string;
  activity_type: string;
  threat_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  location: [number, number];
  zone_name: string;
  person_id?: number;
  confidence: number;
}

const SurveillanceDashboard: React.FC = () => {
  const [isActive, setIsActive] = useState(false);
  const [stats, setStats] = useState<SurveillanceStats | null>(null);
  const [activities, setActivities] = useState<DetectionActivity[]>([]);
  const [loading, setLoading] = useState(false);
  const videoRef = useRef<HTMLImageElement>(null);
  const [videoError, setVideoError] = useState(false);

  // Fetch surveillance status and stats
  const fetchStats = async () => {
    try {
      const response = await fetch('/api/surveillance/status');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
        setIsActive(data.active);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  // Fetch recent activities
  const fetchActivities = async () => {
    try {
      const response = await fetch('/api/surveillance/activities?limit=10');
      if (response.ok) {
        const data = await response.json();
        setActivities(data.activities || []);
      }
    } catch (error) {
      console.error('Failed to fetch activities:', error);
    }
  };

  // Start surveillance
  const startSurveillance = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/surveillance/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        setIsActive(true);
        startVideoStream();
      } else {
        const error = await response.json();
        alert(`Failed to start surveillance: ${error.message}`);
      }
    } catch (error) {
      console.error('Failed to start surveillance:', error);
      alert('Failed to start surveillance');
    } finally {
      setLoading(false);
    }
  };

  // Stop surveillance
  const stopSurveillance = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/surveillance/stop', {
        method: 'POST'
      });
      
      if (response.ok) {
        setIsActive(false);
        stopVideoStream();
      }
    } catch (error) {
      console.error('Failed to stop surveillance:', error);
    } finally {
      setLoading(false);
    }
  };

  // Video streaming
  const startVideoStream = () => {
    if (videoRef.current) {
      videoRef.current.src = '/api/surveillance/live_frame?' + Date.now();
      setVideoError(false);
      
      // Refresh video frame every 100ms for smooth streaming
      const interval = setInterval(() => {
        if (videoRef.current && isActive) {
          videoRef.current.src = '/api/surveillance/live_frame?' + Date.now();
        } else {
          clearInterval(interval);
        }
      }, 100);
    }
  };

  const stopVideoStream = () => {
    if (videoRef.current) {
      videoRef.current.src = '';
    }
  };

  // Handle video load error
  const handleVideoError = () => {
    setVideoError(true);
  };

  // Get threat level color
  const getThreatColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'threat-low';
      case 'MEDIUM': return 'threat-medium';
      case 'HIGH': return 'threat-high';
      case 'CRITICAL': return 'threat-critical';
      default: return 'threat-unknown';
    }
  };

  // Polling for updates
  useEffect(() => {
    fetchStats();
    fetchActivities();
    
    const interval = setInterval(() => {
      fetchStats();
      fetchActivities();
    }, 2000); // Update every 2 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="surveillance-dashboard">
      <div className="dashboard-header">
        <h1>🔍 AI Eyes Surveillance</h1>
        
        <div className="header-controls">
          <span className={`status-badge ${isActive ? 'active' : 'inactive'}`}>
            {isActive ? '🟢 ACTIVE' : '🔴 INACTIVE'}
          </span>
          
          <button
            onClick={isActive ? stopSurveillance : startSurveillance}
            disabled={loading}
            className={`control-button ${isActive ? 'stop' : 'start'}`}
          >
            {loading ? '⏳' : isActive ? '⏹️ Stop' : '▶️ Start'}
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📹</div>
          <div className="stat-info">
            <p className="stat-label">Processing FPS</p>
            <p className="stat-value">{stats?.fps?.toFixed(1) || '0.0'}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-info">
            <p className="stat-label">Active Tracks</p>
            <p className="stat-value">{stats?.active_tracks || 0}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🛡️</div>
          <div className="stat-info">
            <p className="stat-label">Faces Recognized</p>
            <p className="stat-value">{stats?.faces_recognized || 0}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-info">
            <p className="stat-label">Activities</p>
            <p className="stat-value">{stats?.activities_detected || 0}</p>
          </div>
        </div>
      </div>

      {/* Live Video Feed and Recent Activities */}
      <div className="main-content">
        {/* Live Video Feed */}
        <div className="video-section">
          <div className="section-header">
            <h2>📹 Live Feed</h2>
          </div>
          <div className="video-container">
            {isActive ? (
              <>
                <img
                  ref={videoRef}
                  className="video-feed"
                  alt="Live surveillance feed"
                  onError={handleVideoError}
                />
                {videoError && (
                  <div className="video-error">
                    <div>📹</div>
                    <p>Video feed unavailable</p>
                  </div>
                )}
                <div className="live-indicator">🔴 LIVE</div>
              </>
            ) : (
              <div className="video-placeholder">
                <div>📹</div>
                <p>Surveillance Inactive</p>
                <span>Start surveillance to view live feed</span>
              </div>
            )}
          </div>
        </div>

        {/* Recent Activities */}
        <div className="activities-section">
          <div className="section-header">
            <h2>⚠️ Recent Activities</h2>
          </div>
          <div className="activities-list">
            {activities.length === 0 ? (
              <div className="no-activities">
                <div>🛡️</div>
                <p>No recent activities</p>
              </div>
            ) : (
              activities.map((activity) => (
                <div key={activity.id} className="activity-item">
                  <div className="activity-content">
                    <div className="activity-header">
                      <span className={`threat-badge ${getThreatColor(activity.threat_level)}`}>
                        {activity.threat_level}
                      </span>
                      <span className="zone-name">{activity.zone_name}</span>
                      <span className="timestamp">
                        {new Date(activity.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="activity-type">{activity.activity_type.replace('_', ' ')}</p>
                    <p className="activity-description">{activity.description}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SurveillanceDashboard;