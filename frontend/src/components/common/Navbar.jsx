import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  Box,
  Button,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Menu as MenuIcon,
  ShoppingCart as CartIcon,
  FavoriteBorder as WishlistIcon,
  Person as PersonIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Sidebar from './Sidebar';

const Navbar = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      <AppBar position="sticky" elevation={0}>
        <Toolbar sx={{ gap: 2 }}>
          {/* Menu Icon */}
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={() => setSidebarOpen(true)}
          >
            <MenuIcon />
          </IconButton>

          {/* Logo/Brand */}
          <Typography
            variant="h6"
            component="div"
            sx={{
              flexGrow: 1,
              fontWeight: 700,
              cursor: 'pointer',
              userSelect: 'none',
            }}
            onClick={() => navigate('/')}
          >
            E-Commerce
          </Typography>

          {/* Search Icon (placeholder for future search) */}
          <IconButton color="inherit" onClick={() => navigate('/products')}>
            <SearchIcon />
          </IconButton>

          {isAuthenticated ? (
            <>
              {/* Wishlist */}
              <IconButton color="inherit" onClick={() => navigate('/wishlist')}>
                <Badge badgeContent={0} color="secondary">
                  <WishlistIcon />
                </Badge>
              </IconButton>

              {/* Cart */}
              <IconButton color="inherit" onClick={() => navigate('/cart')}>
                <Badge badgeContent={0} color="secondary">
                  <CartIcon />
                </Badge>
              </IconButton>

              {/* Profile/Logout */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <IconButton color="inherit" onClick={() => navigate('/profile')}>
                  <PersonIcon />
                </IconButton>
                {user && (
                  <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
                    {user.first_name}
                  </Typography>
                )}
                <Button
                  color="inherit"
                  onClick={handleLogout}
                  sx={{
                    display: { xs: 'none', md: 'inline-flex' },
                    backgroundColor: alpha(theme.palette.common.white, 0.1),
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.common.white, 0.2),
                    },
                  }}
                >
                  Logout
                </Button>
              </Box>
            </>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                color="inherit"
                onClick={() => navigate('/login')}
                sx={{
                  backgroundColor: alpha(theme.palette.common.white, 0.1),
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.common.white, 0.2),
                  },
                }}
              >
                Login
              </Button>
              <Button
                variant="contained"
                onClick={() => navigate('/register')}
                sx={{
                  background: `${theme.palette.common.white} !important`,
                  color: '#6366f1 !important',
                  fontWeight: 'bold',
                  '&:hover': {
                    background: `${alpha(theme.palette.common.white, 0.95)} !important`,
                    color: '#4f46e5 !important',
                  },
                }}
              >
                Sign Up
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        isAdmin={isAdmin()}
      />
    </>
  );
};

export default Navbar;
