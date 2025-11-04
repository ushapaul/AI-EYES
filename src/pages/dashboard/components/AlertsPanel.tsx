
import { useState } from 'react';

interface Alert {
  id: number | string; // Support both MongoDB ObjectId (string) and integer IDs
  type: string;
  location: string;
  timestamp: string;
  severity: string;
  image?: string;
  status?: string;
  confidence?: number;
  description?: string;
}

interface AlertsPanelProps {
  alerts: Alert[];
  onAcknowledge?: (alertId: number | string) => void;
  onDismiss?: (alertId: number | string) => void;
  onEscalate?: (alertId: number | string, recipientEmail: string, recipientName: string) => Promise<boolean>;
  onRefresh?: () => void;
}

export default function AlertsPanel({ alerts, onAcknowledge, onDismiss, onEscalate, onRefresh }: AlertsPanelProps) {
  const [filter, setFilter] = useState('all');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [selectedRecipients, setSelectedRecipients] = useState<string[]>([]);
  const [escalatedPersons, setEscalatedPersons] = useState<string[]>([]); // Track who received emails

  // Authorized persons list - emails from environment variables
  const authorizedPersons = [
    { 
      name: 'manager_prajwal', 
      email: import.meta.env.VITE_MANAGER_PRAJWAL_EMAIL || 'prajwal@yourdomain.com', 
      role: 'Site Manager', 
      icon: 'ri-user-star-line' 
    },
    { 
      name: 'farmer_Basava', 
      email: import.meta.env.VITE_FARMER_BASAVA_EMAIL || 'basava@yourdomain.com', 
      role: 'Farmer', 
      icon: 'ri-user-line' 
    },
    { 
      name: 'owner_rajasekhar', 
      email: import.meta.env.VITE_OWNER_RAJASEKHAR_EMAIL || 'rajasekhar@yourdomain.com', 
      role: 'Owner', 
      icon: 'ri-vip-crown-line' 
    }
  ];

  const filteredAlerts = alerts.filter(alert => 
    filter === 'all' || alert.severity === filter
  );

  const dismissAlert = (alertId: number | string) => {
    if (onDismiss) {
      onDismiss(alertId);
    }
    if (selectedAlert && selectedAlert.id === alertId) {
      setSelectedAlert(null);
      setEscalatedPersons([]); // Reset escalation status
    }
  };

  const acknowledgeAlert = (alertId: number | string) => {
    if (onAcknowledge) {
      onAcknowledge(alertId);
    }
  };

  // Reset escalated persons when modal closes or new alert is selected
  const handleModalClose = () => {
    setSelectedAlert(null);
    setEscalatedPersons([]);
  };

  const handleAlertSelect = (alert: Alert) => {
    console.log('Selected alert:', alert);
    console.log('Alert image field:', alert.image);
    setSelectedAlert(alert);
    setEscalatedPersons([]); // Reset for new alert
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return 'ri-alarm-warning-fill';
      case 'medium': return 'ri-alert-fill';
      case 'low': return 'ri-information-fill';
      default: return 'ri-notification-3-fill';
    }
  };

  const getAlertTypeIcon = (type: string) => {
    switch (type) {
      case 'intruder': return 'ri-user-forbid-line';
      case 'suspicious_activity': return 'ri-eye-line';
      case 'motion': return 'ri-run-line';
      default: return 'ri-alarm-warning-line';
    }
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 sm:mb-6">
        <div>
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-1">Security Alerts</h2>
          <p className="text-sm text-gray-600">Real-time threat notifications and security events</p>
        </div>
        
        {/* Filter Buttons */}
        <div className="flex items-center space-x-1 sm:space-x-2 mt-3 sm:mt-0 overflow-x-auto">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="px-2 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-colors whitespace-nowrap bg-gray-100 text-gray-600 hover:bg-gray-200 mr-2"
            >
              <i className="ri-refresh-line mr-1"></i>
              Refresh
            </button>
          )}
          {['all', 'high', 'medium', 'low'].map((severity) => (
            <button
              key={severity}
              onClick={() => setFilter(severity)}
              className={`px-2 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-colors whitespace-nowrap ${
                filter === severity
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {severity === 'all' ? 'All Alerts' : `${severity.charAt(0).toUpperCase() + severity.slice(1)} Priority`}
            </button>
          ))}
        </div>
      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="p-4 sm:p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-4 sm:mb-6 pb-4 border-b">
                <div className="flex items-center space-x-3">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                    selectedAlert.severity === 'high' ? 'bg-red-100' :
                    selectedAlert.severity === 'medium' ? 'bg-yellow-100' : 'bg-blue-100'
                  }`}>
                    <i className={`${getAlertTypeIcon(selectedAlert.type)} text-2xl ${
                      selectedAlert.severity === 'high' ? 'text-red-600' :
                      selectedAlert.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                    }`}></i>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {selectedAlert.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Detected
                    </h3>
                    <p className="text-sm text-gray-600">{selectedAlert.location}</p>
                  </div>
                </div>
                <button
                  onClick={handleModalClose}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <i className="ri-close-line text-2xl"></i>
                </button>
              </div>

              {/* Captured Image */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <i className="ri-camera-line mr-2 text-blue-600"></i>
                  Captured Evidence
                </h4>
                {selectedAlert.image ? (
                  <div className="relative group">
                    <img
                      src={selectedAlert.image.startsWith('http') ? selectedAlert.image : `http://localhost:8000${selectedAlert.image}`}
                      alt="Alert Evidence"
                      className="w-full h-80 object-cover rounded-lg border-2 border-gray-200"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        // Hide image and show "No Evidence" message instead
                        target.style.display = 'none';
                        const parent = target.parentElement;
                        if (parent) {
                          parent.innerHTML = `
                            <div class="w-full h-80 bg-gradient-to-br from-gray-900 to-gray-700 rounded-lg flex flex-col items-center justify-center text-white relative overflow-hidden">
                              <div class="absolute inset-0 opacity-10">
                                <svg class="w-full h-full" viewBox="0 0 200 200" fill="currentColor">
                                  <path d="M100 50c-27.6 0-50 22.4-50 50s22.4 50 50 50 50-22.4 50-50-22.4-50-50-50zm0 80c-16.5 0-30-13.5-30-30s13.5-30 30-30 30 13.5 30 30-13.5 30-30 30z"/>
                                  <circle cx="100" cy="100" r="15"/>
                                </svg>
                              </div>
                              <i class="ri-camera-off-line text-6xl mb-3 relative z-10"></i>
                              <p class="text-lg font-medium relative z-10">Evidence Image Not Available</p>
                              <p class="text-sm text-gray-400 mt-1 relative z-10">Could not load captured image</p>
                            </div>
                          `;
                        }
                      }}
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all rounded-lg"></div>
                  </div>
                ) : (
                  <div className="w-full h-80 bg-gradient-to-br from-gray-900 to-gray-700 rounded-lg flex flex-col items-center justify-center text-white relative overflow-hidden">
                    {/* Security Camera Icon Background */}
                    <div className="absolute inset-0 opacity-10">
                      <svg className="w-full h-full" viewBox="0 0 200 200" fill="currentColor">
                        <path d="M100 50c-27.6 0-50 22.4-50 50s22.4 50 50 50 50-22.4 50-50-22.4-50-50-50zm0 80c-16.5 0-30-13.5-30-30s13.5-30 30-30 30 13.5 30 30-13.5 30-30 30z"/>
                        <circle cx="100" cy="100" r="15"/>
                      </svg>
                    </div>
                    <i className="ri-camera-off-line text-6xl mb-3 relative z-10"></i>
                    <p className="text-lg font-medium relative z-10">No Evidence Image Available</p>
                    <p className="text-sm text-gray-400 mt-1 relative z-10">Alert triggered without snapshot</p>
                  </div>
                )}
              </div>

              {/* Two Column Layout */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {/* Left Column - Alert Details */}
                <div className="space-y-4">
                  {/* Alert Information */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                      <i className="ri-information-line mr-2 text-blue-600"></i>
                      Alert Details
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Timestamp:</span>
                        <span className="font-medium text-gray-900">{formatTimestamp(selectedAlert.timestamp)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Location:</span>
                        <span className="font-medium text-gray-900">{selectedAlert.location}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Severity:</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-bold border ${getSeverityColor(selectedAlert.severity)}`}>
                          {selectedAlert.severity.toUpperCase()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Type:</span>
                        <span className="font-medium text-gray-900">
                          {selectedAlert.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Confidence:</span>
                        <span className="font-medium text-green-600">94.7%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Camera ID:</span>
                        <span className="font-medium text-gray-900">CAM-68f264996d2464aaa766a54f</span>
                      </div>
                    </div>
                  </div>

                  {/* Reason for Alert */}
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h4 className="font-semibold text-red-900 mb-3 flex items-center">
                      <i className="ri-error-warning-line mr-2 text-red-600"></i>
                      Reason for Alert
                    </h4>
                    <p className="text-sm text-red-800 leading-relaxed">
                      {selectedAlert.type === 'intruder' && (
                        <>
                          <strong>Unauthorized person detected:</strong> An unknown individual was identified who is not in the authorized personnel database. The face recognition system confirmed this person does not match any of the 3 authorized persons (farmer_Basava, manager_prajwal, owner_rajasekhar). This could indicate a potential security breach or trespassing incident.
                        </>
                      )}
                      {selectedAlert.type === 'suspicious_activity' && (
                        <>
                          <strong>Suspicious behavior identified:</strong> The AI detection system observed unusual activity patterns that deviate from normal behavior. This may include loitering, unauthorized zone access, or suspicious movements requiring immediate attention.
                        </>
                      )}
                      {selectedAlert.type !== 'intruder' && selectedAlert.type !== 'suspicious_activity' && (
                        <>
                          <strong>Security event detected:</strong> The surveillance system has identified an event requiring your attention based on configured security parameters and AI analysis.
                        </>
                      )}
                    </p>
                  </div>
                </div>

                {/* Right Column - Actions & Precautions */}
                <div className="space-y-4">
                  {/* Recommended Precautions */}
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h4 className="font-semibold text-yellow-900 mb-3 flex items-center">
                      <i className="ri-shield-check-line mr-2 text-yellow-600"></i>
                      Recommended Actions
                    </h4>
                    <ul className="space-y-2 text-sm text-yellow-800">
                      <li className="flex items-start">
                        <i className="ri-checkbox-circle-fill mr-2 mt-0.5 text-yellow-600"></i>
                        <span><strong>Verify identity:</strong> Review the captured image to confirm if this is truly an unauthorized person or a false positive.</span>
                      </li>
                      <li className="flex items-start">
                        <i className="ri-checkbox-circle-fill mr-2 mt-0.5 text-yellow-600"></i>
                        <span><strong>Check live feed:</strong> Monitor the camera's live stream to assess current situation and determine if immediate action is needed.</span>
                      </li>
                      <li className="flex items-start">
                        <i className="ri-checkbox-circle-fill mr-2 mt-0.5 text-yellow-600"></i>
                        <span><strong>Secure the area:</strong> If threat is confirmed, ensure all entry points are secured and notify on-site security personnel.</span>
                      </li>
                      <li className="flex items-start">
                        <i className="ri-checkbox-circle-fill mr-2 mt-0.5 text-yellow-600"></i>
                        <span><strong>Document incident:</strong> Take additional screenshots, note the time and circumstances for security records.</span>
                      </li>
                      <li className="flex items-start">
                        <i className="ri-checkbox-circle-fill mr-2 mt-0.5 text-yellow-600"></i>
                        <span><strong>Update training:</strong> If this is a false positive, consider retraining the model with this person's images.</span>
                      </li>
                    </ul>
                  </div>

                  {/* Escalation Options */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
                      <i className="ri-user-voice-line mr-2 text-blue-600"></i>
                      Escalate To Authorized Persons
                    </h4>
                    <div className="space-y-2">
                      {/* Manager Prajwal */}
                      <button
                        onClick={async () => {
                          if (onEscalate) {
                            const manager = authorizedPersons.find(p => p.name === 'manager_prajwal');
                            if (manager) {
                              const success = await onEscalate(selectedAlert.id, manager.email, `${manager.role} - Prajwal`);
                              if (success) {
                                setEscalatedPersons(prev => [...prev, 'manager_prajwal']);
                                alert(`✅ Alert escalated to ${manager.role} (Prajwal)\nEmail sent successfully to: ${manager.email}`);
                              } else {
                                alert('❌ Failed to escalate alert. Please try again or contact support.');
                              }
                            }
                          }
                        }}
                        disabled={escalatedPersons.includes('manager_prajwal')}
                        className={`w-full px-4 py-3 rounded-lg transition-colors text-left ${
                          escalatedPersons.includes('manager_prajwal')
                            ? 'bg-green-50 border-2 border-green-400 cursor-not-allowed opacity-75'
                            : 'bg-white border border-blue-300 hover:bg-blue-100'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <i className={`text-xl ${
                              escalatedPersons.includes('manager_prajwal') 
                                ? 'ri-checkbox-circle-fill text-green-600' 
                                : 'ri-user-star-line text-blue-600'
                            }`}></i>
                            <div>
                              <div className="font-medium text-gray-900 flex items-center gap-2">
                                Manager Prajwal
                                {escalatedPersons.includes('manager_prajwal') && (
                                  <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">✓ Escalated</span>
                                )}
                              </div>
                              <div className="text-xs text-gray-600">{authorizedPersons.find(p => p.name === 'manager_prajwal')?.email}</div>
                            </div>
                          </div>
                          {!escalatedPersons.includes('manager_prajwal') && (
                            <i className="ri-arrow-right-line text-blue-600"></i>
                          )}
                        </div>
                      </button>

                      {/* Farmer Basava */}
                      <button
                        onClick={async () => {
                          if (onEscalate) {
                            const farmer = authorizedPersons.find(p => p.name === 'farmer_Basava');
                            if (farmer) {
                              const success = await onEscalate(selectedAlert.id, farmer.email, `${farmer.role} - Basava`);
                              if (success) {
                                setEscalatedPersons(prev => [...prev, 'farmer_Basava']);
                                alert(`✅ Alert escalated to ${farmer.role} (Basava)\nEmail sent successfully to: ${farmer.email}`);
                              } else {
                                alert('❌ Failed to escalate alert. Please try again or contact support.');
                              }
                            }
                          }
                        }}
                        disabled={escalatedPersons.includes('farmer_Basava')}
                        className={`w-full px-4 py-3 rounded-lg transition-colors text-left ${
                          escalatedPersons.includes('farmer_Basava')
                            ? 'bg-green-50 border-2 border-green-400 cursor-not-allowed opacity-75'
                            : 'bg-white border border-green-300 hover:bg-green-100'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <i className={`text-xl ${
                              escalatedPersons.includes('farmer_Basava') 
                                ? 'ri-checkbox-circle-fill text-green-600' 
                                : 'ri-user-line text-green-600'
                            }`}></i>
                            <div>
                              <div className="font-medium text-gray-900 flex items-center gap-2">
                                Farmer Basava
                                {escalatedPersons.includes('farmer_Basava') && (
                                  <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">✓ Escalated</span>
                                )}
                              </div>
                              <div className="text-xs text-gray-600">{authorizedPersons.find(p => p.name === 'farmer_Basava')?.email}</div>
                            </div>
                          </div>
                          {!escalatedPersons.includes('farmer_Basava') && (
                            <i className="ri-arrow-right-line text-green-600"></i>
                          )}
                        </div>
                      </button>

                      {/* Owner Rajasekhar */}
                      <button
                        onClick={async () => {
                          if (onEscalate) {
                            const owner = authorizedPersons.find(p => p.name === 'owner_rajasekhar');
                            if (owner) {
                              const success = await onEscalate(selectedAlert.id, owner.email, `${owner.role} - Rajasekhar`);
                              if (success) {
                                setEscalatedPersons(prev => [...prev, 'owner_rajasekhar']);
                                alert(`✅ Alert escalated to ${owner.role} (Rajasekhar)\nEmail sent successfully to: ${owner.email}`);
                              } else {
                                alert('❌ Failed to escalate alert. Please try again or contact support.');
                              }
                            }
                          }
                        }}
                        disabled={escalatedPersons.includes('owner_rajasekhar')}
                        className={`w-full px-4 py-3 rounded-lg transition-colors text-left ${
                          escalatedPersons.includes('owner_rajasekhar')
                            ? 'bg-green-50 border-2 border-green-400 cursor-not-allowed opacity-75'
                            : 'bg-white border border-purple-300 hover:bg-purple-100'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <i className={`text-xl ${
                              escalatedPersons.includes('owner_rajasekhar') 
                                ? 'ri-checkbox-circle-fill text-green-600' 
                                : 'ri-vip-crown-line text-purple-600'
                            }`}></i>
                            <div>
                              <div className="font-medium text-gray-900 flex items-center gap-2">
                                Owner Rajasekhar
                                {escalatedPersons.includes('owner_rajasekhar') && (
                                  <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">✓ Escalated</span>
                                )}
                              </div>
                              <div className="text-xs text-gray-600">{authorizedPersons.find(p => p.name === 'owner_rajasekhar')?.email}</div>
                            </div>
                          </div>
                          {!escalatedPersons.includes('owner_rajasekhar') && (
                            <i className="ri-arrow-right-line text-purple-600"></i>
                          )}
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t">
                <button
                  onClick={handleModalClose}
                  className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  <i className="ri-close-line mr-2"></i>
                  Close
                </button>
                <button
                  onClick={() => {
                    acknowledgeAlert(selectedAlert.id);
                    alert('Alert marked as false positive and added to ignore list');
                    setSelectedAlert(null);
                  }}
                  className="flex-1 px-4 py-2.5 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors font-medium"
                >
                  <i className="ri-error-warning-line mr-2"></i>
                  Mark as False Positive
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Email Selection Modal */}
      {showEmailModal && selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6 pb-4 border-b">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                    <i className="ri-mail-send-line text-2xl text-red-600"></i>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Send Alert Email</h3>
                    <p className="text-sm text-gray-600">Select recipients</p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setShowEmailModal(false);
                    setSelectedRecipients([]);
                  }}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <i className="ri-close-line text-2xl"></i>
                </button>
              </div>

              {/* Recipients Selection */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">
                  Select Authorized Persons to Notify:
                </h4>
                <div className="space-y-2">
                  {authorizedPersons.map((person) => (
                    <label
                      key={person.name}
                      className={`flex items-center justify-between p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        selectedRecipients.includes(person.name)
                          ? 'border-red-500 bg-red-50'
                          : 'border-gray-200 hover:border-red-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={selectedRecipients.includes(person.name)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedRecipients([...selectedRecipients, person.name]);
                            } else {
                              setSelectedRecipients(selectedRecipients.filter(r => r !== person.name));
                            }
                          }}
                          className="w-5 h-5 text-red-600 rounded focus:ring-2 focus:ring-red-500"
                        />
                        <i className={`${person.icon} text-2xl text-gray-700`}></i>
                        <div>
                          <div className="font-medium text-gray-900">{person.name}</div>
                          <div className="text-xs text-gray-600">{person.role}</div>
                          <div className="text-xs text-gray-500">{person.email}</div>
                        </div>
                      </div>
                      {selectedRecipients.includes(person.name) && (
                        <i className="ri-checkbox-circle-fill text-red-600 text-xl"></i>
                      )}
                    </label>
                  ))}
                </div>
              </div>

              {/* Alert Preview */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-2 text-sm">Email Will Include:</h4>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li className="flex items-start">
                    <i className="ri-checkbox-circle-fill text-green-600 mr-2 mt-0.5"></i>
                    <span>Captured image (alert_{selectedAlert.id}.jpg)</span>
                  </li>
                  <li className="flex items-start">
                    <i className="ri-checkbox-circle-fill text-green-600 mr-2 mt-0.5"></i>
                    <span>Alert timestamp & location</span>
                  </li>
                  <li className="flex items-start">
                    <i className="ri-checkbox-circle-fill text-green-600 mr-2 mt-0.5"></i>
                    <span>Intruder detection details</span>
                  </li>
                  <li className="flex items-start">
                    <i className="ri-checkbox-circle-fill text-green-600 mr-2 mt-0.5"></i>
                    <span>Recommended security actions</span>
                  </li>
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => {
                    setShowEmailModal(false);
                    setSelectedRecipients([]);
                  }}
                  className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  <i className="ri-close-line mr-2"></i>
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    if (selectedRecipients.length === 0) {
                      alert('Please select at least one recipient');
                      return;
                    }
                    
                    try {
                      // Prepare alert data for backend
                      const alertData = {
                        alert_id: selectedAlert.id,
                        recipients: selectedRecipients,
                        alert_data: {
                          type: selectedAlert.type || 'intruder',
                          camera: 'Camera 1', // Will be populated from actual alert data
                          location: selectedAlert.location,
                          severity: selectedAlert.severity,
                          confidence: selectedAlert.confidence || 95,
                          person: selectedAlert.description || 'Unknown', // Use description field
                          timestamp: selectedAlert.timestamp,
                          image: selectedAlert.image || ''
                        }
                      };
                      
                      // Call backend API
                      const response = await fetch('http://localhost:8000/api/alerts/send-email', {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(alertData),
                      });
                      
                      const result = await response.json();
                      
                      if (result.success) {
                        const recipientNames = selectedRecipients.map(name => {
                          const person = authorizedPersons.find(p => p.name === name);
                          return `• ${person?.name} (${person?.email})`;
                        }).join('\n');
                        
                        alert(`✅ Alert email sent successfully!\n\nRecipients:\n${recipientNames}\n\nImage attached: alert_${selectedAlert.id}.jpg\n\nEmail includes:\n• Captured evidence image\n• Alert timestamp & location\n• Intruder detection details\n• Recommended security actions`);
                        
                        setShowEmailModal(false);
                        setSelectedRecipients([]);
                        dismissAlert(selectedAlert.id);
                        setSelectedAlert(null);
                      } else {
                        alert(`❌ Failed to send email:\n${result.message}`);
                      }
                    } catch (error) {
                      console.error('Error sending email:', error);
                      alert(`❌ Failed to send email: ${error instanceof Error ? error.message : 'Unknown error'}`);
                    }
                  }}
                  disabled={selectedRecipients.length === 0}
                  className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <i className="ri-mail-send-line mr-2"></i>
                  Send to {selectedRecipients.length > 0 ? selectedRecipients.length : ''} {selectedRecipients.length === 1 ? 'Person' : 'People'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alerts List */}
      {filteredAlerts.length === 0 ? (
        <div className="text-center py-8 sm:py-12">
          <div className="w-16 h-16 sm:w-20 sm:h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i className="ri-shield-check-line text-green-600 text-2xl sm:text-3xl"></i>
          </div>
          <h3 className="text-lg sm:text-xl font-medium text-gray-900 mb-2">No Active Alerts</h3>
          <p className="text-sm sm:text-base text-gray-600">
            {filter === 'all' 
              ? 'All systems are operating normally. No security threats detected.'
              : `No ${filter} priority alerts at this time.`
            }
          </p>
        </div>
      ) : (
        <div className="space-y-3 sm:space-y-4">
          {filteredAlerts.map((alert) => (
            <div key={alert.id} className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6 hover:shadow-md transition-shadow">
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                {/* Alert Image */}
                <div className="w-full sm:w-24 h-32 sm:h-16 flex-shrink-0">
                  {alert.image ? (
                    <img
                      src={alert.image}
                      alt="Alert Evidence"
                      className="w-full h-full object-cover rounded-lg cursor-pointer hover:opacity-80 transition-opacity"
                      onClick={() => handleAlertSelect(alert)}
                    />
                  ) : (
                    <div 
                      className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors"
                      onClick={() => handleAlertSelect(alert)}
                    >
                      <i className="ri-image-line text-gray-400 text-xl"></i>
                    </div>
                  )}
                </div>

                {/* Alert Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-4 mb-2">
                    <div className="flex items-center space-x-2">
                      <i className={`${getAlertTypeIcon(alert.type)} text-lg ${
                        alert.severity === 'high' ? 'text-red-600' :
                        alert.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                      }`}></i>
                      <h3 className="font-medium text-gray-900 text-sm sm:text-base">
                        {alert.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Detected
                      </h3>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(alert.severity)} whitespace-nowrap`}>
                      <i className={`${getSeverityIcon(alert.severity)} mr-1`}></i>
                      {alert.severity.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div className="text-sm text-gray-600">
                      <div className="flex items-center space-x-4">
                        <span>
                          <i className="ri-map-pin-line mr-1"></i>
                          {alert.location}
                        </span>
                        <span>
                          <i className="ri-time-line mr-1"></i>
                          {formatTimestamp(alert.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-row sm:flex-col gap-2 sm:gap-1">
                  <button
                    onClick={() => handleAlertSelect(alert)}
                    className="flex-1 sm:flex-none px-3 py-1.5 text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors text-xs sm:text-sm whitespace-nowrap"
                  >
                    <i className="ri-eye-line mr-1"></i>
                    <span className="hidden sm:inline">View Details</span>
                    <span className="sm:hidden">View</span>
                  </button>
                  <button
                    onClick={() => dismissAlert(alert.id)}
                    className="flex-1 sm:flex-none px-3 py-1.5 text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors text-xs sm:text-sm whitespace-nowrap"
                  >
                    <i className="ri-close-line mr-1"></i>
                    <span className="hidden sm:inline">Dismiss</span>
                    <span className="sm:hidden">Dismiss</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
