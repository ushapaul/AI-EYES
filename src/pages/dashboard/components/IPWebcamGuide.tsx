import React, { useState } from 'react';

const IPWebcamGuide: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="text-blue-500 text-sm underline hover:text-blue-600"
      >
        📱 How to set up IP Webcam?
      </button>
    );
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-semibold text-blue-900">📱 IP Webcam Setup Guide</h4>
        <button
          onClick={() => setIsOpen(false)}
          className="text-blue-500 hover:text-blue-700"
        >
          ×
        </button>
      </div>
      
      <div className="space-y-3 text-sm text-blue-800">
        <div>
          <h5 className="font-medium mb-1">Step 1: Install IP Webcam App</h5>
          <p>Download "IP Webcam" app from Google Play Store on your Android phone</p>
        </div>
        
        <div>
          <h5 className="font-medium mb-1">Step 2: Configure Settings</h5>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Open IP Webcam app</li>
            <li>Set video resolution (e.g., 640x480 or 1280x720)</li>
            <li>Set quality to 80-100%</li>
            <li>Choose port (default: 8080)</li>
          </ul>
        </div>
        
        <div>
          <h5 className="font-medium mb-1">Step 3: Start Server</h5>
          <p>Tap "Start server" in the app. Note the IP address shown (e.g., 192.168.1.100:8080)</p>
        </div>
        
        <div>
          <h5 className="font-medium mb-1">Step 4: Find Your Phone's IP</h5>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Go to Phone Settings → Wi-Fi</li>
            <li>Tap your connected network</li>
            <li>Note the IP address (e.g., 192.168.1.100)</li>
          </ul>
        </div>
        
        <div>
          <h5 className="font-medium mb-1">Step 5: Test URLs</h5>
          <p>Try these common URL formats:</p>
          <ul className="list-disc list-inside space-y-1 ml-2 font-mono text-xs">
            <li>http://192.168.1.100:8080/video</li>
            <li>http://192.168.1.100:8080/videofeed</li>
            <li>http://192.168.1.100:8080/shot.jpg</li>
          </ul>
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded p-2">
          <h5 className="font-medium text-yellow-800 mb-1">💡 Troubleshooting Tips</h5>
          <ul className="list-disc list-inside space-y-1 text-yellow-700 text-xs ml-2">
            <li>Ensure both devices are on the same WiFi network</li>
            <li>Turn off phone's mobile data to force WiFi usage</li>
            <li>Try different ports: 8080, 8081, 4747</li>
            <li>Disable firewall temporarily on computer</li>
            <li>Check if IP address changed (phones get new IPs)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default IPWebcamGuide;