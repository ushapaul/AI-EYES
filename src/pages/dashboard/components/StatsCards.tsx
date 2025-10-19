
interface Alert {
  id: number | string; // Support both MongoDB ObjectId (string) and integer IDs
  type: string;
  location: string;
  timestamp: string;
  severity: string;
  image?: string;
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

interface Stats {
  total_cameras?: number;
  active_cameras?: number;
  total_alerts_today?: number;
  detection_accuracy?: number;
  uptime?: string;
}

interface StatsCardsProps {
  alerts: Alert[];
  logs: Log[];
  stats?: Stats;
  isConnected?: boolean;  // Add isConnected prop
}

export default function StatsCards({ alerts, logs, stats, isConnected = true }: StatsCardsProps) {
  const highSeverityAlerts = alerts.filter(alert => alert.severity === 'high').length;
  const recentLogs = logs.filter(log => {
    const logTime = new Date(log.timestamp).getTime();
    const oneHourAgo = Date.now() - (60 * 60 * 1000);
    return logTime > oneHourAgo;
  }).length;

  // When disconnected, show 0 or N/A instead of fallback values
  const getDisplayValue = (value: any, fallback: any = '0') => {
    if (!isConnected) return '0';
    return value !== undefined ? value : fallback;
  };

  const getDisplayPercentage = (value: any, fallback: any = '0') => {
    if (!isConnected) return '0';
    return value !== undefined ? value : fallback;
  };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
      {/* Active Cameras */}
      <div className="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Active Cameras</p>
            <p className="text-xl sm:text-3xl font-bold text-gray-900">{getDisplayValue(stats?.active_cameras, 0)}</p>
            <p className={`text-xs mt-1 ${isConnected ? 'text-green-600' : 'text-gray-500'}`}>
              <i className="ri-arrow-up-line mr-1"></i>
              <span className="hidden sm:inline">{isConnected ? 'All systems operational' : 'System offline'}</span>
              <span className="sm:hidden">{isConnected ? 'Online' : 'Offline'}</span>
            </p>
          </div>
          <div className={`w-8 h-8 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center ${isConnected ? 'bg-green-100' : 'bg-gray-100'}`}>
            <i className={`ri-camera-line text-lg sm:text-2xl ${isConnected ? 'text-green-600' : 'text-gray-400'}`}></i>
          </div>
        </div>
      </div>

      {/* Active Alerts */}
      <div className="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Active Alerts</p>
            <p className="text-xl sm:text-3xl font-bold text-gray-900">{alerts.length}</p>
            <p className={`text-xs mt-1 ${isConnected ? 'text-red-600' : 'text-gray-500'}`}>
              <i className="ri-alert-line mr-1"></i>
              <span className="hidden sm:inline">{isConnected ? `${highSeverityAlerts} high priority` : 'No data'}</span>
              <span className="sm:hidden">{isConnected ? `${highSeverityAlerts} high` : 'N/A'}</span>
            </p>
          </div>
          <div className={`w-8 h-8 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center ${isConnected ? 'bg-red-100' : 'bg-gray-100'}`}>
            <i className={`ri-alarm-warning-line text-lg sm:text-2xl ${isConnected ? 'text-red-600' : 'text-gray-400'}`}></i>
          </div>
        </div>
      </div>

      {/* Detection Rate */}
      <div className="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Detection Rate</p>
            <p className="text-xl sm:text-3xl font-bold text-gray-900">{getDisplayPercentage(stats?.detection_accuracy, 0)}%</p>
            <p className={`text-xs mt-1 ${isConnected ? 'text-blue-600' : 'text-gray-500'}`}>
              <i className="ri-line-chart-line mr-1"></i>
              <span className="hidden sm:inline">{isConnected ? 'Excellent performance' : 'No data available'}</span>
              <span className="sm:hidden">{isConnected ? 'Excellent' : 'N/A'}</span>
            </p>
          </div>
          <div className={`w-8 h-8 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center ${isConnected ? 'bg-blue-100' : 'bg-gray-100'}`}>
            <i className={`ri-radar-line text-lg sm:text-2xl ${isConnected ? 'text-blue-600' : 'text-gray-400'}`}></i>
          </div>
        </div>
      </div>

      {/* Recent Events */}
      <div className="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">Recent Events</p>
            <p className="text-xl sm:text-3xl font-bold text-gray-900">{recentLogs}</p>
            <p className={`text-xs mt-1 ${isConnected ? 'text-purple-600' : 'text-gray-500'}`}>
              <i className="ri-time-line mr-1"></i>
              <span className="hidden sm:inline">{isConnected ? 'Last hour' : 'No data'}</span>
              <span className="sm:hidden">{isConnected ? '1hr' : 'N/A'}</span>
            </p>
          </div>
          <div className={`w-8 h-8 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center ${isConnected ? 'bg-purple-100' : 'bg-gray-100'}`}>
            <i className={`ri-file-list-3-line text-lg sm:text-2xl ${isConnected ? 'text-purple-600' : 'text-gray-400'}`}></i>
          </div>
        </div>
      </div>
    </div>
  );
}
