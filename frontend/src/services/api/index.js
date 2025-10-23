import axios from 'axios';
import { toast } from 'react-toastify';
import { API_BASE_URL } from '../../config';

export * from './auth';
export * from './programs';
export * from './newsletter';
export * from './contact';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 seconds
  withCredentials: true,
});

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
export const setupResponseInterceptors = (onUnauthenticated) => {
  api.interceptors.response.use(
    (response) => {
      // Handle successful responses
      return response;
    },
    async (error) => {
      const originalRequest = error.config;
      
      // Handle network errors
      if (!error.response) {
        toast.error('Network error. Please check your connection.');
        return Promise.reject(error);
      }

      const { status, data } = error.response;

      // Handle token refresh on 401 errors
      if (status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          const refreshToken = localStorage.getItem('refresh_token');
          if (!refreshToken) {
            onUnauthenticated?.();
            return Promise.reject(error);
          }
          
          const response = await axios.post(`${API_BASE_URL}/auth/jwt/refresh/`, {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          
          return api(originalRequest);
        } catch (error) {
          onUnauthenticated?.();
          return Promise.reject(error);
        }
      }

      // Handle specific error statuses
      if (status >= 500) {
        toast.error('Server error. Please try again later.');
      } else if (status === 404) {
        toast.error('The requested resource was not found.');
      } else if (data?.detail) {
        toast.error(data.detail);
      } else if (typeof data === 'object') {
        // Handle form validation errors
        const errorMessages = Object.values(data)
          .flat()
          .filter(Boolean)
          .join('\n');
        if (errorMessages) {
          toast.error(errorMessages);
        }
      }
      
      return Promise.reject(error);
    }
  );
};

export default api;
