import React, { useState } from 'react';
import StreamTester from './StreamTester';
import IPWebcamGuide from './IPWebcamGuide';

interface ProtectedCameraManagerProps {
  onClose?: () => void;
}

const ProtectedCameraManager: React.FC<ProtectedCameraManagerProps> = ({ onClose }) => {
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState('');
  const [cameras, setCameras] = useState<any[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<any>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [newCamera, setNewCamera] = useState({
    name: '',
    location: '',
    url: '',
    type: 'farm',
    username: '',
    password: ''
  });

  const API_BASE_URL = 'http://localhost:8000/api/v2';

  const handleLogin = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password })
      });

      const data = await response.json();
      
      if (data.success) {
        setIsAuthenticated(true);
        setAuthToken(data.token);
        alert('Login successful!');
        loadCameras();
      } else {
        alert('Invalid password: ' + data.message);
      }
    } catch (error) {
      alert('Login failed: ' + error);
    }
  };

  const loadCameras = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/cameras`);
      const data = await response.json();
      
      if (data.success) {
        setCameras(data.cameras);
      }
    } catch (error) {
      console.error('Failed to load cameras:', error);
    }
  };

  const createCamera = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/cameras`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newCamera,
          password: password // Use admin password for auth
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Camera created successfully!');
        setNewCamera({
          name: '',
          location: '',
          url: '',
          type: 'farm',
          username: '',
          password: ''
        });
        loadCameras();
      } else {
        alert('Failed to create camera: ' + data.error);
      }
    } catch (error) {
      alert('Error creating camera: ' + error);
    }
  };

  const updateCamera = async () => {
    if (!selectedCamera) return;

    try {
      const response = await fetch(`${API_BASE_URL}/cameras/${selectedCamera.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...selectedCamera,
          password: password // Use admin password for auth
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Camera updated successfully!');
        setIsEditing(false);
        setSelectedCamera(null);
        loadCameras();
      } else {
        alert('Failed to update camera: ' + data.error);
      }
    } catch (error) {
      alert('Error updating camera: ' + error);
    }
  };

  const deleteCamera = async (cameraId: string) => {
    if (!confirm('Are you sure you want to delete this camera?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/cameras/${cameraId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Camera deleted successfully!');
        loadCameras();
      } else {
        alert('Failed to delete camera: ' + data.error);
      }
    } catch (error) {
      alert('Error deleting camera: ' + error);
    }
  };

  const captureSnapshot = async (cameraId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/cameras/${cameraId}/snapshot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        }
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Snapshot captured successfully!');
      } else {
        alert('Failed to capture snapshot: ' + data.error);
      }
    } catch (error) {
      alert('Error capturing snapshot: ' + error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-8 rounded-lg max-w-md w-full">
          <h2 className="text-2xl font-bold mb-4">Admin Authentication</h2>
          <p className="text-gray-600 mb-4">Enter admin password to manage cameras:</p>
          
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Admin password"
            className="w-full p-3 border rounded-lg mb-4"
            onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
          />
          
          <div className="flex space-x-4">
            <button
              onClick={handleLogin}
              className="flex-1 bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600"
            >
              Login
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="flex-1 bg-gray-500 text-white p-3 rounded-lg hover:bg-gray-600"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-8 rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Protected Camera Management</h2>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          )}
        </div>

        {/* Create New Camera */}
        <div className="mb-8 p-6 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Create New Camera</h3>
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Camera Name"
              value={newCamera.name}
              onChange={(e) => setNewCamera({...newCamera, name: e.target.value})}
              className="p-2 border rounded"
            />
            <input
              type="text"
              placeholder="Location"
              value={newCamera.location}
              onChange={(e) => setNewCamera({...newCamera, location: e.target.value})}
              className="p-2 border rounded"
            />
            <input
              type="text"
              placeholder="Camera URL (e.g., http://192.168.1.100:8080)"
              value={newCamera.url}
              onChange={(e) => setNewCamera({...newCamera, url: e.target.value})}
              className="p-2 border rounded"
            />
            <div className="col-span-2">
              <IPWebcamGuide />
            </div>
            <select
              value={newCamera.type}
              onChange={(e) => setNewCamera({...newCamera, type: e.target.value})}
              className="p-2 border rounded"
            >
              <option value="farm">Farm</option>
              <option value="security">Security</option>
              <option value="monitoring">Monitoring</option>
            </select>
            <input
              type="text"
              placeholder="Username (optional)"
              value={newCamera.username}
              onChange={(e) => setNewCamera({...newCamera, username: e.target.value})}
              className="p-2 border rounded"
            />
            <input
              type="password"
              placeholder="Camera Password (optional)"
              value={newCamera.password}
              onChange={(e) => setNewCamera({...newCamera, password: e.target.value})}
              className="p-2 border rounded"
            />
          </div>
          
          {/* Stream URL Tester */}
          {newCamera.url && newCamera.url.startsWith('http') && (
            <div className="mt-4">
              <StreamTester 
                baseUrl={newCamera.url.replace(/\/(video|videofeed|shot\.jpg|stream|mjpeg|cam\.mjpg).*$/, '')}
                onUrlFound={(workingUrl) => setNewCamera({...newCamera, url: workingUrl})}
              />
            </div>
          )}
          
          <button
            onClick={createCamera}
            className="mt-4 bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
          >
            Create Camera
          </button>
        </div>

        {/* Camera List */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Existing Cameras ({cameras.length})</h3>
          <div className="space-y-4">
            {cameras.map((camera) => (
              <div key={camera.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-semibold">{camera.name}</h4>
                    <p className="text-gray-600">{camera.location}</p>
                    <p className="text-sm text-gray-500">{camera.url}</p>
                    <span className={`inline-block px-2 py-1 rounded text-xs ${
                      camera.enabled !== false ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {camera.enabled !== false ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {setSelectedCamera({...camera}); setIsEditing(true);}}
                      className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => captureSnapshot(camera.id)}
                      className="bg-purple-500 text-white px-3 py-1 rounded text-sm hover:bg-purple-600"
                    >
                      Snapshot
                    </button>
                    <button
                      onClick={() => deleteCamera(camera.id)}
                      className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Edit Camera Modal */}
        {isEditing && selectedCamera && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
            <div className="bg-white p-6 rounded-lg max-w-md w-full">
              <h3 className="text-lg font-semibold mb-4">Edit Camera</h3>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Camera Name"
                  value={selectedCamera.name}
                  onChange={(e) => setSelectedCamera({...selectedCamera, name: e.target.value})}
                  className="w-full p-2 border rounded"
                />
                <input
                  type="text"
                  placeholder="Location"
                  value={selectedCamera.location}
                  onChange={(e) => setSelectedCamera({...selectedCamera, location: e.target.value})}
                  className="w-full p-2 border rounded"
                />
                <input
                  type="text"
                  placeholder="Camera URL"
                  value={selectedCamera.url}
                  onChange={(e) => setSelectedCamera({...selectedCamera, url: e.target.value})}
                  className="w-full p-2 border rounded"
                />
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedCamera.enabled !== false}
                    onChange={(e) => setSelectedCamera({...selectedCamera, enabled: e.target.checked})}
                    className="mr-2"
                  />
                  Enabled
                </label>
              </div>
              <div className="flex space-x-4 mt-6">
                <button
                  onClick={updateCamera}
                  className="flex-1 bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                >
                  Update
                </button>
                <button
                  onClick={() => {setIsEditing(false); setSelectedCamera(null);}}
                  className="flex-1 bg-gray-500 text-white p-2 rounded hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProtectedCameraManager;