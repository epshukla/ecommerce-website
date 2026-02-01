import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Button, CircularProgress, Alert, Grid } from '@mui/material';
import { FavoriteBorder as HeartIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useWishlist } from '../contexts/WishlistContext';
import ProductCard from '../components/products/ProductCard';
import wishlistService from '../services/wishlistService';

const Wishlist = () => {
  const navigate = useNavigate();
  const { refreshWishlist } = useWishlist();
  const [wishlist, setWishlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWishlist();
  }, []);

  const fetchWishlist = async () => {
    try {
      setLoading(true);
      const data = await wishlistService.getWishlist();
      setWishlist(data.wishlist);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load wishlist');
    } finally {
      setLoading(false);
    }
  };

  const handleClearWishlist = async () => {
    if (!window.confirm('Clear all items from wishlist?')) return;
    try {
      await wishlistService.clearWishlist();
      refreshWishlist();
      await fetchWishlist();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to clear wishlist');
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', minHeight: '60vh', alignItems: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (wishlist.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <HeartIcon sx={{ fontSize: 80, color: 'text.secondary', opacity: 0.5 }} />
          <Typography variant="h5" color="text.secondary" gutterBottom sx={{ mt: 2 }}>
            Your wishlist is empty
          </Typography>
          <Button variant="contained" onClick={() => navigate('/products')} sx={{ mt: 2 }}>
            Start Shopping
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">
          My Wishlist
        </Typography>
        <Button variant="outlined" color="error" onClick={handleClearWishlist}>
          Clear All
        </Button>
      </Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      <Grid container spacing={3}>
        {wishlist.map((item) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
            <ProductCard product={item.product} onAddedToCart={fetchWishlist} />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Wishlist;
