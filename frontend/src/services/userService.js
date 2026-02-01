import api from './api';

const userService = {
  getProfile: async () => {
    const response = await api.get('/users/profile');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/users/profile', profileData);
    return response.data;
  },

  changePassword: async (oldPassword, newPassword) => {
    const response = await api.put('/users/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

export default userService;
