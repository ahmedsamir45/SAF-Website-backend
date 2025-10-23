import axios from 'axios';
import { toast } from 'react-toastify';

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
    const token = localStorage.getItem('access_token');
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
  async (error) => {
    const originalRequest = error.config;
    
    // Handle network errors
    if (!error.response) {
      toast.error('Network error. Please check your connection.');
      return Promise.reject({ message: 'Network error. Please check your connection.' });
    }
    
    const { status, data } = error.response;
    
    // Handle token refresh on 401 errors
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          // No refresh token, force logout
          window.dispatchEvent(new Event('logout'));
          return Promise.reject(error);
        }
        
        const response = await axios.post(`${API_BASE_URL}/auth/jwt/refresh/`, {
          refresh: refreshToken
        });
        
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        
        // Retry the original request
        return api(originalRequest);
      } catch (error) {
        // Refresh token failed, force logout
        window.dispatchEvent(new Event('logout'));
        return Promise.reject(error);
      }
    }
    
    // Handle specific error statuses
    if (status === 403) {
      toast.error('You do not have permission to perform this action.');
    } else if (status === 404) {
      toast.error('The requested resource was not found.');
    } else if (status >= 500) {
      toast.error('A server error occurred. Please try again later.');
    } else if (data?.detail) {
      toast.error(data.detail);
    } else if (data) {
      // Handle form validation errors
      const errorMessages = Object.values(data).flat().join('\n');
      toast.error(errorMessages || 'An error occurred');
    }
    
    return Promise.reject({
      status,
      message: data?.detail || 'An error occurred',
      data,
    });
  }
);

// Auth API
export const authApi = {
  login: (email, password) => 
    api.post('/auth/jwt/create/', { email, password }),
    
  register: (userData) => 
    api.post('/auth/users/', userData),
    
  getCurrentUser: () => 
    api.get('/auth/users/me/'),
    
  refreshToken: (refresh) => 
    api.post('/auth/jwt/refresh/', { refresh }),
    
  verifyToken: (token) =>
    api.post('/auth/jwt/verify/', { token })
};

// Newsletter API
export const newsletterApi = {
  subscribe: (email) => 
    api.post('/newsletter/subscriptions/', { email }),
    
  confirm: (email, confirmationCode) =>
    api.post('/newsletter/subscriptions/confirm/', { 
      email, 
      confirmation_code: confirmationCode 
    }),
    
  getAll: () => 
    api.get('/newsletter/subscriptions/'),
    
  get: (email) => 
    api.get(`/newsletter/subscriptions/${email}/`),
    
  delete: (email) => 
    api.delete(`/newsletter/subscriptions/${email}/`),
    
  checkStatus: (email) => 
    api.get(`/newsletter/subscriptions/${email}/status/`)
};

// Programs API
export const programsApi = {
  getAll: (params = {}) => 
    api.get('/programs/', { params }),
    
  get: (id) => 
    api.get(`/programs/${id}/`),
    
  create: (data) => 
    api.post('/programs/', data),
    
  update: (id, data) => 
    api.put(`/programs/${id}/`, data),
    
  delete: (id) => 
    api.delete(`/programs/${id}/`),
    
  getCategories: () => 
    api.get('/programs/categories/')
};

export default api;
