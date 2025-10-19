import React, { useState, useEffect } from 'react';
import './SurveillanceConfig.css';

interface DetectionZone {
  id: string;
  name: string;
  points: [number, number][];
  zone_type: string;
  activity_types: string[];
}

interface KnownPerson {
  id: string;
  name: string;
  images_count: number;
  last_seen?: string;
}

interface SurveillanceSettings {
  confidence_threshold: number;
  loitering_time_threshold: number;
  face_recognition_threshold: number;
  email_alerts_enabled: boolean;
  alert_cooldown: number;
}

const SurveillanceConfig: React.FC = () => {
  const [zones, setZones] = useState<DetectionZone[]>([]);
  const [knownPersons, setKnownPersons] = useState<KnownPerson[]>([]);
  const [settings, setSettings] = useState<SurveillanceSettings>({
    confidence_threshold: 0.5,
    loitering_time_threshold: 30,
    face_recognition_threshold: 100,
    email_alerts_enabled: true,
    alert_cooldown: 60
  });
  const [activeTab, setActiveTab] = useState<'zones' | 'faces' | 'settings'>('zones');
  const [loading, setLoading] = useState(false);

  // Fetch configuration data
  const fetchData = async () => {
    try {
      // Fetch detection zones
      const zonesResponse = await fetch('/api/surveillance/detection_zones');
      if (zonesResponse.ok) {
        const zonesData = await zonesResponse.json();
        setZones(zonesData.zones || []);
      }

      // Fetch known persons
      const personsResponse = await fetch('/api/surveillance/known_faces');
      if (personsResponse.ok) {
        const personsData = await personsResponse.json();
        setKnownPersons(personsData.persons || []);
      }

      // Fetch settings
      const settingsResponse = await fetch('/api/surveillance/settings');
      if (settingsResponse.ok) {
        const settingsData = await settingsResponse.json();
        setSettings(settingsData);
      }
    } catch (error) {
      console.error('Failed to fetch configuration:', error);
    }
  };

  // Add new detection zone
  const addZone = async () => {
    const name = prompt('Enter zone name:');
    if (!name) return;

    const newZone = {
      name,
      points: [[100, 100], [300, 100], [300, 200], [100, 200]], // Default rectangle
      zone_type: 'monitored',
      activity_types: ['LOITERING', 'UNAUTHORIZED_PERSON']
    };

    try {
      const response = await fetch('/api/surveillance/detection_zones', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newZone)
      });

      if (response.ok) {
        fetchData(); // Refresh data
      } else {
        alert('Failed to add zone');
      }
    } catch (error) {
      console.error('Failed to add zone:', error);
      alert('Failed to add zone');
    }
  };

  // Delete detection zone
  const deleteZone = async (zoneId: string) => {
    if (!confirm('Are you sure you want to delete this zone?')) return;

    try {
      const response = await fetch(`/api/surveillance/detection_zones/${zoneId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        fetchData(); // Refresh data
      } else {
        alert('Failed to delete zone');
      }
    } catch (error) {
      console.error('Failed to delete zone:', error);
      alert('Failed to delete zone');
    }
  };

  // Add new known person
  const addPerson = async () => {
    const name = prompt('Enter person name:');
    if (!name) return;

    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'image/*';
    
    input.onchange = async (e) => {
      const files = (e.target as HTMLInputElement).files;
      if (!files || files.length === 0) return;

      const formData = new FormData();
      formData.append('name', name);
      
      for (let i = 0; i < files.length; i++) {
        formData.append('images', files[i]);
      }

      try {
        setLoading(true);
        const response = await fetch('/api/surveillance/known_faces', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          fetchData(); // Refresh data
          alert(`Added ${files.length} images for ${name}`);
        } else {
          alert('Failed to add person');
        }
      } catch (error) {
        console.error('Failed to add person:', error);
        alert('Failed to add person');
      } finally {
        setLoading(false);
      }
    };

    input.click();
  };

  // Delete known person
  const deletePerson = async (personId: string) => {
    if (!confirm('Are you sure you want to delete this person?')) return;

    try {
      const response = await fetch(`/api/surveillance/known_faces/${personId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        fetchData(); // Refresh data
      } else {
        alert('Failed to delete person');
      }
    } catch (error) {
      console.error('Failed to delete person:', error);
      alert('Failed to delete person');
    }
  };

  // Update settings
  const updateSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/surveillance/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        alert('Settings updated successfully');
      } else {
        alert('Failed to update settings');
      }
    } catch (error) {
      console.error('Failed to update settings:', error);
      alert('Failed to update settings');
    } finally {
      setLoading(false);
    }
  };

  // Train face recognition model
  const trainModel = async () => {
    if (!confirm('This will retrain the face recognition model. Continue?')) return;

    try {
      setLoading(true);
      const response = await fetch('/api/surveillance/train_faces', {
        method: 'POST'
      });

      if (response.ok) {
        alert('Face recognition model trained successfully');
      } else {
        alert('Failed to train model');
      }
    } catch (error) {
      console.error('Failed to train model:', error);
      alert('Failed to train model');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="surveillance-config">
      <div className="config-header">
        <h1>⚙️ Surveillance Configuration</h1>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'zones' ? 'active' : ''}`}
          onClick={() => setActiveTab('zones')}
        >
          🗺️ Detection Zones
        </button>
        <button
          className={`tab-button ${activeTab === 'faces' ? 'active' : ''}`}
          onClick={() => setActiveTab('faces')}
        >
          👥 Known Faces
        </button>
        <button
          className={`tab-button ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
      </div>

      {/* Detection Zones Tab */}
      {activeTab === 'zones' && (
        <div className="tab-content">
          <div className="section-header">
            <h2>Detection Zones</h2>
            <button className="add-button" onClick={addZone}>
              ➕ Add Zone
            </button>
          </div>

          <div className="zones-grid">
            {zones.length === 0 ? (
              <div className="empty-state">
                <div>🗺️</div>
                <p>No detection zones configured</p>
                <span>Add zones to monitor specific areas</span>
              </div>
            ) : (
              zones.map((zone) => (
                <div key={zone.id} className="zone-card">
                  <div className="zone-header">
                    <h3>{zone.name}</h3>
                    <button
                      className="delete-button"
                      onClick={() => deleteZone(zone.id)}
                    >
                      🗑️
                    </button>
                  </div>
                  <div className="zone-info">
                    <p><strong>Type:</strong> {zone.zone_type}</p>
                    <p><strong>Activities:</strong> {zone.activity_types.join(', ')}</p>
                    <p><strong>Points:</strong> {zone.points.length} coordinates</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Known Faces Tab */}
      {activeTab === 'faces' && (
        <div className="tab-content">
          <div className="section-header">
            <h2>Known Faces</h2>
            <div className="face-actions">
              <button className="add-button" onClick={addPerson} disabled={loading}>
                👤 Add Person
              </button>
              <button className="train-button" onClick={trainModel} disabled={loading}>
                🧠 Train Model
              </button>
            </div>
          </div>

          <div className="persons-grid">
            {knownPersons.length === 0 ? (
              <div className="empty-state">
                <div>👥</div>
                <p>No known faces configured</p>
                <span>Add known persons to enable face recognition</span>
              </div>
            ) : (
              knownPersons.map((person) => (
                <div key={person.id} className="person-card">
                  <div className="person-header">
                    <h3>{person.name}</h3>
                    <button
                      className="delete-button"
                      onClick={() => deletePerson(person.id)}
                    >
                      🗑️
                    </button>
                  </div>
                  <div className="person-info">
                    <p><strong>Images:</strong> {person.images_count}</p>
                    {person.last_seen && (
                      <p><strong>Last seen:</strong> {new Date(person.last_seen).toLocaleString()}</p>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="tab-content">
          <div className="section-header">
            <h2>Settings</h2>
            <button className="save-button" onClick={updateSettings} disabled={loading}>
              💾 Save Settings
            </button>
          </div>

          <div className="settings-form">
            <div className="setting-group">
              <label>Detection Confidence Threshold</label>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={settings.confidence_threshold}
                onChange={(e) => setSettings({
                  ...settings,
                  confidence_threshold: parseFloat(e.target.value)
                })}
              />
              <span className="range-value">{settings.confidence_threshold}</span>
            </div>

            <div className="setting-group">
              <label>Loitering Time Threshold (seconds)</label>
              <input
                type="number"
                min="10"
                max="300"
                value={settings.loitering_time_threshold}
                onChange={(e) => setSettings({
                  ...settings,
                  loitering_time_threshold: parseInt(e.target.value)
                })}
              />
            </div>

            <div className="setting-group">
              <label>Face Recognition Threshold</label>
              <input
                type="range"
                min="50"
                max="150"
                step="5"
                value={settings.face_recognition_threshold}
                onChange={(e) => setSettings({
                  ...settings,
                  face_recognition_threshold: parseInt(e.target.value)
                })}
              />
              <span className="range-value">{settings.face_recognition_threshold}</span>
            </div>

            <div className="setting-group">
              <label>Alert Cooldown (seconds)</label>
              <input
                type="number"
                min="30"
                max="600"
                value={settings.alert_cooldown}
                onChange={(e) => setSettings({
                  ...settings,
                  alert_cooldown: parseInt(e.target.value)
                })}
              />
            </div>

            <div className="setting-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={settings.email_alerts_enabled}
                  onChange={(e) => setSettings({
                    ...settings,
                    email_alerts_enabled: e.target.checked
                  })}
                />
                Enable Email Alerts
              </label>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">⏳ Processing...</div>
        </div>
      )}
    </div>
  );
};

export default SurveillanceConfig;