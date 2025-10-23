import api from '.';
import { ENDPOINTS } from '../../config';

export const newsletterApi = {
  // Subscribe to newsletter
  subscribe: async (email) => {
    const response = await api.post(ENDPOINTS.NEWSLETTER.SUBSCRIBE, { email });
    return response.data;
  },

  // Confirm subscription with code
  confirm: async (email, confirmationCode) => {
    const response = await api.post(ENDPOINTS.NEWSLETTER.SUBSCRIPTION(email), {
      confirmation_code: confirmationCode
    });
    return response.data;
  },

  // Get all subscriptions (admin only)
  getAllSubscriptions: async () => {
    const response = await api.get(ENDPOINTS.NEWSLETTER.SUBSCRIBE);
    return response.data;
  },

  // Get subscription status
  getSubscriptionStatus: async (email) => {
    const response = await api.get(ENDPOINTS.NEWSLETTER.STATUS(email));
    return response.data;
  },

  // Unsubscribe from newsletter
  unsubscribe: async (email) => {
    await api.delete(ENDPOINTS.NEWSLETTER.SUBSCRIPTION(email));
    return true;
  },

  // Update subscription preferences
  updateSubscription: async (email, preferences) => {
    const response = await api.patch(ENDPOINTS.NEWSLETTER.SUBSCRIPTION(email), {
      preferences
    });
    return response.data;
  },

  // Send newsletter (admin only)
  sendNewsletter: async (newsletterData) => {
    const response = await api.post('/newsletter/send/', newsletterData);
    return response.data;
  },

  // Get newsletter statistics (admin only)
  getNewsletterStats: async () => {
    const response = await api.get('/newsletter/statistics/');
    return response.data;
  }
};

export default newsletterApi;
