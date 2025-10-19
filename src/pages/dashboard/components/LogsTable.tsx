
import { useState } from 'react';

interface Log {
  id: number;
  timestamp: string;
  event: string;
  location: string;
  confidence?: number;
  action?: string;
  image?: string;
}

interface LogsTableProps {
  logs: Log[];
  onRefresh?: () => void;
}

export default function LogsTable({ logs, onRefresh }: LogsTableProps) {
  const [dateFilter, setDateFilter] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [eventFilter, setEventFilter] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedLog, setSelectedLog] = useState<Log | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showBulkDeleteModal, setShowBulkDeleteModal] = useState(false);
  const [deletingLog, setDeletingLog] = useState<Log | null>(null);
  const [selectedLogs, setSelectedLogs] = useState<number[]>([]);
  const [selectAll, setSelectAll] = useState(false);

  const filteredLogs = logs.filter(log => {
    const matchesDate = !dateFilter || log.timestamp.includes(dateFilter);
    const matchesLocation = !locationFilter || log.location.toLowerCase().includes(locationFilter.toLowerCase());
    const matchesEvent = !eventFilter || log.event.toLowerCase().includes(eventFilter.toLowerCase());
    return matchesDate && matchesLocation && matchesEvent;
  });

  const refreshLogs = async () => {
    setIsRefreshing(true);
    try {
      if (onRefresh) {
        await onRefresh();
      }
    } catch (error) {
      console.error('Error refreshing logs:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const exportToCsv = () => {
    const headers = ['Timestamp', 'Event', 'Location', 'Confidence', 'Action'];
    const csvContent = [
      headers.join(','),
      ...filteredLogs.map(log => [
        log.timestamp,
        log.event,
        log.location,
        log.confidence,
        log.action
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'security_logs.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const viewLogDetails = (log: Log) => {
    setSelectedLog(log);
    setShowDetailModal(true);
  };

  const openDeleteModal = (log: Log) => {
    setDeletingLog(log);
    setShowDeleteModal(true);
  };

  const handleDeleteLog = () => {
    console.log('Delete log functionality disabled for security - logs are read-only');
    setShowDeleteModal(false);
    setDeletingLog(null);
  };

  const handleBulkDelete = () => {
    if (selectedLogs.length > 0) {
      console.log(`Bulk delete functionality disabled for security - logs are read-only`);
      console.log(`Would have deleted ${selectedLogs.length} logs`);
      
      setSelectedLogs([]);
      setSelectAll(false);
      setShowBulkDeleteModal(false);
    }
  };

  const toggleLogSelection = (logId: number) => {
    setSelectedLogs(prev => 
      prev.includes(logId) 
        ? prev.filter(id => id !== logId)
        : [...prev, logId]
    );
  };

  const toggleSelectAll = () => {
    if (selectAll) {
      setSelectedLogs([]);
    } else {
      setSelectedLogs(filteredLogs.map(log => log.id));
    }
    setSelectAll(!selectAll);
  };

  const getEventColor = (event: string) => {
    if (event.includes('Unauthorized') || event.includes('Suspicious')) {
      return 'text-red-600';
    } else if (event.includes('Normal')) {
      return 'text-green-600';
    }
    return 'text-gray-600';
  };

  const getDetailedDescription = (log: Log) => {
    if (log.event.includes('Unauthorized')) {
      return 'An unauthorized person has been detected in a restricted area. The AI system identified facial features that do not match any authorized personnel in the database. Immediate security response may be required.';
    } else if (log.event.includes('Suspicious')) {
      return 'Unusual behavior patterns have been detected. The person appears to be loitering or exhibiting movements that deviate from normal activity patterns. Continued monitoring is recommended.';
    } else if (log.event.includes('Normal')) {
      return 'Regular authorized activity has been logged. No security concerns detected. This entry is part of routine monitoring and documentation.';
    }
    return 'A security event has been detected and logged for review.';
  };

  const getRecommendedActions = (log: Log) => {
    if (log.event.includes('Unauthorized')) {
      return [
        'Immediately dispatch security personnel to the location',
        'Lock down the affected area if possible',
        'Contact local authorities if threat level is high',
        'Review access logs for potential security breaches',
        'Verify identity of the detected person'
      ];
    } else if (log.event.includes('Suspicious')) {
      return [
        'Continue monitoring the individual closely',
        'Alert nearby security personnel',
        'Prepare to escalate if behavior becomes threatening',
        'Document the incident for future reference',
        'Consider approaching for identification'
      ];
    } else if (log.event.includes('Normal')) {
      return [
        'No immediate action required',
        'Continue routine monitoring',
        'Log entry for audit purposes',
        'Maintain standard security protocols'
      ];
    }
    return ['Review the incident and take appropriate action'];
  };

  const downloadLogImage = (log: Log) => {
    if (!log.image) return;
    const link = document.createElement('a');
    link.download = `log_${log.id}_${new Date(log.timestamp).toISOString().split('T')[0]}.jpg`;
    link.href = log.image;
    link.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Event Logs</h2>
        <div className="flex items-center space-x-3">
          {selectedLogs.length > 0 && (
            <button
              onClick={() => setShowBulkDeleteModal(true)}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 whitespace-nowrap"
            >
              <i className="ri-delete-bin-line mr-2"></i>
              Delete Selected ({selectedLogs.length})
            </button>
          )}
          <button
            onClick={refreshLogs}
            disabled={isRefreshing}
            className={`px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap ${
              isRefreshing ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <i className={`ri-refresh-line mr-2 ${isRefreshing ? 'animate-spin' : ''}`}></i>
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          <button
            onClick={exportToCsv}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 whitespace-nowrap"
          >
            <i className="ri-file-excel-line mr-2"></i>
            Export CSV
          </button>
          <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 whitespace-nowrap">
            <i className="ri-file-pdf-line mr-2"></i>
            Export PDF
          </button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && deletingLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-4">
                <i className="ri-delete-bin-line text-2xl text-red-600"></i>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Delete Log Entry</h3>
                <p className="text-sm text-gray-600">Log ID: #{deletingLog.id.toString().padStart(6, '0')}</p>
              </div>
            </div>
            
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-2">
                <i className="ri-alert-line text-red-600 mr-2"></i>
                <span className="font-medium text-red-800">Warning: Permanent Action</span>
              </div>
              <p className="text-sm text-red-700">
                Are you sure you want to delete this log entry? This action cannot be undone and will permanently remove:
              </p>
              <ul className="mt-2 text-sm text-red-700 list-disc list-inside">
                <li>Event timestamp and details</li>
                <li>Associated snapshot image</li>
                <li>AI confidence data</li>
                <li>Action history</li>
              </ul>
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
              <h4 className="font-medium text-gray-900 mb-2">Log Details</h4>
              <div className="space-y-1 text-sm text-gray-600">
                <p><span className="font-medium">Event:</span> {deletingLog.event}</p>
                <p><span className="font-medium">Location:</span> {deletingLog.location}</p>
                <p><span className="font-medium">Time:</span> {new Date(deletingLog.timestamp).toLocaleString()}</p>
                <p><span className="font-medium">Confidence:</span> {deletingLog.confidence}%</p>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeletingLog(null);
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteLog}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 whitespace-nowrap"
              >
                <i className="ri-delete-bin-line mr-2"></i>
                Delete Log
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Delete Confirmation Modal */}
      {showBulkDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-4">
                <i className="ri-delete-bin-line text-2xl text-red-600"></i>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Delete Multiple Logs</h3>
                <p className="text-sm text-gray-600">{selectedLogs.length} logs selected</p>
              </div>
            </div>
            
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-2">
                <i className="ri-alert-line text-red-600 mr-2"></i>
                <span className="font-medium text-red-800">Critical Warning</span>
              </div>
              <p className="text-sm text-red-700">
                You are about to permanently delete <strong>{selectedLogs.length} log entries</strong>. 
                This action cannot be undone and will remove all associated data including snapshots and event details.
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-2">
                <i className="ri-information-line text-yellow-600 mr-2"></i>
                <span className="font-medium text-yellow-800">Recommendation</span>
              </div>
              <p className="text-sm text-yellow-700">
                Consider exporting these logs before deletion for compliance and audit purposes.
              </p>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowBulkDeleteModal(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
              >
                Cancel
              </button>
              <button
                onClick={handleBulkDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 whitespace-nowrap"
              >
                <i className="ri-delete-bin-line mr-2"></i>
                Delete {selectedLogs.length} Logs
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Log Detail Modal */}
      {showDetailModal && selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <i className="ri-file-list-3-line text-2xl text-blue-600"></i>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Event Log Details</h3>
                    <p className="text-sm text-gray-600">Log ID: #{selectedLog.id.toString().padStart(6, '0')}</p>
                  </div>
                </div>
                <button 
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <i className="ri-close-line text-2xl"></i>
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <div className="bg-gray-50 rounded-lg p-4 mb-6">
                    <img
                      src={selectedLog.image}
                      alt="Event snapshot"
                      className="w-full h-64 object-cover rounded-lg"
                    />
                    <div className="mt-3 flex justify-between items-center">
                      <span className="text-sm text-gray-600">Event Snapshot</span>
                      <button
                        onClick={() => downloadLogImage(selectedLog)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        <i className="ri-download-line mr-1"></i>
                        Download
                      </button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">Event Information</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Event Type:</span>
                          <span className={`text-sm font-medium ${getEventColor(selectedLog.event)}`}>
                            {selectedLog.event}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Location:</span>
                          <span className="text-sm font-medium text-gray-900">{selectedLog.location}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Timestamp:</span>
                          <span className="text-sm font-medium text-gray-900">
                            {new Date(selectedLog.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">AI Confidence:</span>
                          <div className="flex items-center">
                            <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${selectedLog.confidence}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-medium text-gray-900">{selectedLog.confidence}%</span>
                          </div>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Action Taken:</span>
                          <span className={`text-sm px-2 py-1 rounded-full font-medium ${
                            selectedLog.action === 'Alert Sent' 
                              ? 'bg-red-100 text-red-800'
                              : selectedLog.action === 'Monitoring'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {selectedLog.action}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center mb-3">
                      <i className="ri-information-line text-blue-600 mr-2"></i>
                      <h4 className="font-medium text-blue-900">Event Description</h4>
                    </div>
                    <p className="text-sm text-blue-800 leading-relaxed">
                      {getDetailedDescription(selectedLog)}
                    </p>
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex items-center mb-3">
                      <i className="ri-lightbulb-line text-yellow-600 mr-2"></i>
                      <h4 className="font-medium text-yellow-900">Recommended Actions</h4>
                    </div>
                    <ul className="space-y-2">
                      {getRecommendedActions(selectedLog).map((action, index) => (
                        <li key={index} className="flex items-start text-sm text-yellow-800">
                          <i className="ri-arrow-right-s-line text-yellow-600 mr-1 mt-0.5 flex-shrink-0"></i>
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-3">Technical Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Detection Model:</span>
                        <span className="text-gray-900">
                          {selectedLog.event.includes('Unauthorized') ? 'EfficientNet B7 Face Recognition' : 'YOLOv9 Activity Detection'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Processing Time:</span>
                        <span className="text-gray-900">0.23 seconds</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Camera ID:</span>
                        <span className="text-gray-900">CAM-{selectedLog.location.replace(/\s+/g, '').toUpperCase()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Resolution:</span>
                        <span className="text-gray-900">1920x1080</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={() => downloadLogImage(selectedLog)}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 whitespace-nowrap"
                    >
                      <i className="ri-download-line mr-2"></i>
                      Download Image
                    </button>
                    <button
                      onClick={() => {
                        const reportData = {
                          logId: selectedLog.id,
                          timestamp: selectedLog.timestamp,
                          event: selectedLog.event,
                          location: selectedLog.location,
                          confidence: selectedLog.confidence,
                          action: selectedLog.action,
                          description: getDetailedDescription(selectedLog),
                          recommendations: getRecommendedActions(selectedLog)
                        };
                        
                        const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `log_report_${selectedLog.id}_${new Date().toISOString().split('T')[0]}.json`;
                        a.click();
                        window.URL.revokeObjectURL(url);
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                    >
                      <i className="ri-file-download-line mr-2"></i>
                      Export Report
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex justify-end mt-6 pt-6 border-t border-gray-200">
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 whitespace-nowrap"
                >
                  Close Details
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <input
              type="text"
              placeholder="Filter by location"
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
            <select
              value={eventFilter}
              onChange={(e) => setEventFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
            >
              <option value="">All Events</option>
              <option value="unauthorized">Unauthorized Person</option>
              <option value="suspicious">Suspicious Activity</option>
              <option value="normal">Normal Activity</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setDateFilter('');
                setLocationFilter('');
                setEventFilter('');
              }}
              className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
            >
              <i className="ri-refresh-line mr-2"></i>
              Clear Filters
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4">
                  <input
                    type="checkbox"
                    checked={selectAll}
                    onChange={toggleSelectAll}
                    className="rounded"
                  />
                </th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Snapshot</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Timestamp</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Event</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Location</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Confidence</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Action</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log) => (
                <tr key={log.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <input
                      type="checkbox"
                      checked={selectedLogs.includes(log.id)}
                      onChange={() => toggleLogSelection(log.id)}
                      className="rounded"
                    />
                  </td>
                  <td className="py-3 px-4">
                    <img
                      src={log.image}
                      alt="Event snapshot"
                      className="w-16 h-12 object-cover rounded"
                    />
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className={`py-3 px-4 text-sm font-medium ${getEventColor(log.event)}`}>
                    {log.event}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">{log.location}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center">
                      <div className="w-12 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${log.confidence}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">{log.confidence}%</span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      log.action === 'Alert Sent' 
                        ? 'bg-red-100 text-red-800'
                        : log.action === 'Monitoring'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <button 
                        onClick={() => viewLogDetails(log)}
                        className="text-blue-600 hover:text-blue-800"
                        title="View Details"
                      >
                        <i className="ri-eye-line"></i>
                      </button>
                      <button 
                        onClick={() => downloadLogImage(log)}
                        className="text-green-600 hover:text-green-800"
                        title="Download Image"
                      >
                        <i className="ri-download-line"></i>
                      </button>
                      <button 
                        onClick={() => openDeleteModal(log)}
                        className="text-red-600 hover:text-red-800" 
                        title="Delete Log"
                      >
                        <i className="ri-delete-bin-line"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredLogs.length === 0 && (
          <div className="text-center py-8">
            <i className="ri-file-list-3-line text-4xl text-gray-400 mb-2"></i>
            <p className="text-gray-600">No logs found matching your filters</p>
          </div>
        )}
      </div>
    </div>
  );
}