
import { useState, useEffect } from 'react';
import Header from '../dashboard/components/Header';
import { useProfile } from '../../hooks/useProfile';

export default function Profile() {
  const { user, loading, error: profileError, updateProfile, updatePassword } = useProfile();
  const [activeTab, setActiveTab] = useState('personal');
  const [isEditing, setIsEditing] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [showDeleteAccount, setShowDeleteAccount] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    department: '',
    role: '',
    location: '',
    timezone: '',
  });

  // Load user data into form when user data is fetched
  useEffect(() => {
    if (user) {
      setProfileData({
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        email: user.email || '',
        phone: user.phone || '',
        department: user.department || '',
        role: user.role || '',
        location: user.location || '',
        timezone: user.timezone || '',
      });
    }
  }, [user]);

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [notificationSettings, setNotificationSettings] = useState({
    emailAlerts: true,
    smsAlerts: true,
    pushNotifications: true,
    criticalAlerts: true,
    systemUpdates: false,
    weeklyReports: true,
    maintenanceNotices: true,
    alertSound: true,
    desktopNotifications: true,
    mobileNotifications: true
  });

  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: true,
    sessionTimeout: '30',
    loginNotifications: true,
    deviceTracking: true,
    ipWhitelist: false,
    apiAccess: false
  });

  const handleSaveProfile = async () => {
    try {
      setSaveError(null);
      setSaveSuccess(false);

      // Prepare updates (exclude email as it shouldn't be changed from profile page)
      const updates = {
        firstName: profileData.firstName,
        lastName: profileData.lastName,
        phone: profileData.phone,
        department: profileData.department,
        location: profileData.location,
        timezone: profileData.timezone,
      };

      const result = await updateProfile(updates);
      
      if (result.success) {
        setIsEditing(false);
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      } else {
        setSaveError(result.error || 'Failed to update profile');
      }
    } catch (err) {
      setSaveError('An unexpected error occurred');
      console.error('Save profile error:', err);
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setSaveError('New passwords do not match!');
      return;
    }
    
    if (passwordData.newPassword.length < 6) {
      setSaveError('Password must be at least 6 characters long!');
      return;
    }

    try {
      setSaveError(null);
      
      const result = await updatePassword({
        oldPassword: passwordData.currentPassword,
        newPassword: passwordData.newPassword,
      });

      if (result.success) {
        setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
        setShowChangePassword(false);
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      } else {
        setSaveError(result.error || 'Failed to change password');
      }
    } catch (err) {
      setSaveError('An unexpected error occurred');
      console.error('Change password error:', err);
    }
  };

  const handleDeleteAccount = () => {
    console.log('Account deletion requested');
    setShowDeleteAccount(false);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleNotificationToggle = (setting: string) => {
    setNotificationSettings(prev => ({
      ...prev,
      [setting]: !prev[setting as keyof typeof prev]
    }));
  };

  const handleSecurityToggle = (setting: string) => {
    setSecuritySettings(prev => ({
      ...prev,
      [setting]: setting === 'sessionTimeout' ? prev[setting as keyof typeof prev] : !prev[setting as keyof typeof prev]
    }));
  };

  // Helper function to format role display
  const formatRole = (role: string) => {
    const roleMap: { [key: string]: string } = {
      'admin': 'Administrator',
      'security_admin': 'Security Administrator',
      'user': 'User',
      'viewer': 'Viewer'
    };
    return roleMap[role] || role;
  };

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <i className="ri-loader-4-line text-4xl text-blue-600 animate-spin mb-4"></i>
              <p className="text-gray-600">Loading profile...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (profileError && !user) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <i className="ri-error-warning-line text-4xl text-red-600 mb-4"></i>
              <p className="text-gray-600 mb-4">{profileError}</p>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="mb-6">
          <div className="flex items-center mb-2">
            <button 
              onClick={() => window.history.back()}
              className="mr-4 p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <i className="ri-arrow-left-line text-xl"></i>
            </button>
            <h1 className="text-3xl font-bold text-gray-900">User Profile</h1>
          </div>
          <p className="text-gray-600">Manage your account settings and security preferences</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Profile Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-center mb-6">
                <div className="relative inline-block">
                  <div className="w-24 h-24 rounded-full bg-blue-600 flex items-center justify-center text-white text-3xl font-bold mx-auto">
                    {profileData.firstName.charAt(0).toUpperCase()}{profileData.lastName ? profileData.lastName.charAt(0).toUpperCase() : ''}
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mt-4">
                  {profileData.firstName} {profileData.lastName}
                </h3>
                <p className="text-sm text-gray-600">{formatRole(profileData.role)}</p>
                <p className="text-sm text-gray-500">{profileData.department || 'No Department'}</p>
              </div>

              <nav className="space-y-2">
                <button
                  onClick={() => setActiveTab('personal')}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'personal'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <i className="ri-user-line mr-2"></i>
                  Personal Info
                </button>
                <button
                  onClick={() => setActiveTab('security')}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'security'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <i className="ri-shield-line mr-2"></i>
                  Security
                </button>
                <button
                  onClick={() => setActiveTab('notifications')}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'notifications'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <i className="ri-notification-line mr-2"></i>
                  Notifications
                </button>
                <button
                  onClick={() => setActiveTab('activity')}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'activity'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <i className="ri-history-line mr-2"></i>
                  Activity Log
                </button>
                <button
                  onClick={() => setActiveTab('preferences')}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'preferences'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <i className="ri-settings-line mr-2"></i>
                  Preferences
                </button>
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Success Message */}
            {saveSuccess && (
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start">
                <i className="ri-check-circle-line text-green-600 text-xl mr-3 mt-0.5"></i>
                <p className="text-sm text-green-800">Changes saved successfully!</p>
              </div>
            )}

            {/* Error Message */}
            {saveError && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
                <i className="ri-error-warning-line text-red-600 text-xl mr-3 mt-0.5"></i>
                <p className="text-sm text-red-800">{saveError}</p>
              </div>
            )}

            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Personal Information Tab */}
              {activeTab === 'personal' && (
                <div className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">Personal Information</h2>
                    <button
                      onClick={() => setIsEditing(!isEditing)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap ${
                        isEditing
                          ? 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      <i className={`${isEditing ? 'ri-close-line' : 'ri-edit-line'} mr-2`}></i>
                      {isEditing ? 'Cancel' : 'Edit Profile'}
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                      <input
                        type="text"
                        value={profileData.firstName}
                        onChange={(e) => setProfileData(prev => ({ ...prev, firstName: e.target.value }))}
                        disabled={!isEditing}
                        className={`w-full px-3 py-2 border border-gray-300 rounded-lg text-sm ${
                          !isEditing ? 'bg-gray-50 text-gray-500' : ''
                        }`}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                      <input
                        type="text"
                        value={profileData.lastName}
                        onChange={(e) => setProfileData(prev => ({ ...prev, lastName: e.target.value }))}
                        disabled={!isEditing}
                        className={`w-full px-3 py-2 border border-gray-300 rounded-lg text-sm ${
                          !isEditing ? 'bg-gray-50 text-gray-500' : ''
                        }`}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                      <input
                        type="email"
                        value={profileData.email}
                        disabled={true}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50 text-gray-500 cursor-not-allowed"
                      />
                      <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                      <input
                        type="tel"
                        value={profileData.phone}
                        onChange={(e) => setProfileData(prev => ({ ...prev, phone: e.target.value }))}
                        disabled={!isEditing}
                        className={`w-full px-3 py-2 border border-gray-300 rounded-lg text-sm ${
                          !isEditing ? 'bg-gray-50 text-gray-500' : ''
                        }`}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
                      <select
                        value={profileData.department}
                        onChange={(e) => setProfileData(prev => ({ ...prev, department: e.target.value }))}
                        disabled={!isEditing}
                        className={`w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8 ${
                          !isEditing ? 'bg-gray-50 text-gray-500' : ''
                        }`}
                      >
                        <option value="Security Operations">Security Operations</option>
                        <option value="IT Security">IT Security</option>
                        <option value="Facility Management">Facility Management</option>
                        <option value="Administration">Administration</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                      <select
                        value={profileData.role}
                        onChange={(e) => setProfileData(prev => ({ ...prev, role: e.target.value }))}
                        disabled={!isEditing}
                        className={`w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8 ${
                          !isEditing ? 'bg-gray-50 text-gray-500' : ''
                        }`}
                      >
                        <option value="Security Administrator">Security Administrator</option>
                        <option value="Security Operator">Security Operator</option>
                        <option value="System Administrator">System Administrator</option>
                        <option value="Supervisor">Supervisor</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                      <input
                        type="text"
                        value={profileData.location}
                        onChange={(e) => setProfileData(prev => ({ ...prev, location: e.target.value }))}
                        disabled={!isEditing}
                        className={`w-full px-3 py-2 border border-gray-300 rounded-lg text-sm ${
                          !isEditing ? 'bg-gray-50 text-gray-500' : ''
                        }`}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                      <select
                        value={profileData.timezone}
                        onChange={(e) => setProfileData(prev => ({ ...prev, timezone: e.target.value }))}
                        disabled={!isEditing}
                        className={`w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8 ${
                          !isEditing ? 'bg-gray-50 text-gray-500' : ''
                        }`}
                      >
                        <option value="America/New_York">Eastern Time (ET)</option>
                        <option value="America/Chicago">Central Time (CT)</option>
                        <option value="America/Denver">Mountain Time (MT)</option>
                        <option value="America/Los_Angeles">Pacific Time (PT)</option>
                        <option value="UTC">UTC</option>
                      </select>
                    </div>
                  </div>

                  {isEditing && (
                    <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
                      <button
                        onClick={() => setIsEditing(false)}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleSaveProfile}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 whitespace-nowrap"
                      >
                        <i className="ri-save-line mr-2"></i>
                        Save Changes
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Security Tab */}
              {activeTab === 'security' && (
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">Security Settings</h2>

                  <div className="space-y-6">
                    {/* Password Section */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">Password</h3>
                          <p className="text-sm text-gray-600">Last changed 30 days ago</p>
                        </div>
                        <button
                          onClick={() => setShowChangePassword(true)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 whitespace-nowrap"
                        >
                          <i className="ri-lock-line mr-2"></i>
                          Change Password
                        </button>
                      </div>
                    </div>

                    {/* Two-Factor Authentication */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">Two-Factor Authentication</h3>
                          <p className="text-sm text-gray-600">Add an extra layer of security to your account</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={securitySettings.twoFactorAuth}
                            onChange={() => handleSecurityToggle('twoFactorAuth')}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                    </div>

                    {/* Session Settings */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Session Settings</h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout (minutes)</label>
                          <select
                            value={securitySettings.sessionTimeout}
                            onChange={(e) => setSecuritySettings(prev => ({ ...prev, sessionTimeout: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8"
                          >
                            <option value="15">15 minutes</option>
                            <option value="30">30 minutes</option>
                            <option value="60">1 hour</option>
                            <option value="120">2 hours</option>
                            <option value="480">8 hours</option>
                          </select>
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">Login Notifications</h4>
                            <p className="text-sm text-gray-600">Get notified when someone logs into your account</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={securitySettings.loginNotifications}
                              onChange={() => handleSecurityToggle('loginNotifications')}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">Device Tracking</h4>
                            <p className="text-sm text-gray-600">Track devices that access your account</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={securitySettings.deviceTracking}
                              onChange={() => handleSecurityToggle('deviceTracking')}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>
                      </div>
                    </div>

                    {/* Danger Zone */}
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <h3 className="text-lg font-medium text-red-900 mb-4">Danger Zone</h3>
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-red-900">Delete Account</h4>
                          <p className="text-sm text-red-700">Permanently delete your account and all associated data</p>
                        </div>
                        <button
                          onClick={() => setShowDeleteAccount(true)}
                          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 whitespace-nowrap"
                        >
                          <i className="ri-delete-bin-line mr-2"></i>
                          Delete Account
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Notifications Tab */}
              {activeTab === 'notifications' && (
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">Notification Preferences</h2>

                  <div className="space-y-6">
                    {/* Alert Notifications */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Security Alerts</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">Email Alerts</h4>
                            <p className="text-sm text-gray-600">Receive security alerts via email</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={notificationSettings.emailAlerts}
                              onChange={() => handleNotificationToggle('emailAlerts')}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">SMS Alerts</h4>
                            <p className="text-sm text-gray-600">Receive critical alerts via SMS</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={notificationSettings.smsAlerts}
                              onChange={() => handleNotificationToggle('smsAlerts')}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">Push Notifications</h4>
                            <p className="text-sm text-gray-600">Browser push notifications for real-time alerts</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={notificationSettings.pushNotifications}
                              onChange={() => handleNotificationToggle('pushNotifications')}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>
                      </div>
                    </div>

                    {/* System Notifications */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">System Notifications</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">System Updates</h4>
                            <p className="text-sm text-gray-600">Notifications about system updates and maintenance</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={notificationSettings.systemUpdates}
                              onChange={() => handleNotificationToggle('systemUpdates')}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">Weekly Reports</h4>
                            <p className="text-sm text-gray-600">Weekly security summary reports</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={notificationSettings.weeklyReports}
                              onChange={() => handleNotificationToggle('weeklyReports')}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>
                      </div>
                    </div>

                    {/* Sound & Display */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Sound & Display</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">Alert Sound</h4>
                            <p className="text-sm text-gray-600">Play sound for critical alerts</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={notificationSettings.alertSound}
                              onChange={() => handleNotificationToggle('alertSound')}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">Desktop Notifications</h4>
                            <p className="text-sm text-gray-600">Show desktop notifications when browser is minimized</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={notificationSettings.desktopNotifications}
                              onChange={() => handleNotificationToggle('desktopNotifications')}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Activity Log Tab */}
              {activeTab === 'activity' && (
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">Activity Log</h2>

                  <div className="text-center py-12">
                    <i className="ri-history-line text-6xl text-gray-300 mb-4"></i>
                    <p className="text-gray-500 mb-2">Activity logging coming soon</p>
                    <p className="text-sm text-gray-400">Your login history and account activities will be tracked here</p>
                  </div>
                </div>
              )}

              {/* Preferences Tab */}
              {activeTab === 'preferences' && (
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">System Preferences</h2>

                  <div className="space-y-6">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Display Settings</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
                          <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8">
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="auto">Auto</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Dashboard Settings</h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Default View</label>
                          <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8">
                            <option value="live">Live Streams</option>
                            <option value="alerts">Security Alerts</option>
                            <option value="logs">Event Logs</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Refresh Interval</label>
                          <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-8">
                            <option value="5">5 seconds</option>
                            <option value="10">10 seconds</option>
                            <option value="30">30 seconds</option>
                            <option value="60">1 minute</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Change Password Modal */}
        {showChangePassword && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                  <i className="ri-lock-line text-2xl text-blue-600"></i>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Change Password</h3>
                  <p className="text-sm text-gray-600">Update your account password</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                  <input
                    type="password"
                    value={passwordData.currentPassword}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="Enter current password"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                  <input
                    type="password"
                    value={passwordData.newPassword}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="Enter new password"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                  <input
                    type="password"
                    value={passwordData.confirmPassword}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="Confirm new password"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowChangePassword(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                >
                  Cancel
                </button>
                <button
                  onClick={handleChangePassword}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 whitespace-nowrap"
                >
                  <i className="ri-save-line mr-2"></i>
                  Update Password
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Account Modal */}
        {showDeleteAccount && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-4">
                  <i className="ri-delete-bin-line text-2xl text-red-600"></i>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Delete Account</h3>
                  <p className="text-sm text-gray-600">This action cannot be undone</p>
                </div>
              </div>

              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-center mb-2">
                  <i className="ri-alert-line text-red-600 mr-2"></i>
                  <span className="font-medium text-red-800">Warning: Permanent Action</span>
                </div>
                <p className="text-sm text-red-700">
                  Deleting your account will permanently remove all your data, settings, and access to the security system. This action cannot be reversed.
                </p>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowDeleteAccount(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteAccount}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 whitespace-nowrap"
                >
                  <i className="ri-delete-bin-line mr-2"></i>
                  Delete Account
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
