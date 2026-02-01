import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Divider,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Add as AddIcon, CheckCircle as CheckCircleIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import cartService from '../services/cartService';
import addressService from '../services/addressService';
import orderService from '../services/orderService';
import { formatCurrency } from '../utils/currency';

const Checkout = () => {
  const navigate = useNavigate();
  const { refreshCart } = useCart();
  const [cart, setCart] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState('');
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [showAddressDialog, setShowAddressDialog] = useState(false);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [orderId, setOrderId] = useState(null);

  const [newAddress, setNewAddress] = useState({
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'India',
    is_default: false,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [cartData, addressData] = await Promise.all([
        cartService.getCart(),
        addressService.getAddresses(),
      ]);
      setCart(cartData);
      setAddresses(addressData.addresses);

      const defaultAddr = addressData.addresses.find((addr) => addr.is_default);
      if (defaultAddr) {
        setSelectedAddress(defaultAddr.id.toString());
      } else if (addressData.addresses.length > 0) {
        setSelectedAddress(addressData.addresses[0].id.toString());
      }

      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load checkout data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddressChange = (event) => {
    setSelectedAddress(event.target.value);
  };

  const handleNewAddressChange = (e) => {
    setNewAddress({
      ...newAddress,
      [e.target.name]: e.target.value,
    });
  };

  const handleAddAddress = async () => {
    try {
      await addressService.createAddress(newAddress);
      setShowAddressDialog(false);
      setNewAddress({
        address_line1: '',
        address_line2: '',
        city: '',
        state: '',
        postal_code: '',
        country: 'India',
        is_default: false,
      });
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add address');
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddress) {
      setError('Please select a shipping address');
      return;
    }

    try {
      setProcessing(true);
      const result = await orderService.checkout(parseInt(selectedAddress));
      setOrderId(result.order.id);
      refreshCart();
      setShowSuccessDialog(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to place order');
    } finally {
      setProcessing(false);
    }
  };

  const handleSuccessClose = () => {
    setShowSuccessDialog(false);
    navigate('/orders');
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!cart || !cart.items || cart.items.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="info">
          Your cart is empty. Please add items before checkout.
        </Alert>
        <Button
          variant="contained"
          onClick={() => navigate('/products')}
          sx={{ mt: 2 }}
        >
          Continue Shopping
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Checkout
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Shipping Address */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">
                  Shipping Address
                </Typography>
                <Button
                  startIcon={<AddIcon />}
                  onClick={() => setShowAddressDialog(true)}
                  variant="outlined"
                  size="small"
                >
                  Add New Address
                </Button>
              </Box>

              {addresses.length === 0 ? (
                <Alert severity="warning">
                  No addresses found. Please add a shipping address.
                </Alert>
              ) : (
                <FormControl component="fieldset" fullWidth>
                  <RadioGroup value={selectedAddress} onChange={handleAddressChange}>
                    {addresses.map((address) => (
                      <FormControlLabel
                        key={address.id}
                        value={address.id.toString()}
                        control={<Radio />}
                        label={
                          <Box>
                            <Typography variant="body1" fontWeight="medium">
                              {address.address_line1}
                              {address.is_default && (
                                <Typography component="span" color="primary" sx={{ ml: 1 }}>
                                  (Default)
                                </Typography>
                              )}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {address.address_line2 && `${address.address_line2}, `}
                              {address.city}, {address.state} {address.postal_code}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {address.country}
                            </Typography>
                          </Box>
                        }
                        sx={{
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 1,
                          p: 2,
                          mb: 2,
                          '&:last-child': { mb: 0 },
                        }}
                      />
                    ))}
                  </RadioGroup>
                </FormControl>
              )}

              <Divider sx={{ my: 3 }} />

              {/* Payment Method */}
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Payment Method
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                Payment integration coming soon. Orders will be placed with "Pending" payment status.
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Order Summary */}
        <Grid item xs={12} md={4}>
          <Card sx={{ position: 'sticky', top: 80 }}>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Order Summary
              </Typography>
              <Divider sx={{ my: 2 }} />

              <Box sx={{ mb: 2 }}>
                {cart.items.map((item) => (
                  <Box key={item.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">
                      {item.product.name} x {item.quantity}
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {formatCurrency(item.subtotal)}
                    </Typography>
                  </Box>
                ))}
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">Subtotal</Typography>
                <Typography fontWeight="medium">{formatCurrency(cart.subtotal)}</Typography>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography color="text.secondary">Shipping</Typography>
                <Typography fontWeight="medium">FREE</Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h6" fontWeight="bold">
                  Total
                </Typography>
                <Typography variant="h6" color="primary" fontWeight="bold">
                  {formatCurrency(cart.subtotal)}
                </Typography>
              </Box>

              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={handlePlaceOrder}
                disabled={processing || !selectedAddress || addresses.length === 0}
                sx={{
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                  },
                }}
              >
                {processing ? <CircularProgress size={24} /> : 'Place Order'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add Address Dialog */}
      <Dialog open={showAddressDialog} onClose={() => setShowAddressDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Address</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField
              label="Address Line 1"
              name="address_line1"
              value={newAddress.address_line1}
              onChange={handleNewAddressChange}
              required
              fullWidth
            />
            <TextField
              label="Address Line 2"
              name="address_line2"
              value={newAddress.address_line2}
              onChange={handleNewAddressChange}
              fullWidth
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="City"
                  name="city"
                  value={newAddress.city}
                  onChange={handleNewAddressChange}
                  required
                  fullWidth
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="State"
                  name="state"
                  value={newAddress.state}
                  onChange={handleNewAddressChange}
                  required
                  fullWidth
                />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Postal Code"
                  name="postal_code"
                  value={newAddress.postal_code}
                  onChange={handleNewAddressChange}
                  required
                  fullWidth
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Country"
                  name="country"
                  value={newAddress.country}
                  onChange={handleNewAddressChange}
                  required
                  fullWidth
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAddressDialog(false)}>Cancel</Button>
          <Button onClick={handleAddAddress} variant="contained">
            Add Address
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Dialog */}
      <Dialog open={showSuccessDialog} onClose={handleSuccessClose}>
        <DialogContent sx={{ textAlign: 'center', py: 4 }}>
          <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            Order Placed Successfully!
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Your order #{orderId} has been placed.
          </Typography>
          <Button variant="contained" onClick={handleSuccessClose} fullWidth>
            View Orders
          </Button>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default Checkout;
