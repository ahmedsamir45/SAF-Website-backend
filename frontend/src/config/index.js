// API Configuration
export const API_BASE_URL = 'http://localhost:8000/api';

// API Endpoints
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
    FEATURED: '/programs/featured/',
    CATEGORIES: '/programs/categories/',
    DETAIL: (id) => `/programs/${id}/`,
  },
  NEWSLETTER: {
    SUBSCRIBE: '/newsletter/subscriptions/',
    CONFIRM: '/newsletter/subscriptions/confirm/',
    STATUS: (email) => `/newsletter/subscriptions/${email}/status/`,
    SUBSCRIPTION: (email) => `/newsletter/subscriptions/${email}/`,
  },
  CONTACT: '/contact/',
};

// Application Routes
export const ROUTES = {
  HOME: '/',
  PROGRAMS: '/programs',
  PROGRAM_DETAIL: (id) => `/programs/${id}`,
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  CONTACT: '/contact',
  NOT_FOUND: '/404',
};

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
};

// Form Validation
export const VALIDATION = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD: {
    MIN_LENGTH: 8,
    REQUIRE_UPPERCASE: true,
    REQUIRE_LOWERCASE: true,
    REQUIRE_NUMBER: true,
    REQUIRE_SPECIAL_CHAR: true,
  },
  PHONE: /^[0-9\-\+]{9,15}$/,
};

// UI Configuration
export const UI = {
  ITEMS_PER_PAGE: 10,
  DATE_FORMAT: 'MMMM D, YYYY',
  DATE_TIME_FORMAT: 'MMMM D, YYYY h:mm A',
};

export default {
  API_BASE_URL,
  ENDPOINTS,
  ROUTES,
  STORAGE_KEYS,
  VALIDATION,
  UI,
};
