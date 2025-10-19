import { useState, useEffect } from 'react';

interface User {
  _id: string;
  email: string;
  firstName: string;
  lastName?: string;
  phone?: string;
  department?: string;
  role: string;
  location?: string;
  timezone?: string;
  createdAt: string;
  lastLogin?: string;
}

interface PasswordUpdate {
  oldPassword: string;
  newPassword: string;
}

export const useProfile = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get user from localStorage first for immediate display
      const storedUser = localStorage.getItem('user');
      
      console.log('Stored user from localStorage:', storedUser);
      
      if (!storedUser || storedUser === 'undefined' || storedUser === 'null') {
        throw new Error('No user found in session. Please login again.');
      }

      let userData;
      try {
        userData = JSON.parse(storedUser);
      } catch (parseError) {
        console.error('Failed to parse user data:', parseError);
        throw new Error('Invalid session data. Please login again.');
      }

      if (!userData || !userData.id) {
        throw new Error('Invalid user data. Please login again.');
      }
      
      // Set initial user data from localStorage
      console.log('Setting user data:', userData);
      setUser(userData);
      setLoading(false);

      // Then fetch fresh data from API in the background
      const userId = userData.id;
      const response = await fetch(`http://localhost:8000/api/users/${userId}`);
      
      if (!response.ok) {
        // If API fails, keep using localStorage data
        console.warn('Failed to fetch fresh user data, using cached data');
        return;
      }

      const data = await response.json();
      
      // Check if response contains user data
      if (data.user) {
        setUser(data.user);
        // Update localStorage with fresh data
        localStorage.setItem('user', JSON.stringify(data.user));
      } else if (data.id) {
        // Response is the user object directly
        setUser(data);
        localStorage.setItem('user', JSON.stringify(data));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load profile';
      setError(errorMessage);
      console.error('Profile fetch error:', err);
      setLoading(false);
    }
  };

  const updateProfile = async (updates: Partial<User>) => {
    try {
      setError(null);

      const storedUser = localStorage.getItem('user');
      if (!storedUser) {
        throw new Error('No user found in session');
      }

      const userData = JSON.parse(storedUser);
      const userId = userData._id || userData.id;

      const response = await fetch(`http://localhost:8000/api/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update profile');
      }

      const data = await response.json();
      setUser(data.user);

      // Update localStorage with new user data
      localStorage.setItem('user', JSON.stringify(data.user));

      return { success: true, user: data.user };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update profile';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const updatePassword = async (passwordData: PasswordUpdate) => {
    try {
      setError(null);

      const storedUser = localStorage.getItem('user');
      if (!storedUser) {
        throw new Error('No user found in session');
      }

      const userData = JSON.parse(storedUser);
      const userId = userData._id || userData.id;

      const response = await fetch(`http://localhost:8000/api/users/${userId}/password`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(passwordData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update password');
      }

      const data = await response.json();
      return { success: true, message: data.message };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update password';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  useEffect(() => {
    fetchUserProfile();
  }, []);

  return {
    user,
    loading,
    error,
    updateProfile,
    updatePassword,
    refreshProfile: fetchUserProfile,
  };
};
