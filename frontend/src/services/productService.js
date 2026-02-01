import api from './api';

const productService = {
  // Get all products with optional filters
  getProducts: async (params = {}) => {
    const response = await api.get('/products/', { params });
    return response.data;
  },

  // Get single product by ID
  getProductById: async (id) => {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },

  // Search products
  searchProducts: async (query) => {
    const response = await api.get('/products/search', { params: { q: query } });
    return response.data;
  },

  // Get products by category
  getProductsByCategory: async (category) => {
    const response = await api.get('/products/', { params: { category } });
    return response.data;
  },
};

export default productService;
