import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  Box,
  IconButton,
  Chip,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  ShoppingCart as CartIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import cartService from '../../services/cartService';
import { formatCurrency } from '../../utils/currency';
import { getImageUrl } from '../../utils/imageUrl';

const ProductCard = ({ product, onAddedToCart }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isFavorite, setIsFavorite] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleCardClick = (e) => {
    // Don't navigate if clicking on buttons
    if (e.target.closest('button')) {
      return;
    }
    navigate(`/products/${product.id}`);
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    try {
      await cartService.addToCart(product.id, 1);
      setSnackbar({
        open: true,
        message: 'Product added to cart!',
        severity: 'success',
      });
      if (onAddedToCart) {
        onAddedToCart();
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.response?.data?.error || 'Failed to add to cart',
        severity: 'error',
      });
    }
  };

  const handleToggleFavorite = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setIsFavorite(!isFavorite);
    // TODO: Implement wishlist API call
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <>
      <Card
        onClick={handleCardClick}
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          overflow: 'hidden',
          '&:hover': {
            transform: 'translateY(-8px)',
            boxShadow: (theme) => theme.shadows[8],
          },
        }}
      >
        {/* Favorite Button */}
        <IconButton
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            backgroundColor: 'background.paper',
            '&:hover': {
              backgroundColor: 'background.paper',
            },
            zIndex: 1,
          }}
          onClick={handleToggleFavorite}
        >
          {isFavorite ? (
            <FavoriteIcon sx={{ color: 'error.main' }} />
          ) : (
            <FavoriteBorderIcon />
          )}
        </IconButton>

        {/* Stock Badge */}
        {product.stock_quantity === 0 && (
          <Chip
            label="Out of Stock"
            color="error"
            size="small"
            sx={{
              position: 'absolute',
              top: 8,
              left: 8,
              zIndex: 1,
            }}
          />
        )}

        {/* Product Image */}
        <CardMedia
          component="img"
          height="280"
          image={getImageUrl(product.image_url)}
          alt={product.name}
          sx={{
            objectFit: 'cover',
            width: '100%',
          }}
        />

        <CardContent
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            background: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(10px)',
            color: 'white',
            position: 'relative',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.9))',
              zIndex: 0,
            },
            '& > *': {
              position: 'relative',
              zIndex: 1,
            }
          }}
        >
          {/* Category */}
          <Typography variant="caption" sx={{ color: '#B794F4' }} gutterBottom>
            {product.category_name || 'Uncategorized'}
          </Typography>

          {/* Product Name */}
          <Typography
            variant="h6"
            component="h2"
            gutterBottom
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              minHeight: '3.5em',
            }}
          >
            {product.name}
          </Typography>

          {/* Description */}
          <Typography
            variant="body2"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              minHeight: '2.5em',
              mb: 2,
              color: 'rgba(255, 255, 255, 0.7)',
            }}
          >
            {product.description}
          </Typography>

          {/* Price and Add to Cart */}
          <Box sx={{ mt: 'auto' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h5" sx={{ color: '#B794F4' }} fontWeight="bold">
                {formatCurrency(product.price)}
              </Typography>
              {product.stock_quantity > 0 && product.stock_quantity < 10 && (
                <Typography variant="caption" sx={{ color: '#FFA500' }}>
                  Only {product.stock_quantity} left
                </Typography>
              )}
            </Box>

            <Button
              variant="contained"
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
          </Box>
        </CardContent>
      </Card>

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
    </>
  );
};

export default ProductCard;
