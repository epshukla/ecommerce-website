import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Wishlist = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Wishlist
        </Typography>
        <Typography color="text.secondary">
          Wishlist page coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Wishlist;
