import apiClient from './client';

export const profileApi = {
  getProfile: () => apiClient.get('/learners/me'),
  updateProfile: (data) => apiClient.patch('/learners/me', data),
};
