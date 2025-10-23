import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config';
import { FaSpinner } from 'react-icons/fa';

// API utility function
const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `JWT ${token}` }),
    ...options.headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include'
    });

    // If unauthorized, try to refresh token
    if (response.status === 401 && refreshToken && !endpoint.includes('token')) {
      const refreshResponse = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
        credentials: 'include'
      });

      if (refreshResponse.ok) {
        const { access } = await refreshResponse.json();
        localStorage.setItem('access_token', access);
        
        // Retry the original request with new token
        return apiRequest(endpoint, {
          ...options,
          headers: {
            ...headers,
            'Authorization': `JWT ${access}`,
          },
        });
      } else {
        // If refresh fails, clear tokens and throw error
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        throw new Error('Session expired. Please log in again.');
      }
    }

    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      throw new Error(data.detail || 'Something went wrong');
    }

    return data;
  } catch (error) {
    console.error('API Request Error:', error);
    throw error;
  }
};

export default function DashboardPage() {
  const [userData, setUserData] = useState(null);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { logout } = useAuth();
  const navigate = useNavigate();

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch user profile and programs in parallel
      const [profileData, programsData] = await Promise.all([
        apiRequest('/auth/users/me/'),
        apiRequest('/programs/enrolled/').catch(() => []) // Handle if programs endpoint fails
      ]);
      
      setUserData(profileData);
      setPrograms(Array.isArray(programsData) ? programsData : []);
      
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message || 'Failed to load dashboard data');
      
      // If unauthorized, redirect to login
      if (err.message.includes('Session expired') || err.message.includes('401')) {
        logout();
        navigate('/login', { state: { from: '/dashboard' } });
      }
    } finally {
      setLoading(false);
    }
  }, [navigate, logout]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <FaSpinner className="animate-spin text-blue-500 text-4xl mb-4 mx-auto" />
          <h2 className="text-xl font-semibold">Loading Dashboard...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="bg-white p-6 rounded-lg shadow-md max-w-md w-full">
          <h2 className="text-xl font-semibold text-red-600 mb-4">Error</h2>
          <p className="text-gray-700 mb-6">
            {error.includes('Session expired') ? 'Your session has expired. Please log in again.' : error}
          </p>
          <div className="space-y-3">
            <button
              onClick={fetchData}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
            >
              Try Again
            </button>
            <button
              onClick={handleLogout}
              className="w-full bg-gray-200 text-gray-800 py-2 px-4 rounded hover:bg-gray-300"
            >
              Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {userData && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Welcome, {userData.first_name || 'User'}!</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-700">Email</h3>
                <p className="text-gray-900">{userData.email || 'No email provided'}</p>
              </div>
              <div>
                <h3 className="font-medium text-gray-700">Account Status</h3>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active
                </span>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Your Programs</h2>
            <button 
              onClick={fetchData}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Refresh
            </button>
          </div>
          
          {programs.length > 0 ? (
            <div className="space-y-4">
              {programs.map((program) => (
                <div key={program.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <h3 className="font-medium text-lg">{program.title || 'Untitled Program'}</h3>
                  {program.description && (
                    <p className="text-gray-600 text-sm mt-1">{program.description}</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">You are not enrolled in any programs yet.</p>
              <button
                onClick={fetchData}
                className="mt-4 text-blue-600 hover:text-blue-800 text-sm"
              >
                Check again
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
