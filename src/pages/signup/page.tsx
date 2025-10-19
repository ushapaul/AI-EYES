import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function Signup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    department: '',
    role: 'user',
    location: '',
    timezone: 'UTC'
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.firstName || !formData.email || !formData.password) {
      setError('Please fill in all required fields');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Ensure user data exists
        if (!data.user) {
          setError('Invalid server response. Please try again.');
          return;
        }

        // Store user data in localStorage
        console.log('Storing user data:', data.user);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Navigate to dashboard
        navigate('/dashboard');
      } else {
        setError(data.error || 'Registration failed. Please try again.');
      }
    } catch (err) {
      console.error('Signup error:', err);
      setError('Failed to connect to server. Please make sure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center px-4 py-8">
      <div className="max-w-5xl w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
        <div className="flex flex-col lg:flex-row">
          {/* Left Side - Branding */}
          <div className="lg:w-2/5 bg-gradient-to-br from-blue-600 to-indigo-700 p-8 text-white flex flex-col justify-center">
            <div className="mb-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                  <i className="ri-shield-check-line text-2xl text-blue-600"></i>
                </div>
                <div className="ml-3">
                  <h1 className="text-2xl font-bold">AI Eyes</h1>
                  <p className="text-blue-200 text-xs">Security System</p>
                </div>
              </div>
              
              <h2 className="text-2xl font-bold mb-3">Join AI Eyes Security</h2>
              <p className="text-blue-100 mb-6 text-sm">
                Create your account and start protecting what matters most with advanced AI-powered surveillance.
              </p>
              
              <div className="space-y-3">
                <div className="flex items-start">
                  <i className="ri-check-line text-xl mr-2 text-green-300"></i>
                  <div>
                    <h3 className="font-semibold text-sm">AI Face Recognition</h3>
                    <p className="text-xs text-blue-200">Powered by MobileNetV2</p>
                </div>
                <div className="flex items-start">
                  <i className="ri-check-line text-xl mr-2 text-green-300"></i>
                  <div>
                    <h3 className="font-semibold text-sm">Real-Time Alerts</h3>
                    <p className="text-xs text-blue-200">Instant email notifications</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <i className="ri-check-line text-xl mr-2 text-green-300"></i>
                  <div>
                    <h3 className="font-semibold text-sm">24/7 Monitoring</h3>
                    <p className="text-xs text-blue-200">Multi-camera surveillance</p>
                  </div>
                </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Signup Form */}
          <div className="lg:w-3/5 p-8">
            <div className="max-w-md mx-auto">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Create Account</h2>
                <p className="text-gray-600 text-sm">Fill in your details to get started</p>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start">
                  <i className="ri-error-warning-line text-red-600 text-lg mr-2 mt-0.5"></i>
                  <p className="text-xs text-red-800">{error}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1.5">
                      First Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1.5">
                      Last Name
                    </label>
                    <input
                      type="text"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1.5">
                    Email Address <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1.5">
                      Password <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1.5">
                      Confirm Password <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1.5">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1.5">
                      Department
                    </label>
                    <select
                      name="department"
                      value={formData.department}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    >
                      <option value="">Select Department</option>
                      <option value="Security Operations">Security Operations</option>
                      <option value="IT Department">IT Department</option>
                      <option value="Management">Management</option>
                      <option value="Facility Management">Facility Management</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1.5">
                    Timezone
                  </label>
                  <select
                    name="timezone"
                    value={formData.timezone}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                    <option value="Asia/Kolkata">India Standard Time</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1.5">
                    Location
                  </label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-blue-600 text-white py-2.5 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center text-sm"
                >
                  {isLoading ? (
                    <>
                      <i className="ri-loader-4-line animate-spin mr-2"></i>
                      Creating Account...
                    </>
                  ) : (
                    <>
                      <i className="ri-user-add-line mr-2"></i>
                      Create Account
                    </>
                  )}
                </button>

                <p className="text-center text-sm text-gray-600 mt-6">
                  Already have an account?{' '}
                  <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                    Sign in here
                  </Link>
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
