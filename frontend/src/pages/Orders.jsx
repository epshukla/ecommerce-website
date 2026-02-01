import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Orders = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Orders
        </Typography>
        <Typography color="text.secondary">
          Orders page coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Orders;
