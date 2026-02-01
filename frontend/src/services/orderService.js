import api from './api';

const orderService = {
  // Create order from cart
  checkout: async (shippingAddressId) => {
    const response = await api.post('/orders/checkout', {
      shipping_address_id: shippingAddressId,
    });
    return response.data;
  },

  // Get all orders for current user
  getOrders: async (page = 1, perPage = 10, status = null) => {
    const params = { page, per_page: perPage };
    if (status) {
      params.status = status;
    }
    const response = await api.get('/orders/', { params });
    return response.data;
  },

  // Get specific order details
  getOrder: async (orderId) => {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },

  // Cancel an order
  cancelOrder: async (orderId) => {
    const response = await api.post(`/orders/${orderId}/cancel`);
    return response.data;
  },

  // Get order statistics
  getOrderStats: async () => {
    const response = await api.get('/orders/stats');
    return response.data;
  },
};

export default orderService;
