import React, { createContext, useState, useContext, useEffect } from 'react';
import { useAuth } from './AuthContext';
import wishlistService from '../services/wishlistService';

const WishlistContext = createContext();

export const useWishlist = () => {
  const context = useContext(WishlistContext);
  if (!context) {
    throw new Error('useWishlist must be used within a WishlistProvider');
  }
  return context;
};

export const WishlistProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [wishlistItems, setWishlistItems] = useState([]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchWishlist();
    } else {
      setWishlistItems([]);
    }
  }, [isAuthenticated]);

  const fetchWishlist = async () => {
    try {
      const data = await wishlistService.getWishlist();
      setWishlistItems(data.wishlist || []);
    } catch (err) {
      console.error('Failed to fetch wishlist:', err);
      setWishlistItems([]);
    }
  };

  const isInWishlist = (productId) => {
    return wishlistItems.some((item) => item.product_id === productId);
  };

  const value = {
    wishlistItems,
    isInWishlist,
    refreshWishlist: fetchWishlist,
  };

  return <WishlistContext.Provider value={value}>{children}</WishlistContext.Provider>;
};
