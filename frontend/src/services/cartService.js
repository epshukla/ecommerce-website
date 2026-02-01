import api from './api';

const cartService = {
  // Get current cart
  getCart: async () => {
    const response = await api.get('/cart/');
    return response.data;
  },

  // Add item to cart
  addToCart: async (productId, quantity = 1) => {
    const response = await api.post('/cart/add', {
      product_id: productId,
      quantity,
    });
    return response.data;
  },

  // Update cart item quantity
  updateCartItem: async (productId, quantity) => {
    const response = await api.put('/cart/update', {
      product_id: productId,
      quantity,
    });
    return response.data;
  },

  // Remove item from cart
  removeFromCart: async (productId) => {
    const response = await api.delete(`/cart/remove/${productId}`);
    return response.data;
  },

  // Clear cart
  clearCart: async () => {
    const response = await api.delete('/cart/clear');
    return response.data;
  },
};

export default cartService;
