import api from './api';

const addressService = {
  // Get all addresses for current user
  getAddresses: async () => {
    const response = await api.get('/addresses/');
    return response.data;
  },

  // Create a new address
  createAddress: async (addressData) => {
    const response = await api.post('/addresses/', addressData);
    return response.data;
  },

  // Update an address
  updateAddress: async (addressId, addressData) => {
    const response = await api.put(`/addresses/${addressId}`, addressData);
    return response.data;
  },

  // Delete an address
  deleteAddress: async (addressId) => {
    const response = await api.delete(`/addresses/${addressId}`);
    return response.data;
  },

  // Set address as default
  setDefaultAddress: async (addressId) => {
    const response = await api.post(`/addresses/${addressId}/set-default`);
    return response.data;
  },
};

export default addressService;
