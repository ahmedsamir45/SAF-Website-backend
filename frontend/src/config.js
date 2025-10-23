export const API_BASE_URL = 'http://localhost:8000/api';

export const ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/jwt/create/',
    REGISTER: '/auth/users/',
    ME: '/auth/users/me/',
    REFRESH: '/auth/jwt/refresh/',
    VERIFY: '/auth/jwt/verify/',
  },
  PROGRAMS: {
    LIST: '/programs/',
    DETAIL: (id) => `/programs/${id}/`,
  },
  NEWSLETTER: {
    SUBSCRIBE: '/newsletter-subscriptions/',
    CONFIRM: '/newsletter-subscriptions/confirm/',
  },
  CONTACT: '/contact/',
};

export const ROUTES = {
  HOME: '/',
  PROGRAMS: '/programs',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  CONTACT: '/contact',
};

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
};
