import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Products = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Products
        </Typography>
        <Typography color="text.secondary">
          Product catalog coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Products;
