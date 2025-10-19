
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  isConnected?: boolean;
}

export default function Header({ isConnected = true }: HeaderProps) {
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  const handleLogout = () => {
    // Clear all user session data
    localStorage.removeItem('user');
    localStorage.removeItem('userId');
    localStorage.clear();
    
    // Navigate to login page
    navigate('/login');
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6">
        <div className="flex justify-between items-center h-14 sm:h-16">
          {/* Logo and Brand */}
          <button 
            onClick={() => navigate('/')}
            className="flex items-center space-x-2 sm:space-x-3 hover:opacity-80 transition-opacity"
          >
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-blue-600 rounded-xl flex items-center justify-center">
              <i className="ri-eye-line text-white text-lg sm:text-xl"></i>
            </div>
            <div className="text-left">
              <h1 className="text-lg sm:text-xl font-bold text-gray-900">AI Eyes Security</h1>
              <p className="text-xs sm:text-sm text-gray-500 hidden sm:block">Security Dashboard</p>
            </div>
          </button>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              <i className="ri-dashboard-line mr-2"></i>
              Dashboard
            </button>
            <button
              onClick={() => navigate('/settings')}
              className="text-gray-600 hover:text-gray-700 font-medium"
            >
              <i className="ri-settings-3-line mr-2"></i>
              Settings
            </button>
            <button
              onClick={() => navigate('/profile')}
              className="text-gray-600 hover:text-gray-700 font-medium"
            >
              <i className="ri-user-line mr-2"></i>
              Profile
            </button>
          </nav>

          {/* Desktop User Menu */}
          <div className="hidden md:flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">System Online</span>
            </div>
            
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 p-2 rounded-lg hover:bg-gray-100"
              >
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <i className="ri-user-line text-blue-600"></i>
                </div>
                <span className="font-medium">Admin</span>
                <i className="ri-arrow-down-s-line"></i>
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                  <button
                    onClick={() => navigate('/profile')}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <i className="ri-user-line mr-3"></i>
                    Profile Settings
                  </button>
                  <button
                    onClick={() => navigate('/settings')}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <i className="ri-settings-3-line mr-3"></i>
                    System Settings
                  </button>
                  <hr className="my-1" />
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center"
                  >
                    <i className="ri-logout-box-line mr-3"></i>
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-600">Online</span>
            </div>
            <button
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
            >
              <i className={`${showMobileMenu ? 'ri-close-line' : 'ri-menu-line'} text-xl`}></i>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {showMobileMenu && (
          <div className="md:hidden border-t border-gray-200 py-4">
            <div className="space-y-1">
              <button
                onClick={() => {
                  navigate('/dashboard');
                  setShowMobileMenu(false);
                }}
                className="w-full text-left px-3 py-2 text-blue-600 bg-blue-50 rounded-lg font-medium flex items-center"
              >
                <i className="ri-dashboard-line mr-3 w-5 h-5 flex items-center justify-center"></i>
                Dashboard
              </button>
              <button
                onClick={() => {
                  navigate('/settings');
                  setShowMobileMenu(false);
                }}
                className="w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium flex items-center"
              >
                <i className="ri-settings-3-line mr-3 w-5 h-5 flex items-center justify-center"></i>
                Settings
              </button>
              <button
                onClick={() => {
                  navigate('/profile');
                  setShowMobileMenu(false);
                }}
                className="w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium flex items-center"
              >
                <i className="ri-user-line mr-3 w-5 h-5 flex items-center justify-center"></i>
                Profile
              </button>
              <hr className="my-2" />
              <div className="px-3 py-2">
                <div className="flex items-center space-x-2 mb-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <i className="ri-user-line text-blue-600"></i>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Admin</p>
                    <p className="text-xs text-gray-500">System Administrator</p>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg font-medium flex items-center"
                >
                  <i className="ri-logout-box-line mr-3 w-5 h-5 flex items-center justify-center"></i>
                  Logout
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
