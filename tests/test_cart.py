"""Test script for cart endpoints"""
import requests
import json

BASE_URL = 'http://localhost:5001/api'

def get_auth_token():
    """Login and get auth token"""
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'john.doe@example.com',
        'password': 'NewPass123'
    })
    if response.status_code == 200:
        return response.json().get('access_token')
    return None


def test_get_empty_cart(token):
    """Test getting empty cart"""
    print("\n=== Testing Get Empty Cart ===")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/cart/', headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Cart items: {data['total_items']}")
    print(f"Subtotal: ${data['subtotal']}")


def test_add_to_cart(token):
    """Test adding items to cart"""
    print("\n=== Testing Add to Cart ===")
    headers = {'Authorization': f'Bearer {token}'}

    # Add first item
    print("\nAdding iPhone to cart...")
    response = requests.post(f'{BASE_URL}/cart/add',
                            json={'product_id': 1, 'quantity': 1},
                            headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Items in cart: {data['cart']['total_items']}")
        print(f"Subtotal: ${data['cart']['subtotal']}")

    # Add second item
    print("\nAdding MacBook to cart...")
    response = requests.post(f'{BASE_URL}/cart/add',
                            json={'product_id': 3, 'quantity': 2},
                            headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Items in cart: {data['cart']['total_items']}")
        print(f"Subtotal: ${data['cart']['subtotal']}")

    # Add third item
    print("\nAdding T-Shirt to cart...")
    response = requests.post(f'{BASE_URL}/cart/add',
                            json={'product_id': 5, 'quantity': 3},
                            headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Items in cart: {data['cart']['total_items']}")
        print(f"Subtotal: ${data['cart']['subtotal']}")


def test_add_duplicate_item(token):
    """Test adding same item again (should update quantity)"""
    print("\n=== Testing Add Duplicate Item ===")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{BASE_URL}/cart/add',
                            json={'product_id': 1, 'quantity': 1},
                            headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Items in cart: {data['cart']['total_items']}")
        for item in data['cart']['items']:
            if item['product_id'] == 1:
                print(f"iPhone quantity updated to: {item['quantity']}")


def test_get_cart(token):
    """Test getting cart details"""
    print("\n=== Testing Get Cart ===")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/cart/', headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"\nCart Summary:")
    print(f"Total items: {data['total_items']}")
    print(f"Subtotal: ${data['subtotal']}")
    print(f"\nCart Items:")
    for item in data['items']:
        product = item['product']
        print(f"  - {product['name']}: {item['quantity']} x ${product['price']} = ${item['subtotal']}")


def test_update_cart_item(token):
    """Test updating cart item quantity"""
    print("\n=== Testing Update Cart Item ===")
    headers = {'Authorization': f'Bearer {token}'}

    # First get cart to find an item ID
    cart_response = requests.get(f'{BASE_URL}/cart/', headers=headers)
    cart = cart_response.json()

    if cart['items']:
        item_id = cart['items'][0]['id']
        product_name = cart['items'][0]['product']['name']
        old_quantity = cart['items'][0]['quantity']

        print(f"Updating {product_name} quantity from {old_quantity} to 5...")
        response = requests.put(f'{BASE_URL}/cart/update/{item_id}',
                               json={'quantity': 5},
                               headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"New subtotal: ${data['cart']['subtotal']}")


def test_cart_count(token):
    """Test getting cart count"""
    print("\n=== Testing Cart Count ===")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/cart/count', headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total items in cart: {data['count']}")
    print(f"Subtotal: ${data['subtotal']}")


def test_remove_from_cart(token):
    """Test removing item from cart"""
    print("\n=== Testing Remove from Cart ===")
    headers = {'Authorization': f'Bearer {token}'}

    # Get cart to find an item ID
    cart_response = requests.get(f'{BASE_URL}/cart/', headers=headers)
    cart = cart_response.json()

    if cart['items']:
        item_id = cart['items'][0]['id']
        product_name = cart['items'][0]['product']['name']

        print(f"Removing {product_name} from cart...")
        response = requests.delete(f'{BASE_URL}/cart/remove/{item_id}', headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Items remaining: {data['cart']['total_items']}")
            print(f"New subtotal: ${data['cart']['subtotal']}")


def test_insufficient_stock(token):
    """Test adding more items than available in stock"""
    print("\n=== Testing Insufficient Stock ===")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{BASE_URL}/cart/add',
                            json={'product_id': 1, 'quantity': 1000},
                            headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Error: {data.get('error')}")
    if 'available' in data:
        print(f"Available stock: {data['available']}")


def test_clear_cart(token):
    """Test clearing cart"""
    print("\n=== Testing Clear Cart ===")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(f'{BASE_URL}/cart/clear', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Message: {data['message']}")
        print(f"Items in cart: {data['cart']['total_items']}")


if __name__ == '__main__':
    print("Starting Cart Tests...")
    print("Make sure the Flask server is running on http://localhost:5001")

    token = get_auth_token()
    if not token:
        print("Failed to get auth token")
        exit(1)

    # Clear cart first to start fresh
    headers = {'Authorization': f'Bearer {token}'}
    requests.delete(f'{BASE_URL}/cart/clear', headers=headers)

    # Run tests
    test_get_empty_cart(token)
    test_add_to_cart(token)
    test_add_duplicate_item(token)
    test_get_cart(token)
    test_cart_count(token)
    test_update_cart_item(token)
    test_get_cart(token)
    test_remove_from_cart(token)
    test_insufficient_stock(token)
    test_clear_cart(token)

    print("\n=== Tests Complete ===")
