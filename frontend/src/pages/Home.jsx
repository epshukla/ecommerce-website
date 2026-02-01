import React from 'react';
import { Container, Typography, Box, Button, Grid, Card, CardContent } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, LocalShipping, CreditCard, Headset } from '@mui/icons-material';

const Home = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <ShoppingBag sx={{ fontSize: 48 }} />,
      title: 'Wide Selection',
      description: 'Browse thousands of products across multiple categories',
    },
    {
      icon: <LocalShipping sx={{ fontSize: 48 }} />,
      title: 'Fast Shipping',
      description: 'Get your orders delivered quickly and reliably',
    },
    {
      icon: <CreditCard sx={{ fontSize: 48 }} />,
      title: 'Secure Payment',
      description: 'Shop with confidence using our secure payment system',
    },
    {
      icon: <Headset sx={{ fontSize: 48 }} />,
      title: '24/7 Support',
      description: 'Our customer service team is always here to help',
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      {/* Hero Section */}
      <Box
        sx={{
          textAlign: 'center',
          mb: 8,
          py: 6,
          borderRadius: 4,
          background: (theme) =>
            `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
          color: 'white',
        }}
      >
        <Typography variant="h2" fontWeight="bold" gutterBottom>
          Welcome to E-Commerce
        </Typography>
        <Typography variant="h5" sx={{ mb: 4, opacity: 0.95 }}>
          Discover amazing products at unbeatable prices
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/products')}
          sx={{
            backgroundColor: 'white',
            color: 'primary.main',
            px: 4,
            py: 1.5,
            fontSize: '1.1rem',
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.9)',
            },
          }}
        >
          Shop Now
        </Button>
      </Box>

      {/* Features Grid */}
      <Grid container spacing={4}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                textAlign: 'center',
                p: 2,
              }}
            >
              <CardContent>
                <Box sx={{ color: 'primary.main', mb: 2 }}>{feature.icon}</Box>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Home;
