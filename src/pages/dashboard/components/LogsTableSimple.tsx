import { useState } from 'react';

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

interface LogsTableProps {
  logs: Log[];
  onRefresh?: () => void;
}

export default function LogsTableSimple({ logs, onRefresh }: LogsTableProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedLog, setSelectedLog] = useState<Log | null>(null);

  const handleRefresh = async () => {
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

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getEventIcon = (action: string) => {
    const actionLower = action.toLowerCase();
    if (actionLower.includes('intruder') || actionLower.includes('unknown')) {
      return 'ri-user-forbid-line text-red-600';
    } else if (actionLower.includes('alert') || actionLower.includes('escalat')) {
      return 'ri-alarm-warning-line text-yellow-600';
    } else if (actionLower.includes('dismiss') || actionLower.includes('acknowledg')) {
      return 'ri-check-line text-green-600';
    } else {
      return 'ri-information-line text-blue-600';
    }
  };

  const getEventColor = (action: string) => {
    const actionLower = action.toLowerCase();
    if (actionLower.includes('intruder') || actionLower.includes('unknown')) {
      return 'border-l-4 border-red-500';
    } else if (actionLower.includes('alert') || actionLower.includes('escalat')) {
      return 'border-l-4 border-yellow-500';
    } else if (actionLower.includes('dismiss') || actionLower.includes('acknowledg')) {
      return 'border-l-4 border-green-500';
    } else {
      return 'border-l-4 border-blue-500';
    }
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 sm:mb-6">
        <div>
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-1">Event Logs</h2>
          <p className="text-sm text-gray-600">Security events and system activities</p>
        </div>
        
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="mt-3 sm:mt-0 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
        >
          {isRefreshing ? (
            <>
              <i className="ri-loader-4-line animate-spin mr-2"></i>
              Refreshing...
            </>
          ) : (
            <>
              <i className="ri-refresh-line mr-2"></i>
              Refresh
            </>
          )}
        </button>
      </div>

      {/* Log Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-4 sm:mb-6">
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900">Log Details</h3>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <i className="ri-close-line text-xl sm:text-2xl"></i>
                </button>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Event Information</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Action:</span>
                      <span className="font-medium">{selectedLog.action}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Camera/Location:</span>
                      <span className="font-medium">{selectedLog.camera_id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Timestamp:</span>
                      <span className="font-medium">{formatTimestamp(selectedLog.timestamp)}</span>
                    </div>
                    {selectedLog.description && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Description:</span>
                        <span className="font-medium">{selectedLog.description}</span>
                      </div>
                    )}
                    {selectedLog.level && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Level:</span>
                        <span className="font-medium uppercase">{selectedLog.level}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex justify-end mt-6">
                <button
                  onClick={() => setSelectedLog(null)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Logs List */}
      {logs.length === 0 ? (
        <div className="text-center py-8 sm:py-12">
          <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i className="ri-file-list-3-line text-gray-400 text-2xl sm:text-3xl"></i>
          </div>
          <h3 className="text-lg sm:text-xl font-medium text-gray-900 mb-2">No Logs Available</h3>
          <p className="text-sm sm:text-base text-gray-600">
            Event logs will appear here when security events are detected.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                  <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Camera/Location
                  </th>
                  <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs.map((log) => (
                  <tr 
                    key={log.id} 
                    className={`hover:bg-gray-50 cursor-pointer ${getEventColor(log.action)}`}
                    onClick={() => setSelectedLog(log)}
                  >
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <i className={`${getEventIcon(log.action)} mr-2 text-lg`}></i>
                        <div>
                          <div className="text-sm font-medium text-gray-900">{log.action}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{log.camera_id}</div>
                    </td>
                    <td className="px-3 sm:px-6 py-4">
                      <div className="text-sm text-gray-900">{log.description || '-'}</div>
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{formatTimestamp(log.timestamp)}</div>
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedLog(log);
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}