import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
  Switch,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Home as HomeIcon,
  ShoppingCart as CartIcon,
  FavoriteBorder as WishlistIcon,
  Receipt as OrdersIcon,
  Person as ProfileIcon,
  Dashboard as DashboardIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Store as StoreIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useThemeMode } from '../../contexts/ThemeContext';

const DRAWER_WIDTH = 280;

const Sidebar = ({ open, onClose, isAdmin = false }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { mode, toggleTheme } = useThemeMode();

  const userMenuItems = [
    { text: 'Home', icon: <HomeIcon />, path: '/' },
    { text: 'Products', icon: <StoreIcon />, path: '/products' },
    { text: 'Cart', icon: <CartIcon />, path: '/cart' },
    { text: 'Wishlist', icon: <WishlistIcon />, path: '/wishlist' },
    { text: 'Orders', icon: <OrdersIcon />, path: '/orders' },
    { text: 'Profile', icon: <ProfileIcon />, path: '/profile' },
  ];

  const adminMenuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/admin/dashboard' },
    { text: 'Products', icon: <StoreIcon />, path: '/admin/products' },
    { text: 'Orders', icon: <OrdersIcon />, path: '/admin/orders' },
    { text: 'Users', icon: <ProfileIcon />, path: '/admin/users' },
  ];

  const menuItems = isAdmin ? adminMenuItems : userMenuItems;

  const handleNavigation = (path) => {
    navigate(path);
    onClose();
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box
        sx={{
          p: 3,
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
          color: 'white',
        }}
      >
        <Typography variant="h5" fontWeight="bold">
          E-Commerce
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
          {isAdmin ? 'Admin Portal' : 'Shop Smart'}
        </Typography>
      </Box>

      {/* Navigation Items */}
      <List sx={{ flexGrow: 1, px: 2, py: 2 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 2,
                  backgroundColor: isActive
                    ? alpha(theme.palette.primary.main, 0.12)
                    : 'transparent',
                  color: isActive ? theme.palette.primary.main : theme.palette.text.primary,
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.08),
                  },
                  transition: 'all 0.2s',
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? theme.palette.primary.main : theme.palette.text.secondary,
                    minWidth: 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isActive ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider />

      {/* Theme Toggle */}
      <Box sx={{ p: 2 }}>
        <ListItemButton
          sx={{
            borderRadius: 2,
            backgroundColor: alpha(theme.palette.primary.main, 0.05),
          }}
        >
          <ListItemIcon sx={{ minWidth: 40 }}>
            {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
          </ListItemIcon>
          <ListItemText
            primary="Dark Mode"
            primaryTypographyProps={{
              fontSize: '0.95rem',
            }}
          />
          <Switch
            edge="end"
            checked={mode === 'dark'}
            onChange={toggleTheme}
            inputProps={{ 'aria-label': 'toggle dark mode' }}
          />
        </ListItemButton>
      </Box>
    </Box>
  );

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          borderRight: 'none',
          boxShadow: theme.shadows[8],
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;
