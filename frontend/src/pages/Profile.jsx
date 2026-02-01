import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Profile = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Profile
        </Typography>
        <Typography color="text.secondary">
          Profile page coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Profile;
