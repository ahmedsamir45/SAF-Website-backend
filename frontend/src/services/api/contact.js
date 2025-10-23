import api from '.';
import { ENDPOINTS } from '../../config';

export const contactApi = {
  // Send a contact message
  sendMessage: async (messageData) => {
    const response = await api.post(ENDPOINTS.CONTACT, messageData);
    return response.data;
  },

  // Get all messages (admin only)
  getMessages: async (params = {}) => {
    const response = await api.get(ENDPOINTS.CONTACT, { params });
    return response.data;
  },

  // Get message by ID (admin only)
  getMessage: async (id) => {
    const response = await api.get(`${ENDPOINTS.CONTACT}${id}/`);
    return response.data;
  },

  // Update message status (admin only)
  updateMessageStatus: async (id, status) => {
    const response = await api.patch(`${ENDPOINTS.CONTACT}${id}/`, { status });
    return response.data;
  },

  // Delete a message (admin only)
  deleteMessage: async (id) => {
    await api.delete(`${ENDPOINTS.CONTACT}${id}/`);
    return true;
  },

  // Get message statistics (admin only)
  getMessageStats: async () => {
    const response = await api.get('/contact/statistics/');
    return response.data;
  }
};

export default contactApi;
