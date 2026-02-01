import React, { createContext, useState, useContext, useEffect } from 'react';
import { useAuth } from './AuthContext';
import cartService from '../services/cartService';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [cartCount, setCartCount] = useState(0);

  useEffect(() => {
    if (isAuthenticated) {
      fetchCartCount();
    } else {
      setCartCount(0);
    }
  }, [isAuthenticated]);

  const fetchCartCount = async () => {
    try {
      const data = await cartService.getCart();
      setCartCount(data.total_items || 0);
    } catch (err) {
      console.error('Failed to fetch cart count:', err);
      setCartCount(0);
    }
  };

  const refreshCart = () => {
    if (isAuthenticated) {
      fetchCartCount();
    }
  };

  const value = {
    cartCount,
    refreshCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};
