"""Test script for order endpoints"""
import requests
import json

BASE_URL = 'http://localhost:5001/api'

def get_auth_token(email, password):
    """Login and get auth token"""
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': email,
        'password': password
    })
    if response.status_code == 200:
        return response.json().get('access_token')
    return None


def setup_cart(token):
    """Add items to cart for testing"""
    print("\n=== Setting Up Cart ===")
    headers = {'Authorization': f'Bearer {token}'}

    # Clear cart first
    requests.delete(f'{BASE_URL}/cart/clear', headers=headers)

    # Add items
    items = [
        {'product_id': 1, 'quantity': 1},  # iPhone
        {'product_id': 5, 'quantity': 2},  # T-Shirt
        {'product_id': 7, 'quantity': 1},  # Book
    ]

    for item in items:
        response = requests.post(f'{BASE_URL}/cart/add', json=item, headers=headers)
        if response.status_code == 200:
            product_id = item['product_id']
            print(f"Added product {product_id} to cart")

    # Get cart summary
    cart_response = requests.get(f'{BASE_URL}/cart/', headers=headers)
    cart = cart_response.json()
    print(f"Cart total: ${cart['subtotal']} ({cart['total_items']} items)")


def test_checkout(token):
    """Test creating an order"""
    print("\n=== Testing Checkout ===")
    headers = {'Authorization': f'Bearer {token}'}

    # Get user's address
    user_response = requests.get(f'{BASE_URL}/auth/me', headers=headers)
    user = user_response.json()['user']

    # For this test, we'll use address ID 1 (from seed data)
    checkout_data = {
        'shipping_address_id': 1
    }

    response = requests.post(f'{BASE_URL}/orders/checkout',
                            json=checkout_data,
                            headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        print(f"Order created: #{data['order']['id']}")
        print(f"Total: ${data['order']['total_amount']}")
        print(f"Status: {data['order']['status']}")
        print(f"Items: {data['order']['total_items']}")
        return data['order']['id']
    else:
        print(f"Error: {response.json()}")
        return None


def test_get_orders(token):
    """Test getting order history"""
    print("\n=== Testing Get Orders ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/orders/', headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Total orders: {data['pagination']['total']}")
        for order in data['orders']:
            print(f"  Order #{order['id']}: ${order['total_amount']} - {order['status']}")
        return data['orders']
    return []


def test_get_order_detail(token, order_id):
    """Test getting specific order details"""
    print(f"\n=== Testing Get Order #{order_id} Details ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/orders/{order_id}', headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        order = response.json()
        print(f"Order #{order['id']}")
        print(f"Status: {order['status']}")
        print(f"Payment: {order['payment_status']}")
        print(f"Total: ${order['total_amount']}")
        print(f"\nItems:")
        for item in order['items']:
            print(f"  - {item['product_name']}: {item['quantity']} x ${item['price_at_purchase']}")


def test_order_stats(token):
    """Test getting order statistics"""
    print("\n=== Testing Order Stats ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/orders/stats', headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        stats = response.json()
        print(f"Total orders: {stats['total_orders']}")
        print(f"Pending: {stats['pending']}")
        print(f"Processing: {stats['processing']}")
        print(f"Shipped: {stats['shipped']}")
        print(f"Delivered: {stats['delivered']}")
        print(f"Cancelled: {stats['cancelled']}")
        print(f"Total spent: ${stats['total_spent']}")


def test_cancel_order(token, order_id):
    """Test cancelling an order"""
    print(f"\n=== Testing Cancel Order #{order_id} ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.post(f'{BASE_URL}/orders/{order_id}/cancel', headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Message: {data['message']}")
        print(f"New status: {data['order']['status']}")
    else:
        print(f"Error: {response.json()}")


def test_update_order_status_admin(admin_token, order_id):
    """Test updating order status as admin"""
    print(f"\n=== Testing Update Order Status (Admin) ===")
    headers = {'Authorization': f'Bearer {admin_token}'}

    response = requests.put(f'{BASE_URL}/orders/{order_id}/status',
                           json={'status': 'processing'},
                           headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Order #{order_id} status updated to: {data['order']['status']}")
    else:
        print(f"Error: {response.json()}")


def test_checkout_empty_cart(token):
    """Test checkout with empty cart"""
    print("\n=== Testing Checkout with Empty Cart ===")
    headers = {'Authorization': f'Bearer {token}'}

    # Clear cart
    requests.delete(f'{BASE_URL}/cart/clear', headers=headers)

    response = requests.post(f'{BASE_URL}/orders/checkout',
                            json={'shipping_address_id': 1},
                            headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Error: {response.json()['error']}")


def test_filter_orders_by_status(token):
    """Test filtering orders by status"""
    print("\n=== Testing Filter Orders by Status ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/orders/',
                           params={'status': 'pending'},
                           headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Pending orders: {data['pagination']['total']}")


if __name__ == '__main__':
    print("Starting Order Tests...")
    print("Make sure the Flask server is running on http://localhost:5001")

    # Get tokens
    user_token = get_auth_token('john.doe@example.com', 'NewPass123')
    admin_token = get_auth_token('admin@example.com', 'admin123')

    if not user_token:
        print("Failed to get user token")
        exit(1)

    # Test order flow
    setup_cart(user_token)
    order_id = test_checkout(user_token)

    if order_id:
        test_get_orders(user_token)
        test_get_order_detail(user_token, order_id)
        test_order_stats(user_token)

        # Test admin functions
        if admin_token:
            test_update_order_status_admin(admin_token, order_id)

        # Create another order and cancel it
        setup_cart(user_token)
        order_id2 = test_checkout(user_token)
        if order_id2:
            test_cancel_order(user_token, order_id2)

        test_order_stats(user_token)
        test_filter_orders_by_status(user_token)

    # Test error cases
    test_checkout_empty_cart(user_token)

    print("\n=== Tests Complete ===")
