import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Cart = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Cart
        </Typography>
        <Typography color="text.secondary">
          Cart page coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Cart;
