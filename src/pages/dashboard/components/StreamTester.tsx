import React, { useState } from 'react';

interface StreamTesterProps {
  baseUrl: string;
  onUrlFound: (workingUrl: string) => void;
}

const StreamTester: React.FC<StreamTesterProps> = ({ baseUrl, onUrlFound }) => {
  const [testResults, setTestResults] = useState<{[key: string]: 'testing' | 'success' | 'failed'}>({});
  const [workingUrl, setWorkingUrl] = useState<string>('');

  // Common IP Webcam URL patterns
  const urlPatterns = [
    { name: 'Video Stream', url: `${baseUrl}/video` },
    { name: 'Video Feed', url: `${baseUrl}/videofeed` },
    { name: 'MJPEG Stream', url: `${baseUrl}/mjpeg` },
    { name: 'Still Image', url: `${baseUrl}/shot.jpg` },
    { name: 'Live Stream', url: `${baseUrl}/stream` },
    { name: 'Camera Feed', url: `${baseUrl}/cam.mjpg` },
    { name: 'Direct URL', url: baseUrl }
  ];

  const testUrl = async (pattern: {name: string, url: string}) => {
    setTestResults(prev => ({...prev, [pattern.name]: 'testing'}));
    
    try {
      // Create a test image element
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      return new Promise<void>((resolve, reject) => {
        img.onload = () => {
          setTestResults(prev => ({...prev, [pattern.name]: 'success'}));
          setWorkingUrl(pattern.url);
          onUrlFound(pattern.url);
          resolve();
        };
        
        img.onerror = () => {
          setTestResults(prev => ({...prev, [pattern.name]: 'failed'}));
          reject();
        };
        
        // Timeout after 5 seconds
        setTimeout(() => {
          setTestResults(prev => ({...prev, [pattern.name]: 'failed'}));
          reject();
        }, 5000);
        
        img.src = pattern.url;
      });
    } catch (error) {
      setTestResults(prev => ({...prev, [pattern.name]: 'failed'}));
    }
  };

  const testAllUrls = async () => {
    setTestResults({});
    setWorkingUrl('');
    
    for (const pattern of urlPatterns) {
      try {
        await testUrl(pattern);
        break; // Stop on first success
      } catch {
        // Continue to next pattern
      }
    }
  };

  const getStatusIcon = (status: 'testing' | 'success' | 'failed' | undefined) => {
    switch (status) {
      case 'testing': return <i className="ri-loader-4-line animate-spin text-blue-500"></i>;
      case 'success': return <i className="ri-check-line text-green-500"></i>;
      case 'failed': return <i className="ri-close-line text-red-500"></i>;
      default: return <i className="ri-question-line text-gray-400"></i>;
    }
  };

  return (
    <div className="bg-gray-50 p-4 rounded-lg">
      <div className="flex justify-between items-center mb-4">
        <h4 className="font-medium text-gray-900">Stream URL Tester</h4>
        <button
          onClick={testAllUrls}
          className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
        >
          Test URLs
        </button>
      </div>
      
      <div className="space-y-2">
        {urlPatterns.map((pattern) => (
          <div key={pattern.name} className="flex items-center justify-between p-2 bg-white rounded border">
            <div className="flex-1">
              <div className="font-medium text-sm">{pattern.name}</div>
              <div className="text-xs text-gray-500 font-mono break-all">{pattern.url}</div>
            </div>
            <div className="ml-2 flex items-center">
              {getStatusIcon(testResults[pattern.name])}
              {testResults[pattern.name] === 'success' && (
                <button
                  onClick={() => onUrlFound(pattern.url)}
                  className="ml-2 bg-green-500 text-white px-2 py-1 rounded text-xs hover:bg-green-600"
                >
                  Use This
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {workingUrl && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
          <div className="flex items-center">
            <i className="ri-check-circle-line text-green-500 mr-2"></i>
            <span className="text-green-800 font-medium">Working URL Found!</span>
          </div>
          <div className="text-green-700 text-sm mt-1 font-mono break-all">{workingUrl}</div>
        </div>
      )}
      
      <div className="mt-4 text-xs text-gray-500">
        <p><strong>Tips:</strong></p>
        <ul className="list-disc list-inside space-y-1">
          <li>Make sure your IP Webcam app is running on your phone</li>
          <li>Both devices should be on the same WiFi network</li>
          <li>Try replacing the IP with your phone's actual IP address</li>
          <li>Common ports are 8080, 8081, or 4747</li>
        </ul>
      </div>
    </div>
  );
};

export default StreamTester;