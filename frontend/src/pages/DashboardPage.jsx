import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config';
import { FaSpinner, FaStar } from 'react-icons/fa';

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

// Program Card Component
const ProgramCard = ({ program, isFavorite, onFavoriteToggle }) => {
  const [favoriteLoading, setFavoriteLoading] = useState(false);

  const handleFavoriteClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      setFavoriteLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) {
        window.location.href = '/login';
        return;
      }

      await fetch(
        `${API_BASE_URL}/programs/${program.id}/${isFavorite ? 'unfavorite' : 'favorite'}/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `JWT ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (onFavoriteToggle) {
        onFavoriteToggle();
      }
    } catch (error) {
      console.error('Error updating favorite status:', error);
    } finally {
      setFavoriteLoading(false);
    }
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200">
      <div className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                <svg className="h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">{program.title}</h3>
                <p className="text-sm text-gray-500">{program.university}</p>
                <p className="text-sm text-gray-500">{program.department}</p>
              </div>
            </div>
          </div>
          <button
            onClick={handleFavoriteClick}
            disabled={favoriteLoading}
            className={`p-2 rounded-full ${isFavorite ? 'text-yellow-400 hover:text-yellow-500' : 'text-gray-400 hover:text-yellow-400'}`}
            title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            {favoriteLoading ? (
              <FaSpinner className="animate-spin" />
            ) : (
              <FaStar className={`h-5 w-5 ${isFavorite ? 'fill-current' : ''}`} />
            )}
          </button>
        </div>
      </div>
      <div className="bg-gray-50 px-5 py-3 flex justify-end">
        <a
          href={`/programs/${program.id}`}
          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          View Details
        </a>
      </div>
    </div>
  );
};

export default function DashboardPage() {
  const [userData, setUserData] = useState(null);
  const [favoritePrograms, setFavoritePrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { logout } = useAuth();
  const navigate = useNavigate();

  // Track in-flight requests to prevent duplicates
  const requestCache = React.useRef(new Map()).current;

  const fetchWithCache = React.useCallback(async (key, fetchFn) => {
    // If a request with the same key is already in progress, return its promise
    if (requestCache.has(key)) {
      return requestCache.get(key);
    }

    const promise = fetchFn();
    requestCache.set(key, promise);

    try {
      const result = await promise;
      return result;
    } finally {
      // Clean up the cache when the request completes
      requestCache.delete(key);
    }
  }, [requestCache]);

  const fetchData = useCallback(async () => {
    // Use a unique key for this request
    const requestKey = 'dashboard-data';
    
    try {
      setLoading(true);
      setError(null);
      
      // Use the cache wrapper to prevent duplicate requests
      const [profileData, programsData] = await fetchWithCache(
        requestKey,
        () => Promise.all([
          apiRequest('/auth/users/me/'),
          apiRequest('/programs/').catch(() => []) // Get all programs
        ])
      );
      
      setUserData(profileData);
      
      // Fetch favorites with the programs data
      try {
        const favoritesData = await fetchWithCache(
          'favorites-ids',
          () => apiRequest('/programs/favorites/ids/')
        );
        
        // Debug: Log raw data
        console.log('=== DEBUG: Favorites Data ===');
        console.log('Raw Favorites Data:', JSON.parse(JSON.stringify(favoritesData)));
        console.log('Raw Programs Data:', JSON.parse(JSON.stringify(programsData)));
        
        let favoritePrograms = [];
        
        // Handle paginated response (programsData.results) or direct array
        const programsList = programsData.results || programsData;
        
        if (Array.isArray(programsList) && Array.isArray(favoritesData)) {
          console.log('=== Processing Favorites ===');
          
          // Extract favorite program IDs with detailed logging
          const favoriteIds = favoritesData.map((fav, index) => {
            const id = fav && typeof fav === 'object' ? fav.program : fav;
            console.log(`Favorite #${index + 1}:`, { raw: fav, extractedId: id, type: typeof id });
            return id;
          }).filter(Boolean);
          
          console.log('Extracted Favorite IDs:', favoriteIds);
          
          // Log all available program IDs for comparison
          console.log('Available Program IDs:', programsList.map(p => ({
            id: p.id,
            title: p.title,
            type: typeof p.id
          })));
          
          // Convert all IDs to strings for consistent comparison
          const favoriteIdsStr = favoriteIds.map(String);
          console.log('Favorite IDs (as strings):', favoriteIdsStr);
          
          // Detailed filtering with logging
          favoritePrograms = programsList.filter(program => {
            const programId = String(program.id);
            const isFavorite = favoriteIdsStr.includes(programId);
            
            console.group(`Program ${programId} (${program.title})`);
            console.log('Program ID (string):', programId);
            console.log('Is in favorites?', isFavorite);
            if (isFavorite) {
              console.log('Matched favorite ID:', programId);
            } else {
              console.log('Available favorite IDs:', favoriteIdsStr);
              console.log('Program ID type:', typeof programId, 'Value:', programId);
              console.log('Sample favorite ID type:', typeof favoriteIdsStr[0], 'Value:', favoriteIdsStr[0]);
            }
            console.groupEnd();
            
            return isFavorite;
          });
          
          console.log('=== Final Favorite Programs ===');
          console.table(favoritePrograms.map(p => ({
            id: p.id,
            title: p.title,
            type: typeof p.id
          })));
        } else {
          console.error('Invalid data format:', {
            isProgramsArray: Array.isArray(programsData),
            isFavoritesArray: Array.isArray(favoritesData),
            programsData: programsData ? 'exists' : 'null/undefined',
            favoritesData: favoritesData ? 'exists' : 'null/undefined'
          });
        }
        
        console.log('Setting favorite programs:', favoritePrograms);
        setFavoritePrograms(favoritePrograms || []);
      } catch (err) {
        console.error('Error fetching favorites:', err);
        setFavoritePrograms([]);
      }
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

  // Handle favorite updates
  const handleFavoriteUpdate = useCallback(async () => {
    try {
      const [programsData, favoritesData] = await Promise.all([
        fetchWithCache('programs', () => apiRequest('/programs/').catch(() => [])),
        fetchWithCache('favorites-ids', () => apiRequest('/programs/favorites/ids/'))
      ]);

      if (Array.isArray(programsData) && Array.isArray(favoritesData)) {
        const updatedFavorites = programsData.filter(program => 
          favoritesData.some(fav => fav.program === program.id)
        );
        setFavoritePrograms(updatedFavorites);
      }
    } catch (error) {
      console.error('Error updating favorites:', error);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Set up event listener for favorite updates
  useEffect(() => {
    window.addEventListener('favoritesUpdated', handleFavoriteUpdate);
    return () => {
      window.removeEventListener('favoritesUpdated', handleFavoriteUpdate);
    };
  }, [handleFavoriteUpdate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Render loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <FaSpinner className="animate-spin h-12 w-12 text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border-l-4 border-red-400 p-4 w-full max-w-2xl">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
              <div className="mt-4">
                <button
                  onClick={fetchData}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <button
            onClick={handleLogout}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* User Profile Section */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <div className="flex items-center">
            <div className="flex-shrink-0 h-12 w-12 rounded-full bg-blue-500 flex items-center justify-center text-white text-xl font-bold">
              {userData?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="ml-4">
              <h2 className="text-lg font-medium text-gray-900">
                {userData?.first_name && userData?.last_name 
                  ? `${userData.first_name} ${userData.last_name}`
                  : userData?.email || 'User'}
              </h2>
              <p className="text-sm text-gray-500">{userData?.email || ''}</p>
              <p className="text-sm text-gray-500 mt-1">
                {favoritePrograms.length} favorite program{favoritePrograms.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        </div>

        {/* Favorites Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">My Favorite Programs</h2>
            {favoritePrograms.length > 0 && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {favoritePrograms.length} program{favoritePrograms.length !== 1 ? 's' : ''}
              </span>
            )}
          </div>
          
          {favoritePrograms.length > 0 ? (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {favoritePrograms.map((program) => (
                <ProgramCard 
                  key={program.id} 
                  program={program} 
                  isFavorite={true}
                  onFavoriteToggle={handleFavoriteUpdate}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No favorites yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Click the star icon on any program to add it to your favorites.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
