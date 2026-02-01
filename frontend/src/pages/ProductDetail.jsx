import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardMedia,
  Typography,
  Button,
  Box,
  Chip,
  IconButton,
  Snackbar,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  ShoppingCart as CartIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import { useWishlist } from '../contexts/WishlistContext';
import cartService from '../services/cartService';
import wishlistService from '../services/wishlistService';
import { formatCurrency } from '../utils/currency';
import { getImageUrl } from '../utils/imageUrl';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { refreshCart } = useCart();
  const { isInWishlist, refreshWishlist } = useWishlist();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';
        const response = await fetch(`${API_BASE_URL}/products/${id}`);
        if (!response.ok) {
          throw new Error('Product not found');
        }
        const data = await response.json();
        setProduct(data);
      } catch (error) {
        setSnackbar({
          open: true,
          message: error.message || 'Failed to load product',
          severity: 'error',
        });
        setTimeout(() => navigate('/products'), 2000);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id, navigate]);

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    try {
      await cartService.addToCart(product.id, quantity);
      refreshCart();
      setSnackbar({
        open: true,
        message: `Added ${quantity} ${quantity > 1 ? 'items' : 'item'} to cart!`,
        severity: 'success',
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.response?.data?.error || 'Failed to add to cart',
        severity: 'error',
      });
    }
  };

  const handleToggleFavorite = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    try {
      if (isInWishlist(product.id)) {
        await wishlistService.removeFromWishlist(product.id);
        setSnackbar({
          open: true,
          message: 'Removed from wishlist',
          severity: 'info',
        });
      } else {
        await wishlistService.addToWishlist(product.id);
        setSnackbar({
          open: true,
          message: 'Added to wishlist!',
          severity: 'success',
        });
      }
      refreshWishlist();
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.response?.data?.error || 'Failed to update wishlist',
        severity: 'error',
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!product) {
    return null;
  }

  return (
    <Container sx={{ py: 4 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/products')}
        sx={{ mb: 3 }}
      >
        Back to Products
      </Button>

      <Grid container spacing={4}>
        {/* Product Image */}
        <Grid item xs={12} md={6}>
          <Card sx={{ position: 'relative' }}>
            {product.stock_quantity === 0 && (
              <Chip
                label="Out of Stock"
                color="error"
                sx={{
                  position: 'absolute',
                  top: 16,
                  left: 16,
                  zIndex: 1,
                }}
              />
            )}
            <CardMedia
              component="img"
              image={getImageUrl(product.image_url)}
              alt={product.name}
              sx={{
                width: '100%',
                height: 'auto',
                maxHeight: '600px',
                objectFit: 'contain',
              }}
            />
          </Card>
        </Grid>

        {/* Product Details */}
        <Grid item xs={12} md={6}>
          <Box>
            {/* Category */}
            <Chip
              label={product.category_name || 'Uncategorized'}
              color="primary"
              size="small"
              sx={{ mb: 2 }}
            />

            {/* Product Name */}
            <Typography variant="h3" component="h1" gutterBottom>
              {product.name}
            </Typography>

            {/* Price */}
            <Typography variant="h4" color="primary" fontWeight="bold" sx={{ mb: 3 }}>
              {formatCurrency(product.price)}
            </Typography>

            <Divider sx={{ my: 3 }} />

            {/* Description */}
            <Typography variant="h6" gutterBottom>
              Description
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              {product.description}
            </Typography>

            <Divider sx={{ my: 3 }} />

            {/* Stock Info */}
            <Box sx={{ mb: 3 }}>
              {product.stock_quantity > 0 ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip label="In Stock" color="success" />
                  {product.stock_quantity < 10 && (
                    <Typography variant="body2" color="warning.main">
                      Only {product.stock_quantity} left in stock
                    </Typography>
                  )}
                </Box>
              ) : (
                <Chip label="Out of Stock" color="error" />
              )}
            </Box>

            {/* Quantity Selector */}
            {product.stock_quantity > 0 && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Typography variant="body1">Quantity:</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    disabled={quantity <= 1}
                  >
                    -
                  </Button>
                  <Typography variant="body1" sx={{ minWidth: '40px', textAlign: 'center' }}>
                    {quantity}
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
                    disabled={quantity >= product.stock_quantity}
                  >
                    +
                  </Button>
                </Box>
              </Box>
            )}

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={<CartIcon />}
                onClick={handleAddToCart}
                disabled={product.stock_quantity === 0}
                sx={{
                  background: product.stock_quantity === 0
                    ? undefined
                    : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  '&:hover': {
                    background: product.stock_quantity === 0
                      ? undefined
                      : 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                  },
                }}
              >
                {product.stock_quantity === 0 ? 'Out of Stock' : 'Add to Cart'}
              </Button>

              <IconButton
                onClick={handleToggleFavorite}
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                {isInWishlist(product.id) ? (
                  <FavoriteIcon sx={{ color: 'error.main' }} />
                ) : (
                  <FavoriteBorderIcon />
                )}
              </IconButton>
            </Box>
          </Box>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default ProductDetail;
