
import { useState, useEffect } from 'react';
import ProtectedCameraManager from './ProtectedCameraManager';

interface Camera {
  id: string | number;  // Support both MongoDB ObjectId (string) and simple IDs (number)
  name: string;
  location: string;
  status: string;
  url?: string;
  type?: string;
  image?: string;
}

interface LiveStreamsProps {
  cameras?: Camera[];
  onRefreshCameras?: () => Promise<void>;
}

export default function LiveStreams({ cameras: propCameras, onRefreshCameras }: LiveStreamsProps) {
  const [showFullscreenModal, setShowFullscreenModal] = useState(false);
  const [fullscreenCamera, setFullscreenCamera] = useState<Camera | null>(null);
  const [showAddCameraModal, setShowAddCameraModal] = useState(false);
  const [showProtectedManager, setShowProtectedManager] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newCamera, setNewCamera] = useState({
    name: '',
    location: '',
    url: '',
    type: 'farm' as 'farm' | 'bank',
    username: '',
    password: '',
    ai_mode: 'both' as 'face_recognition' | 'yolov9' | 'both'
  });
  
  // Recording state management
  const [recordingCameras, setRecordingCameras] = useState<Set<string | number>>(new Set());
  const [recordingStartTimes, setRecordingStartTimes] = useState<Map<string | number, number>>(new Map());
  const [recordingDurations, setRecordingDurations] = useState<Map<string | number, string>>(new Map());
  
  // Modals state
  const [showSnapshotModal, setShowSnapshotModal] = useState(false);
  const [snapshotData, setSnapshotData] = useState<{url: string, path: string} | null>(null);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [settingsCamera, setSettingsCamera] = useState<Camera | null>(null);
  const [showRecordingsModal, setShowRecordingsModal] = useState(false);
  const [recordings, setRecordings] = useState<any[]>([]);
  const [loadingRecordings, setLoadingRecordings] = useState(false);

  // Use only prop cameras (from API), no mock data
  const cameras = propCameras || [];

  // Sync recording status on mount and when cameras change
  useEffect(() => {
    const syncRecordingStatus = async () => {
      for (const camera of cameras) {
        try {
          const response = await fetch(`http://localhost:8000/api/camera/${camera.id}/recording-status`);
          if (response.ok) {
            const status = await response.json();
            // Backend returns 'is_recording' not 'recording'
            if (status.is_recording || status.recording) {
              // Update state to show this camera is recording
              setRecordingCameras(prev => new Set(prev).add(camera.id));
              setRecordingStartTimes(prev => new Map(prev).set(camera.id, Date.now()));
            }
          }
        } catch (error) {
          console.error(`Failed to check recording status for camera ${camera.id}:`, error);
        }
      }
    };

    if (cameras.length > 0) {
      syncRecordingStatus();
    }
  }, [cameras]);

  const handleAddCamera = () => {
    setShowAddCameraModal(true);
  };

  const handleSaveCamera = async () => {
    if (!newCamera.name || !newCamera.location || !newCamera.url) {
      alert('Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);
    try {
      // Ensure URL has /video endpoint for IP Webcam
      let cameraUrl = newCamera.url.trim();
      
      // Convert https to http (IP Webcam uses http)
      if (cameraUrl.startsWith('https://')) {
        cameraUrl = cameraUrl.replace('https://', 'http://');
      }
      
      // Add /video if not present
      if (!cameraUrl.includes('/video') && !cameraUrl.includes('/videofeed')) {
        cameraUrl = cameraUrl.endsWith('/') ? cameraUrl + 'video' : cameraUrl + '/video';
      }
      
      // In a real system, this would make an API call to add the camera
      const response = await fetch('http://localhost:8000/api/camera/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newCamera,
          url: cameraUrl  // Use the fixed URL
        })
      });

      if (response.ok) {
        await response.json(); // Parse response to ensure it's valid
        alert(`Camera "${newCamera.name}" added successfully!\nURL: ${cameraUrl}`);
        setShowAddCameraModal(false);
        setNewCamera({
          name: '',
          location: '',
          url: '',
          type: 'farm',
          username: '',
          password: '',
          ai_mode: 'both'
        });
        // Refresh the camera list to show the new camera immediately
        if (onRefreshCameras) {
          await onRefreshCameras();
        }
      } else {
        const error = await response.json();
        alert(`Failed to add camera: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error adding camera:', error);
      alert('Error adding camera. Please check your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelAddCamera = () => {
    setShowAddCameraModal(false);
    setNewCamera({
      name: '',
      location: '',
      url: '',
      type: 'farm',
      username: '',
      password: '',
      ai_mode: 'both'
    });
  };

  const handleTakeSnapshot = async (cameraId: string | number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/camera/${cameraId}/snapshot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const result = await response.json();
        // Show snapshot preview modal
        setSnapshotData({
          url: `http://localhost:8000${result.image_url}`,
          path: result.image_path
        });
        setShowSnapshotModal(true);
      } else {
        const error = await response.json();
        alert(`Failed to capture snapshot: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error taking snapshot:', error);
      alert('Error capturing snapshot. Please check your connection and try again.');
    }
  };

  const handleRecording = async (cameraId: string | number) => {
    try {
      // Check current recording status first
      const statusResponse = await fetch(`http://localhost:8000/api/camera/${cameraId}/recording-status`);
      
      if (!statusResponse.ok) {
        alert('Failed to check recording status');
        return;
      }
      
      const status = await statusResponse.json();
      
      // Backend returns 'is_recording' not 'recording'
      if (status.is_recording || status.recording) {
        // Camera is recording - STOP it
        const stopResponse = await fetch(`http://localhost:8000/api/camera/${cameraId}/stop-recording`, {
          method: 'POST',
        });
        
        if (stopResponse.ok) {
          const result = await stopResponse.json();
          
          // Update recording state - REMOVE from recording
          setRecordingCameras(prev => {
            const updated = new Set(prev);
            updated.delete(cameraId);
            return updated;
          });
          setRecordingStartTimes(prev => {
            const updated = new Map(prev);
            updated.delete(cameraId);
            return updated;
          });
          setRecordingDurations(prev => {
            const updated = new Map(prev);
            updated.delete(cameraId);
            return updated;
          });
          
          alert(`Recording stopped! Video saved to: ${result.filename}`);
        } else {
          const error = await stopResponse.json();
          console.error('Failed to stop recording:', error);
          alert(`Failed to stop recording: ${error.error || 'Unknown error'}`);
        }
      } else {
        // Camera is NOT recording - START it
        const startResponse = await fetch(`http://localhost:8000/api/camera/${cameraId}/start-recording`, {
          method: 'POST',
        });
        
        if (startResponse.ok) {
          // Update recording state - ADD to recording
          setRecordingCameras(prev => new Set(prev).add(cameraId));
          setRecordingStartTimes(prev => new Map(prev).set(cameraId, Date.now()));
          
          // Start duration timer
          setInterval(() => {
            setRecordingDurations(prev => {
              const updated = new Map(prev);
              const startTime = recordingStartTimes.get(cameraId);
              if (startTime) {
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                updated.set(cameraId, `${minutes}:${seconds.toString().padStart(2, '0')}`);
              }
              return updated;
            });
          }, 1000);
          
          alert('Recording started successfully!');
        } else {
          const errorData = await startResponse.json();
          if (errorData.error && errorData.error.includes('already recording')) {
            alert('This camera is already recording! The red button shows it\'s active. Click it again to stop.');
            // Force update the UI to show recording state
            setRecordingCameras(prev => new Set(prev).add(cameraId));
            setRecordingStartTimes(prev => new Map(prev).set(cameraId, Date.now()));
          } else {
            alert(`Failed to start recording: ${errorData.error || 'Unknown error'}`);
          }
        }
      }
    } catch (error) {
      console.error('Error managing recording:', error);
      alert('Error managing recording. Please check your connection and try again.');
    }
  };

  const handleSettings = (camera: Camera) => {
    setSettingsCamera(camera);
    setShowSettingsModal(true);
  };

  const fetchRecordings = async () => {
    setLoadingRecordings(true);
    try {
      const response = await fetch('http://localhost:8000/api/recordings/list');
      if (response.ok) {
        const data = await response.json();
        setRecordings(data.recordings || []);
      } else {
        console.error('Failed to fetch recordings');
        setRecordings([]);
      }
    } catch (error) {
      console.error('Error fetching recordings:', error);
      setRecordings([]);
    } finally {
      setLoadingRecordings(false);
    }
  };

  const handleDeleteRecording = async (filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"? This cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/recording/${filename}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        alert('✅ Recording deleted successfully!');
        // Refresh the recordings list
        fetchRecordings();
      } else {
        const error = await response.json();
        
        // Special handling for file-in-use error (423 Locked)
        if (response.status === 423) {
          alert(`⚠️ ${error.error}\n\n💡 Tip: Close or pause all video players showing this recording, then try again.`);
        } else {
          alert(`❌ Failed to delete recording:\n${error.error || error.details || 'Unknown error'}`);
        }
      }
    } catch (error) {
      console.error('Error deleting recording:', error);
      alert('❌ Error deleting recording. Please try again.');
    }
  };

  const handleOpenRecordings = () => {
    setShowRecordingsModal(true);
    fetchRecordings();
  };

  const handleSaveSettings = async (updatedCamera: Camera) => {
    try {
      const response = await fetch(`http://localhost:8000/api/camera/${updatedCamera.id}/update`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedCamera)
      });

      if (response.ok) {
        alert('Settings saved successfully!');
        setShowSettingsModal(false);
        if (onRefreshCameras) await onRefreshCameras();
      } else {
        alert('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error saving settings');
    }
  };

  const handleOpenFullscreen = (camera: Camera) => {
    setFullscreenCamera(camera);
    setShowFullscreenModal(true);
  };

  const handleCloseFullscreen = () => {
    setShowFullscreenModal(false);
    setFullscreenCamera(null);
  };

  return (
    <div>
      {/* Fullscreen Camera Modal */}
      {showFullscreenModal && fullscreenCamera && (
        <div className="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-50">
          <div className="relative w-full h-full flex flex-col">
            {/* Header with camera info and controls */}
            <div className="bg-black bg-opacity-75 text-white p-4 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <div>
                  <h2 className="text-xl font-semibold">{fullscreenCamera.name}</h2>
                  <p className="text-gray-300 text-sm">{fullscreenCamera.location}</p>
                </div>
                <div className="bg-red-600 text-white px-3 py-1 rounded text-sm flex items-center">
                  <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></div>
                  LIVE
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => handleTakeSnapshot(fullscreenCamera.id)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center space-x-2"
                >
                  <i className="ri-camera-line"></i>
                  <span>Snapshot</span>
                </button>
                <button
                  onClick={handleCloseFullscreen}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded flex items-center space-x-2"
                >
                  <i className="ri-close-line"></i>
                  <span>Close</span>
                </button>
              </div>
            </div>

            {/* Main video area */}
            <div className="flex-1 flex items-center justify-center bg-black">
              {fullscreenCamera.url && fullscreenCamera.url !== '0' ? (
                <div className="relative w-full h-full max-w-6xl max-h-[80vh]">
                  <img
                    src={fullscreenCamera.url.includes('video') ? fullscreenCamera.url : `${fullscreenCamera.url}/video`}
                    className="w-full h-full object-contain"
                    alt={`${fullscreenCamera.name} Live Stream`}
                    onError={(e) => {
                      const img = e.target as HTMLImageElement;
                      const originalUrl = fullscreenCamera.url;
                      
                      if (originalUrl && img.src.includes('/video')) {
                        img.src = originalUrl.includes('videofeed') ? originalUrl : `${originalUrl}/videofeed`;
                      } else if (originalUrl && img.src.includes('/videofeed')) {
                        img.src = originalUrl.includes('shot.jpg') ? originalUrl : `${originalUrl}/shot.jpg`;
                      } else {
                        img.style.display = 'none';
                        const placeholder = img.nextElementSibling as HTMLDivElement;
                        if (placeholder) placeholder.style.display = 'flex';
                      }
                    }}
                    onLoad={(e) => {
                      const img = e.target as HTMLImageElement;
                      if (img.src.includes('shot.jpg')) {
                        setTimeout(() => {
                          const url = new URL(img.src);
                          url.searchParams.set('t', Date.now().toString());
                          img.src = url.toString();
                        }, 1000); // Faster refresh for fullscreen
                      }
                    }}
                  />
                  
                  {/* Fallback placeholder */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-white hidden">
                    <i className="ri-camera-off-line text-6xl mb-4 text-gray-400"></i>
                    <h3 className="text-xl mb-2">Camera Stream Unavailable</h3>
                    <p className="text-gray-400">Check camera URL: {fullscreenCamera.url}</p>
                  </div>
                </div>
              ) : (
                <div className="text-center text-white">
                  <i className="ri-camera-off-line text-6xl mb-4 text-gray-400"></i>
                  <h3 className="text-xl mb-2">Camera Stream Unavailable</h3>
                  <p className="text-gray-400">
                    {fullscreenCamera.url === '0' ? 'Webcam stream not accessible' : 'IP camera stream not reachable'}
                  </p>
                </div>
              )}
            </div>

            {/* Footer with stream info */}
            <div className="bg-black bg-opacity-75 text-white p-4 flex items-center justify-between">
              <div className="flex items-center space-x-6 text-sm">
                <span>Resolution: 1920x1080</span>
                <span>FPS: 30</span>
                <span>Quality: HD</span>
                <span>AI Detection: Active</span>
              </div>
              <div className="text-sm text-gray-300">
                {new Date().toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Camera Modal */}
      {showAddCameraModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-4 sm:mb-6">
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900">Add New Camera</h3>
                <button
                  onClick={handleCancelAddCamera}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <i className="ri-close-line text-xl sm:text-2xl"></i>
                </button>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); handleSaveCamera(); }} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Camera Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={newCamera.name}
                    onChange={(e) => setNewCamera({...newCamera, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Main Entrance"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={newCamera.location}
                    onChange={(e) => setNewCamera({...newCamera, location: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Gate A"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    AI Detection Mode <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={newCamera.ai_mode}
                    onChange={(e) => setNewCamera({...newCamera, ai_mode: e.target.value as 'face_recognition' | 'yolov9' | 'both'})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="both">🛡️ Face Recognition + Activity Detection</option>
                    <option value="face_recognition">👤 Face Recognition Only</option>
                    <option value="yolov9">🎯 Activity Detection Only</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Camera URL <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={newCamera.url}
                    onChange={(e) => setNewCamera({...newCamera, url: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="http://192.168.1.100:8080/video"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    💡 Use IP Webcam app or enter '0' for laptop webcam
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-3 sm:justify-end pt-4">
                  <button
                    type="button"
                    onClick={handleCancelAddCamera}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm sm:text-base"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                  >
                    {isSubmitting ? (
                      <>
                        <i className="ri-loader-4-line animate-spin mr-2"></i>
                        Adding...
                      </>
                    ) : (
                      <>
                        <i className="ri-camera-line mr-2"></i>
                        Add Camera
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 sm:mb-6">
        <div>
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-1">Live Camera Streams</h2>
          <p className="text-sm text-gray-600">Monitor all camera feeds in real-time</p>
        </div>
        <div className="flex items-center space-x-2 mt-3 sm:mt-0">
          <button 
            onClick={handleAddCamera}
            className="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm whitespace-nowrap"
          >
            <i className="ri-add-line mr-1 sm:mr-2"></i>
            <span className="hidden sm:inline">Add Camera</span>
            <span className="sm:hidden">Add</span>
          </button>
          <button 
            onClick={handleOpenRecordings}
            className="px-3 sm:px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm whitespace-nowrap"
          >
            <i className="ri-video-line mr-1 sm:mr-2"></i>
            <span className="hidden sm:inline">View Recordings</span>
            <span className="sm:hidden">Videos</span>
          </button>
          <button 
            onClick={() => setShowProtectedManager(true)}
            className="px-3 sm:px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm whitespace-nowrap"
          >
            <i className="ri-shield-user-line mr-1 sm:mr-2"></i>
            <span className="hidden sm:inline">Admin Panel</span>
            <span className="sm:hidden">Admin</span>
          </button>
          <button className="px-3 sm:px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm whitespace-nowrap">
            <i className="ri-settings-3-line mr-1 sm:mr-2"></i>
            <span className="hidden sm:inline">Settings</span>
            <span className="sm:hidden">Config</span>
          </button>
        </div>
      </div>

      {/* Camera Grid */}
      {cameras.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {cameras.map((camera) => (
            <div key={camera.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="relative">
                {/* Live video stream display */}
                {camera.url && camera.url !== '0' ? (
                  <div className="w-full h-40 sm:h-48 bg-black relative">
                    {/* Try different stream formats for IP Webcam */}
                    <img
                      src={camera.url.includes('video') ? camera.url : `${camera.url}/video`}
                      className="w-full h-full object-cover"
                      alt={`${camera.name} Live Stream`}
                      onError={(e) => {
                        // Try alternative URL formats
                        const img = e.target as HTMLImageElement;
                        const originalUrl = camera.url;
                        
                        if (originalUrl && img.src.includes('/video')) {
                          // Try /videofeed
                          img.src = originalUrl.includes('videofeed') ? originalUrl : `${originalUrl}/videofeed`;
                        } else if (originalUrl && img.src.includes('/videofeed')) {
                          // Try /shot.jpg for still images
                          img.src = originalUrl.includes('shot.jpg') ? originalUrl : `${originalUrl}/shot.jpg`;
                        } else {
                          // Show error placeholder
                          img.style.display = 'none';
                          const placeholder = img.nextElementSibling as HTMLDivElement;
                          if (placeholder) placeholder.style.display = 'flex';
                        }
                      }}
                      onLoad={(e) => {
                        // If it's a still image (shot.jpg), refresh it every 2 seconds for live effect
                        const img = e.target as HTMLImageElement;
                        if (img.src.includes('shot.jpg')) {
                          setTimeout(() => {
                            const url = new URL(img.src);
                            url.searchParams.set('t', Date.now().toString());
                            img.src = url.toString();
                          }, 2000);
                        }
                      }}
                    />
                    
                    {/* Fallback placeholder for failed streams */}
                    <div 
                      className="absolute inset-0 bg-gray-200 flex-col items-center justify-center hidden"
                      style={{ display: 'none' }}
                    >
                      <i className="ri-camera-off-line text-gray-400 text-3xl mb-2"></i>
                      <span className="text-gray-500 text-sm">Stream Unavailable</span>
                      <span className="text-gray-400 text-xs mt-1">Check camera URL</span>
                    </div>
                  </div>
                ) : (
                  // Local webcam placeholder
                  <div className="w-full h-40 sm:h-48 bg-gray-200 flex flex-col items-center justify-center">
                    <i className="ri-camera-line text-gray-400 text-3xl mb-2"></i>
                    <span className="text-gray-500 text-sm">Local Webcam</span>
                    <span className="text-gray-400 text-xs">Use Admin Panel to configure</span>
                  </div>
                )}

                <div className={`absolute top-2 sm:top-3 right-2 sm:right-3 px-2 py-1 rounded text-xs font-medium ${
                  camera.status === 'online' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-red-600 text-white'
                }`}>
                  {camera.status === 'online' ? (
                    <div className="flex items-center">
                      <div className="w-1.5 h-1.5 bg-white rounded-full mr-1 animate-pulse"></div>
                      <span className="hidden sm:inline">LIVE</span>
                      <span className="sm:hidden">●</span>
                    </div>
                  ) : (
                    <span className="hidden sm:inline">OFFLINE</span>
                  )}
                </div>
                {camera.status === 'online' && (
                  <button
                    onClick={() => handleOpenFullscreen(camera)}
                    className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-30 transition-all group"
                  >
                    <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-600 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <i className="ri-fullscreen-line text-white text-lg sm:text-xl"></i>
                    </div>
                  </button>
                )}
              </div>
              
              <div className="p-3 sm:p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900 text-sm sm:text-base">{camera.name}</h3>
                  <div className={`w-2 h-2 rounded-full ${
                    camera.status === 'online' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                </div>
                <p className="text-xs sm:text-sm text-gray-600 mb-2">{camera.location}</p>
                <p className="text-xs text-gray-500 mb-3 font-mono">{camera.url === '0' ? 'Webcam' : camera.url}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex space-x-1 sm:space-x-2">
                    <div className="relative">
                      <button 
                        className={`p-1.5 sm:p-2 rounded transition-colors ${
                          recordingCameras.has(camera.id)
                            ? 'text-red-600 bg-red-50 hover:bg-red-100'
                            : 'text-gray-400 hover:text-blue-600 hover:bg-blue-50'
                        }`}
                        title={recordingCameras.has(camera.id) ? 'Stop Recording' : 'Start Recording'}
                        onClick={() => handleRecording(camera.id)}
                      >
                        <i className={`ri-record-circle-line text-sm sm:text-base ${
                          recordingCameras.has(camera.id) ? 'animate-pulse' : ''
                        }`}></i>
                      </button>
                      {recordingCameras.has(camera.id) && recordingDurations.get(camera.id) && (
                        <div className="absolute -top-1 -right-1 bg-red-600 text-white text-[10px] px-1 rounded font-mono">
                          {recordingDurations.get(camera.id)}
                        </div>
                      )}
                    </div>
                    <button 
                      className="p-1.5 sm:p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="Snapshot"
                      onClick={() => handleTakeSnapshot(camera.id)}
                    >
                      <i className="ri-camera-line text-sm sm:text-base"></i>
                    </button>
                    <button 
                      className="p-1.5 sm:p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="Settings"
                      onClick={() => handleSettings(camera)}
                    >
                      <i className="ri-settings-3-line text-sm sm:text-base"></i>
                    </button>
                  </div>
                  
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    camera.status === 'online' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {camera.status === 'online' ? 'Online' : 'Offline'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 sm:py-12">
          <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i className="ri-camera-line text-gray-400 text-2xl sm:text-3xl"></i>
          </div>
          <h3 className="text-lg sm:text-xl font-medium text-gray-900 mb-2">No Cameras Connected</h3>
          <p className="text-sm sm:text-base text-gray-600 mb-4">
            Add IP cameras or webcams to start monitoring your surveillance network
          </p>
          <button 
            onClick={handleAddCamera}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <i className="ri-add-line mr-2"></i>
            Add Your First Camera
          </button>
        </div>
      )}
      
      {/* Protected Camera Manager */}
      {showProtectedManager && (
        <ProtectedCameraManager onClose={() => setShowProtectedManager(false)} />
      )}

      {/* Snapshot Preview Modal */}
      {showSnapshotModal && snapshotData && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="text-lg font-semibold">Snapshot Preview</h3>
              <button onClick={() => setShowSnapshotModal(false)} className="text-gray-500 hover:text-gray-700">
                <i className="ri-close-line text-2xl"></i>
              </button>
            </div>
            <div className="p-6">
              <img src={snapshotData.url} alt="Snapshot" className="w-full rounded-lg shadow-lg" />
              <p className="text-sm text-gray-600 mt-4">Saved to: {snapshotData.path}</p>
            </div>
            <div className="p-4 border-t flex justify-end space-x-3">
              <a
                href={snapshotData.url}
                download
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <i className="ri-download-line mr-2"></i>
                Download
              </a>
              <button
                onClick={() => window.open(snapshotData.url, '_blank')}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                <i className="ri-fullscreen-line mr-2"></i>
                Fullscreen
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettingsModal && settingsCamera && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setShowSettingsModal(false)}
        >
          <div 
            className="bg-white rounded-lg max-w-2xl w-full max-h-[85vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b flex items-center justify-between flex-shrink-0">
              <h3 className="text-lg font-semibold">Camera Settings - {settingsCamera.name}</h3>
              <button onClick={() => setShowSettingsModal(false)} className="text-gray-500 hover:text-gray-700">
                <i className="ri-close-line text-2xl"></i>
              </button>
            </div>
            <div className="p-6 space-y-4 overflow-y-auto flex-1">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Camera Name</label>
                <input
                  type="text"
                  defaultValue={settingsCamera.name}
                  onChange={(e) => setSettingsCamera({...settingsCamera, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input
                  type="text"
                  defaultValue={settingsCamera.location}
                  onChange={(e) => setSettingsCamera({...settingsCamera, location: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Camera URL</label>
                <input
                  type="text"
                  defaultValue={settingsCamera.url}
                  onChange={(e) => setSettingsCamera({...settingsCamera, url: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="http://192.168.1.100:8080/video"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">AI Detection Mode</label>
                <select
                  defaultValue={(settingsCamera as any).ai_mode || 'both'}
                  onChange={(e) => setSettingsCamera({...settingsCamera, ai_mode: e.target.value} as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="both">Face Recognition + Activity Detection</option>
                  <option value="face_recognition">Face Recognition Only</option>
                  <option value="yolov9">Activity Detection Only</option>
                </select>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-700 mb-2">Live Preview</h4>
                {settingsCamera.url && settingsCamera.url !== '0' ? (
                  <img 
                    src={settingsCamera.url.includes('video') ? settingsCamera.url : `${settingsCamera.url}/video`}
                    alt="Camera preview"
                    className="w-full rounded"
                  />
                ) : (
                  <div className="bg-gray-200 h-48 flex items-center justify-center rounded">
                    <i className="ri-camera-line text-gray-400 text-4xl"></i>
                  </div>
                )}
              </div>
            </div>
            <div className="p-4 border-t flex justify-end space-x-3 flex-shrink-0 bg-white">
              <button
                onClick={() => setShowSettingsModal(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleSaveSettings(settingsCamera)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Recordings List Modal */}
      {showRecordingsModal && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setShowRecordingsModal(false)}
        >
          <div 
            className="bg-white rounded-lg max-w-6xl w-full max-h-[85vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b flex items-center justify-between flex-shrink-0">
              <div>
                <h3 className="text-lg font-semibold">Recorded Videos</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Storage: <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">backend/storage/recordings/</code>
                </p>
              </div>
              <button onClick={() => setShowRecordingsModal(false)} className="text-gray-500 hover:text-gray-700">
                <i className="ri-close-line text-2xl"></i>
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-1">
              {loadingRecordings ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                  <span className="ml-3 text-gray-600">Loading recordings...</span>
                </div>
              ) : recordings.length === 0 ? (
                <div className="text-center py-12">
                  <i className="ri-video-line text-6xl text-gray-300 block mb-4"></i>
                  <h4 className="text-lg font-medium text-gray-700 mb-2">No Recordings Yet</h4>
                  <p className="text-gray-500 mb-4">Start recording from any camera to see videos here</p>
                  <button
                    onClick={() => setShowRecordingsModal(false)}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  >
                    <i className="ri-record-circle-line mr-2"></i>
                    Start Recording
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recordings.map((recording, index) => (
                    <div key={index} className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                      <div className="bg-black aspect-video flex items-center justify-center">
                        <video 
                          src={`http://localhost:8000/api/storage/recording/${recording.filename}`}
                          className="w-full h-full object-contain"
                          controls
                        >
                          Your browser does not support video playback.
                        </video>
                      </div>
                      <div className="p-3">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900 truncate">{recording.camera_name || 'Unknown Camera'}</h4>
                            <p className="text-xs text-gray-500">
                              {recording.location || cameras.find(c => c.name === recording.camera_name)?.location || 'No location set'}
                            </p>
                          </div>
                          <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                            {recording.size_mb || recording.duration || 'N/A'}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mb-3">
                          <i className="ri-time-line mr-1"></i>
                          {recording.timestamp || 'Unknown time'}
                        </p>
                        <div className="flex gap-2">
                          <a
                            href={`http://localhost:8000/api/storage/recording/${recording.filename}`}
                            download
                            className="flex-1 px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 text-center"
                          >
                            <i className="ri-download-line mr-1"></i>
                            Download
                          </a>
                          <button
                            onClick={() => window.open(`http://localhost:8000/api/storage/recording/${recording.filename}`, '_blank')}
                            className="px-3 py-1.5 border border-gray-300 text-gray-700 text-xs rounded hover:bg-gray-50"
                          >
                            <i className="ri-external-link-line"></i>
                          </button>
                          <button
                            onClick={() => handleDeleteRecording(recording.filename)}
                            className="px-3 py-1.5 bg-red-600 text-white text-xs rounded hover:bg-red-700"
                            title="Delete recording"
                          >
                            <i className="ri-delete-bin-line"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="p-4 border-t flex justify-between items-center flex-shrink-0 bg-gray-50">
              <p className="text-sm text-gray-600">
                Total: <span className="font-semibold">{recordings.length}</span> recording{recordings.length !== 1 ? 's' : ''}
              </p>
              <button
                onClick={() => setShowRecordingsModal(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
