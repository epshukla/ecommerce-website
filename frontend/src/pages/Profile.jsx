import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Card, CardContent, Tabs, Tab, TextField, Button, Alert, Grid, List, ListItem, ListItemText, IconButton, Divider } from '@mui/material';
import { Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import userService from '../services/userService';
import addressService from '../services/addressService';

const Profile = () => {
  const { user } = useAuth();
  const [tab, setTab] = useState(0);
  const [addresses, setAddresses] = useState([]);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [profileData, setProfileData] = useState({ first_name: '', last_name: '', email: '' });
  const [passwordData, setPasswordData] = useState({ old_password: '', new_password: '', confirm_password: '' });
  const [newAddress, setNewAddress] = useState({ address_line1: '', address_line2: '', city: '', state: '', postal_code: '', country: 'India' });

  useEffect(() => {
    if (user) {
      setProfileData({ first_name: user.first_name || '', last_name: user.last_name || '', email: user.email || '' });
    }
    fetchAddresses();
  }, [user]);

  const fetchAddresses = async () => {
    try {
      const data = await addressService.getAddresses();
      setAddresses(data.addresses);
    } catch (err) {
      console.error('Failed to fetch addresses');
    }
  };

  const handleProfileUpdate = async () => {
    try {
      await userService.updateProfile(profileData);
      setMessage({ text: 'Profile updated successfully', type: 'success' });
    } catch (err) {
      setMessage({ text: err.response?.data?.error || 'Update failed', type: 'error' });
    }
  };

  const handlePasswordChange = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ text: 'Passwords do not match', type: 'error' });
      return;
    }
    try {
      await userService.changePassword(passwordData.old_password, passwordData.new_password);
      setMessage({ text: 'Password changed successfully', type: 'success' });
      setPasswordData({ old_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setMessage({ text: err.response?.data?.error || 'Password change failed', type: 'error' });
    }
  };

  const handleAddAddress = async () => {
    try {
      await addressService.createAddress(newAddress);
      setMessage({ text: 'Address added', type: 'success' });
      setNewAddress({ address_line1: '', address_line2: '', city: '', state: '', postal_code: '', country: 'India' });
      fetchAddresses();
    } catch (err) {
      setMessage({ text: 'Failed to add address', type: 'error' });
    }
  };

  const handleDeleteAddress = async (id) => {
    try {
      await addressService.deleteAddress(id);
      fetchAddresses();
    } catch (err) {
      setMessage({ text: 'Failed to delete address', type: 'error' });
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>My Profile</Typography>
      {message.text && <Alert severity={message.type} sx={{ mb: 2 }} onClose={() => setMessage({ text: '', type: '' })}>{message.text}</Alert>}
      <Card>
        <Tabs value={tab} onChange={(e, v) => setTab(v)}>
          <Tab label="Profile Info" />
          <Tab label="Change Password" />
          <Tab label="Addresses" />
        </Tabs>
        <CardContent>
          {tab === 0 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField label="First Name" value={profileData.first_name} onChange={(e) => setProfileData({ ...profileData, first_name: e.target.value })} />
              <TextField label="Last Name" value={profileData.last_name} onChange={(e) => setProfileData({ ...profileData, last_name: e.target.value })} />
              <TextField label="Email" value={profileData.email} onChange={(e) => setProfileData({ ...profileData, email: e.target.value })} />
              <Button variant="contained" onClick={handleProfileUpdate}>Update Profile</Button>
            </Box>
          )}
          {tab === 1 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField type="password" label="Old Password" value={passwordData.old_password} onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })} />
              <TextField type="password" label="New Password" value={passwordData.new_password} onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })} />
              <TextField type="password" label="Confirm Password" value={passwordData.confirm_password} onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })} />
              <Button variant="contained" onClick={handlePasswordChange}>Change Password</Button>
            </Box>
          )}
          {tab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>Saved Addresses</Typography>
              <List>
                {addresses.map((addr) => (
                  <ListItem key={addr.id} secondaryAction={<IconButton onClick={() => handleDeleteAddress(addr.id)}><DeleteIcon /></IconButton>}>
                    <ListItemText primary={`${addr.address_line1}, ${addr.city}`} secondary={`${addr.state} ${addr.postal_code}, ${addr.country}`} />
                  </ListItem>
                ))}
              </List>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom><AddIcon /> Add New Address</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}><TextField fullWidth label="Address Line 1" value={newAddress.address_line1} onChange={(e) => setNewAddress({ ...newAddress, address_line1: e.target.value })} /></Grid>
                <Grid item xs={12}><TextField fullWidth label="Address Line 2" value={newAddress.address_line2} onChange={(e) => setNewAddress({ ...newAddress, address_line2: e.target.value })} /></Grid>
                <Grid item xs={6}><TextField fullWidth label="City" value={newAddress.city} onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })} /></Grid>
                <Grid item xs={6}><TextField fullWidth label="State" value={newAddress.state} onChange={(e) => setNewAddress({ ...newAddress, state: e.target.value })} /></Grid>
                <Grid item xs={6}><TextField fullWidth label="Postal Code" value={newAddress.postal_code} onChange={(e) => setNewAddress({ ...newAddress, postal_code: e.target.value })} /></Grid>
                <Grid item xs={6}><TextField fullWidth label="Country" value={newAddress.country} onChange={(e) => setNewAddress({ ...newAddress, country: e.target.value })} /></Grid>
                <Grid item xs={12}><Button fullWidth variant="contained" onClick={handleAddAddress}>Add Address</Button></Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default Profile;
