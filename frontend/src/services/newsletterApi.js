import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with base URL and default headers
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Request interceptor to add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors
    if (!error.response) {
      console.error('Network Error:', error.message);
      return Promise.reject({ message: 'Network error. Please check your connection.' });
    }
    
    // Handle specific status codes
    const { status, data } = error.response;
    
    if (status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access - redirecting to login');
      // You might want to redirect to login here
    }
    
    return Promise.reject({
      status,
      message: data?.detail || 'An error occurred',
      data,
    });
  }
);

// Newsletter API endpoints
export const newsletterApi = {
  // Subscribe to newsletter
  subscribe: (email) => 
    api.post('/newsletter-subscriptions/', { email }),
  
  // Confirm subscription with code
  confirm: (email, confirmationCode) =>
    api.post('/newsletter-subscriptions/confirm/', { 
      email, 
      confirmation_code: confirmationCode 
    }),
    
  // Get all subscriptions (admin only)
  getAll: () => 
    api.get('/newsletter-subscriptions/'),
    
  // Get a specific subscription
  get: (email) => 
    api.get(`/newsletter-subscriptions/${email}/`),
    
  // Delete a subscription
  delete: (email) => 
    api.delete(`/newsletter-subscriptions/${email}/`),
    
  // Check subscription status
  checkStatus: (email) => 
    api.get(`/newsletter-subscriptions/${email}/status/`)
};

// Auth API endpoints
export const authApi = {
  // Updated to use the correct JWT endpoints
  login: (email, password) => 
    api.post('/auth/token/', { email, password }),
  
  register: (userData) => 
    api.post('/auth/register/', userData),
    
  getCurrentUser: () => 
    api.get('/auth/users/me/'),
    
  refreshToken: (refresh) => 
    api.post('/auth/token/refresh/', { refresh }),
    
  verifyToken: (token) => 
    api.post('/auth/token/verify/', { token })
};

// Export all API functions
export const {
  subscribe: subscribeToNewsletter,
  confirm: confirmSubscription,
  getAll: getSubscriptions,
  get: getSubscription,
  delete: deleteSubscription,
  checkStatus: checkSubscriptionStatus
} = newsletterApi;

export const {
  login,
  register,
  getCurrentUser,
  refreshToken,
  verifyToken
} = authApi;

// Default export for backward compatibility
export default api;
