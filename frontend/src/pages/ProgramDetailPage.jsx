import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { API_BASE_URL } from '../config';
import { FaArrowLeft, FaCalendarAlt, FaLink, FaMoneyBillWave, FaTag, FaUserGraduate, FaBriefcase, FaStar } from 'react-icons/fa';

const ProgramDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [program, setProgram] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);

  // Check favorite status when component mounts
  useEffect(() => {
    const checkFavoriteStatus = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const response = await axios.get(
          `${API_BASE_URL}/programs/${id}/is_favorite/`,
          {
            headers: {
              'Authorization': `JWT ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );
        
        setIsFavorite(response.data.is_favorite);
      } catch (error) {
        console.error('Error checking favorite status:', error);
      }
    };

    if (id) {
      checkFavoriteStatus();
    }
  }, [id]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProgram = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/programs/${id}/`, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
        });
        setProgram(response.data);
      } catch (err) {
        console.error('Error fetching program:', err);
        setError('Failed to load program details');
        toast.error('Failed to load program details');
      } finally {
        setLoading(false);
      }
    };

    fetchProgram();
  }, [id]);

  // Helper function to get CSRF token from cookies
  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error || !program) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-600 mb-4">{error || 'Program not found'}</p>
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-blue-600 hover:text-blue-800 mb-6"
        >
          <FaArrowLeft className="mr-2" /> Back to Programs
        </button>

        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          {/* Header */}
          <div className="px-4 py-5 sm:px-6 bg-gray-50">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{program.title}</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Posted on {new Date(program.post_date).toLocaleDateString()}
                </p>
              </div>
              {program.is_featured && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                  <FaStar className="mr-1" /> Featured
                </span>
              )}
            </div>
          </div>

          {/* Program Image */}
          {program.image && (
            <div className="h-64 sm:h-96 overflow-hidden">
              <img
                src={program.image}
                alt={program.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://via.placeholder.com/800x400?text=No+Image+Available';
                }}
              />
            </div>
          )}

          {/* Program Details */}
          <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Program Details</h3>
                <dl className="space-y-3">
                  <div className="flex items-start">
                    <dt className="w-32 flex-shrink-0 text-sm font-medium text-gray-500 flex items-center">
                      <FaCalendarAlt className="mr-2" /> Duration
                    </dt>
                    <dd className="text-sm text-gray-900">
                      {new Date(program.start_date).toLocaleDateString()} -{' '}
                      {new Date(program.end_date).toLocaleDateString()}
                    </dd>
                  </div>
                  <div className="flex items-start">
                    <dt className="w-32 flex-shrink-0 text-sm font-medium text-gray-500 flex items-center">
                      <FaMoneyBillWave className="mr-2" /> Cost
                    </dt>
                    <dd className="text-sm text-gray-900">${program.cost}</dd>
                  </div>
                  <div className="flex items-start">
                    <dt className="w-32 flex-shrink-0 text-sm font-medium text-gray-500 flex items-center">
                      <FaTag className="mr-2" /> Category
                    </dt>
                    <dd className="text-sm text-gray-900">
                      {program.category}
                    </dd>
                  </div>
                  <div className="flex items-start">
                    <dt className="w-32 flex-shrink-0 text-sm font-medium text-gray-500 flex items-center">
                      <FaUserGraduate className="mr-2" /> Audience
                    </dt>
                    <dd className="text-sm text-gray-900">
                      {program.audience}
                    </dd>
                  </div>
                  <div className="flex items-start">
                    <dt className="w-32 flex-shrink-0 text-sm font-medium text-gray-500 flex items-center">
                      <FaBriefcase className="mr-2" /> Type
                    </dt>
                    <dd className="text-sm text-gray-900">
                      {program.kind}
                    </dd>
                  </div>
                  {program.url && (
                    <div className="flex items-start">
                      <dt className="w-32 flex-shrink-0 text-sm font-medium text-gray-500 flex items-center">
                        <FaLink className="mr-2" /> Website
                      </dt>
                      <dd className="text-sm text-blue-600 hover:underline">
                        <a href={program.url} target="_blank" rel="noopener noreferrer">
                          Visit Website
                        </a>
                      </dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Requirements */}
              {program.requirements && program.requirements.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Requirements</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {program.requirements.map((req, index) => (
                      <li key={index} className="text-sm text-gray-700">
                        {req.description}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Description */}
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Description</h3>
              <div className="prose max-w-none text-gray-700">
                {program.description.split('\n').map((paragraph, i) => (
                  <p key={i} className="mb-4">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
              <a
                href={program.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Apply Now
              </a>
              <button
                onClick={async () => {
                  try {
                    const token = localStorage.getItem('access_token');
                    console.log('Token from localStorage:', token ? 'Found' : 'Not found');
                    
                    if (!token) {
                      toast.error('Please log in to add to favorites');
                      return;
                    }

                    setLoading(true);
                    const url = `${API_BASE_URL}/programs/${program.id}/favorite/`;
                    console.log('Making request to:', url);
                    
                    const response = await axios.post(
                      url,
                      {},
                      {
                        headers: {
                          'Authorization': `JWT ${token}`,
                          'Content-Type': 'application/json',
                        },
                      }
                    );

                    // Toggle favorite status based on response
                    const isFavorited = response.data.status === 'added to favorites';
                    setIsFavorite(isFavorited);
                    toast.success(isFavorited ? 'Added to favorites' : 'Removed from favorites');
                    
                    // Trigger a custom event to notify the dashboard to refresh favorites
                    window.dispatchEvent(new Event('favoritesUpdated'));
                  } catch (error) {
                    console.error('Error updating favorite status:', {
                      message: error.message,
                      response: error.response?.data,
                      status: error.response?.status,
                      statusText: error.response?.statusText,
                      headers: error.response?.headers,
                      config: {
                        url: error.config?.url,
                        method: error.config?.method,
                        headers: error.config?.headers
                      }
                    });
                    toast.error(error.response?.data?.detail || 'Failed to update favorite status');
                  } finally {
                    setLoading(false);
                  }
                }}
                disabled={loading}
                className={`inline-flex items-center justify-center px-6 py-3 border ${
                  isFavorite 
                    ? 'border-yellow-300 bg-yellow-50 text-yellow-700' 
                    : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                } shadow-sm text-base font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
              >
                <FaStar className={`mr-2 ${isFavorite ? 'text-yellow-500' : 'text-yellow-400'}`} /> 
                {loading ? 'Loading...' : (isFavorite ? 'Favorited' : 'Add to Favorites')}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgramDetailPage;
