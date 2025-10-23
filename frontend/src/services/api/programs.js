import api from '.';
import { ENDPOINTS } from '../../config';

export const programsApi = {
  // Get all programs with optional filters
  getPrograms: async (params = {}) => {
    const response = await api.get(ENDPOINTS.PROGRAMS.LIST, { params });
    return response.data;
  },

  // Get featured programs
  getFeaturedPrograms: async () => {
    const response = await api.get(ENDPOINTS.PROGRAMS.FEATURED);
    return response.data;
  },

  // Get program by ID
  getProgramById: async (id) => {
    const response = await api.get(ENDPOINTS.PROGRAMS.DETAIL(id));
    return response.data;
  },

  // Get program categories
  getCategories: async () => {
    const response = await api.get(ENDPOINTS.PROGRAMS.CATEGORIES);
    return response.data;
  },

  // Create a new program (admin only)
  createProgram: async (programData) => {
    const response = await api.post(ENDPOINTS.PROGRAMS.LIST, programData);
    return response.data;
  },

  // Update a program (admin only)
  updateProgram: async (id, programData) => {
    const response = await api.patch(ENDPOINTS.PROGRAMS.DETAIL(id), programData);
    return response.data;
  },

  // Delete a program (admin only)
  deleteProgram: async (id) => {
    await api.delete(ENDPOINTS.PROGRAMS.DETAIL(id));
    return true;
  },

  // Apply to a program
  applyToProgram: async (programId, applicationData) => {
    const response = await api.post(`/programs/${programId}/apply/`, applicationData);
    return response.data;
  },

  // Get user's program applications
  getUserApplications: async () => {
    const response = await api.get('/programs/applications/');
    return response.data;
  },

  // Get program statistics (admin only)
  getProgramStatistics: async (programId) => {
    const response = await api.get(`/programs/${programId}/statistics/`);
    return response.data;
  }
};

export default programsApi;
