/**
 * Weekly Updates API client
 * Isolated module — does NOT modify the existing client.js or other API files.
 */
import apiClient from './client';

export const weeklyUpdatesApi = {
  /**
   * Fetch weekly career updates for a given career path.
   * @param {string} careerPath - e.g. "Data Scientist"
   * @returns {Promise<AxiosResponse>}
   */
  getUpdates: (careerPath = 'Machine Learning Engineer') =>
    apiClient.get('/weekly-updates', {
      params: { career_path: careerPath },
    }),
};
