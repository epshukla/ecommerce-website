import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Paper,
  Chip,
} from '@mui/material';
import { Search as SearchIcon, FilterList as FilterIcon } from '@mui/icons-material';
import ProductCard from '../components/products/ProductCard';
import productService from '../services/productService';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    filterAndSortProducts();
  }, [products, searchQuery, categoryFilter, sortBy]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const data = await productService.getProducts();
      setProducts(data.products || []);

      // Extract unique categories
      const uniqueCategories = [
        ...new Set(data.products.map((p) => p.category).filter(Boolean)),
      ];
      setCategories(uniqueCategories);

      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortProducts = () => {
    let filtered = [...products];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (product) =>
          product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          product.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter((product) => product.category === categoryFilter);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'price-low':
          return parseFloat(a.price) - parseFloat(b.price);
        case 'price-high':
          return parseFloat(b.price) - parseFloat(a.price);
        default:
          return 0;
      }
    });

    setFilteredProducts(filtered);
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleCategoryChange = (e) => {
    setCategoryFilter(e.target.value);
  };

  const handleSortChange = (e) => {
    setSortBy(e.target.value);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading products...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Product Catalog
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Discover our amazing collection of products
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <FilterIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" fontWeight="medium">
            Filters & Search
          </Typography>
        </Box>

        <Grid container spacing={2}>
          {/* Search */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search products..."
              value={searchQuery}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          {/* Category Filter */}
          <Grid item xs={12} sm={6} md={4}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select value={categoryFilter} onChange={handleCategoryChange} label="Category">
                <MenuItem value="all">All Categories</MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Sort By */}
          <Grid item xs={12} sm={6} md={4}>
            <FormControl fullWidth>
              <InputLabel>Sort By</InputLabel>
              <Select value={sortBy} onChange={handleSortChange} label="Sort By">
                <MenuItem value="name">Name (A-Z)</MenuItem>
                <MenuItem value="price-low">Price (Low to High)</MenuItem>
                <MenuItem value="price-high">Price (High to Low)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Active Filters */}
        {(searchQuery || categoryFilter !== 'all') && (
          <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {searchQuery && (
              <Chip
                label={`Search: "${searchQuery}"`}
                onDelete={() => setSearchQuery('')}
                color="primary"
                variant="outlined"
              />
            )}
            {categoryFilter !== 'all' && (
              <Chip
                label={`Category: ${categoryFilter}`}
                onDelete={() => setCategoryFilter('all')}
                color="primary"
                variant="outlined"
              />
            )}
          </Box>
        )}
      </Paper>

      {/* Results Count */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="body1" color="text.secondary">
          Showing {filteredProducts.length} {filteredProducts.length === 1 ? 'product' : 'products'}
        </Typography>
      </Box>

      {/* Products Grid */}
      {filteredProducts.length === 0 ? (
        <Paper elevation={1} sx={{ p: 6, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No products found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Try adjusting your filters or search query
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredProducts.map((product) => (
            <Grid item xs={12} sm={6} md={4} key={product.id}>
              <ProductCard product={product} onAddedToCart={fetchProducts} />
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default Products;
