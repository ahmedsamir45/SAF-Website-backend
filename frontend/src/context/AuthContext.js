import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../services/api';
import { toast } from 'react-toastify';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const checkAuth = useCallback(async () => {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!accessToken || !refreshToken) {
      setLoading(false);
      return;
    }
    
    try {
      // Verify the token is still valid
      await authApi.verifyToken(accessToken);
      
      // Get the current user data
      const response = await authApi.getCurrentUser();
      setUser({ ...response.data });
    } catch (error) {
      console.error('Session validation failed:', error);
      // If token is invalid, clear the stored tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
    } finally {
      setLoading(false);
    }
  }, [navigate]);
  
  useEffect(() => {
    // Initial auth check
    checkAuth();
    
    // Listen for logout events from other components
    const handleLogout = () => logout();
    window.addEventListener('logout', handleLogout);
    
    return () => {
      window.removeEventListener('logout', handleLogout);
    };
  }, [checkAuth]);

  const login = async (email, password) => {
    try {
      const response = await authApi.login(email, password);
      const { access, refresh } = response.data;
      
      // Store both access and refresh tokens
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      // Fetch user data
      const userResponse = await authApi.getCurrentUser();
      setUser({ ...userResponse.data });
      
      toast.success('Login successful!');
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      const errorMessage = error.response?.data?.detail || 'Login failed. Please check your credentials.';
      toast.error(errorMessage);
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const logout = () => {
    // Remove all auth-related items
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Clear user state
    setUser(null);
    
    // Show logout message
    toast.info('You have been logged out.');
    
    // Redirect to login page
    navigate('/login');
  };

  const value = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
