import api from '.';
import { ENDPOINTS } from '../../config';

export const authApi = {
  login: async (email, password) => {
    const response = await api.post(ENDPOINTS.AUTH.LOGIN, { email, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post(ENDPOINTS.AUTH.REGISTER, userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get(ENDPOINTS.AUTH.ME);
    return response.data;
  },

  refreshToken: async (refresh) => {
    const response = await api.post(ENDPOINTS.AUTH.REFRESH, { refresh });
    return response.data;
  },

  verifyToken: async (token) => {
    const response = await api.post(ENDPOINTS.AUTH.VERIFY, { token });
    return response.data;
  },

  updateProfile: async (userData) => {
    const response = await api.patch(ENDPOINTS.AUTH.ME, userData);
    return response.data;
  },

  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/auth/users/set_password/', {
      current_password: currentPassword,
      new_password: newPassword,
      re_new_password: newPassword
    });
    return response.data;
  },

  requestPasswordReset: async (email) => {
    const response = await api.post('/auth/users/reset_password/', { email });
    return response.data;
  },

  confirmPasswordReset: async (uid, token, newPassword) => {
    const response = await api.post('/auth/users/reset_password_confirm/', {
      uid,
      token,
      new_password: newPassword,
      re_new_password: newPassword
    });
    return response.data;
  }
};

export default authApi;
