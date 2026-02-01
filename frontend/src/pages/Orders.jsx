import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Grid,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  ShoppingBag as ShoppingBagIcon,
  Visibility as VisibilityIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import orderService from '../services/orderService';
import { formatCurrency } from '../utils/currency';

const Orders = () => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [cancellingOrder, setCancellingOrder] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await orderService.getOrders();
      setOrders(data.orders);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (orderId) => {
    try {
      const order = await orderService.getOrder(orderId);
      setSelectedOrder(order);
      setDetailsOpen(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load order details');
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) {
      return;
    }

    try {
      setCancellingOrder(orderId);
      await orderService.cancelOrder(orderId);
      await fetchOrders();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to cancel order');
    } finally {
      setCancellingOrder(null);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      processing: 'info',
      shipped: 'primary',
      delivered: 'success',
      cancelled: 'error',
    };
    return colors[status] || 'default';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (orders.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          sx={{
            textAlign: 'center',
            py: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <ShoppingBagIcon sx={{ fontSize: 80, color: 'text.secondary', opacity: 0.5 }} />
          <Typography variant="h5" color="text.secondary" gutterBottom>
            No orders yet
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Start shopping to see your orders here
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/products')}
            sx={{
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
              },
            }}
          >
            Start Shopping
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        My Orders
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {orders.map((order) => (
          <Grid item xs={12} key={order.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      Order #{order.id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Placed on {formatDate(order.created_at)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column', alignItems: 'flex-end' }}>
                    <Chip label={order.status.toUpperCase()} color={getStatusColor(order.status)} size="small" />
                    <Typography variant="h6" color="primary" fontWeight="bold">
                      {formatCurrency(order.total_amount)}
                    </Typography>
                  </Box>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {order.total_items} {order.total_items === 1 ? 'item' : 'items'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Payment: {order.payment_status}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      startIcon={<VisibilityIcon />}
                      onClick={() => handleViewDetails(order.id)}
                      variant="outlined"
                      size="small"
                    >
                      View Details
                    </Button>
                    {order.status !== 'delivered' && order.status !== 'cancelled' && (
                      <Button
                        startIcon={<CancelIcon />}
                        onClick={() => handleCancelOrder(order.id)}
                        disabled={cancellingOrder === order.id}
                        color="error"
                        variant="outlined"
                        size="small"
                      >
                        {cancellingOrder === order.id ? <CircularProgress size={20} /> : 'Cancel'}
                      </Button>
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Order Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Order Details #{selectedOrder?.id}</DialogTitle>
        <DialogContent>
          {selectedOrder && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Order Date
                  </Typography>
                  <Typography variant="body1">{formatDate(selectedOrder.created_at)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip label={selectedOrder.status.toUpperCase()} color={getStatusColor(selectedOrder.status)} size="small" />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Payment Status
                  </Typography>
                  <Typography variant="body1">{selectedOrder.payment_status}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Amount
                  </Typography>
                  <Typography variant="h6" color="primary" fontWeight="bold">
                    {formatCurrency(selectedOrder.total_amount)}
                  </Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Shipping Address
              </Typography>
              {selectedOrder.shipping_address && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2">{selectedOrder.shipping_address.address_line1}</Typography>
                  {selectedOrder.shipping_address.address_line2 && (
                    <Typography variant="body2">{selectedOrder.shipping_address.address_line2}</Typography>
                  )}
                  <Typography variant="body2">
                    {selectedOrder.shipping_address.city}, {selectedOrder.shipping_address.state}{' '}
                    {selectedOrder.shipping_address.postal_code}
                  </Typography>
                  <Typography variant="body2">{selectedOrder.shipping_address.country}</Typography>
                </Box>
              )}

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Order Items
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Product</TableCell>
                      <TableCell align="right">Price</TableCell>
                      <TableCell align="right">Quantity</TableCell>
                      <TableCell align="right">Subtotal</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {selectedOrder.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.product_name}</TableCell>
                        <TableCell align="right">{formatCurrency(item.price_at_purchase)}</TableCell>
                        <TableCell align="right">{item.quantity}</TableCell>
                        <TableCell align="right">{formatCurrency(item.subtotal)}</TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell colSpan={3} align="right">
                        <Typography variant="h6" fontWeight="bold">
                          Total
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="h6" color="primary" fontWeight="bold">
                          {formatCurrency(selectedOrder.total_amount)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Orders;
