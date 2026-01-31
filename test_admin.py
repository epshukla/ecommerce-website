"""Test script for admin endpoints"""
import requests
import json

BASE_URL = 'http://localhost:5001/api'

def get_admin_token():
    """Login as admin and get token"""
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    if response.status_code == 200:
        return response.json().get('access_token')
    return None


def test_dashboard_stats(token):
    """Test getting dashboard statistics"""
    print("\n=== Testing Dashboard Stats ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/admin/dashboard/stats', headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        stats = response.json()
        print(f"\nOverview:")
        print(f"  Total Users: {stats['overview']['total_users']}")
        print(f"  Total Products: {stats['overview']['total_products']}")
        print(f"  Total Orders: {stats['overview']['total_orders']}")
        print(f"  Total Revenue: ${stats['overview']['total_revenue']}")

        print(f"\nOrders:")
        print(f"  Pending: {stats['orders']['pending']}")
        print(f"  Processing: {stats['orders']['processing']}")
        print(f"  Shipped: {stats['orders']['shipped']}")
        print(f"  Delivered: {stats['orders']['delivered']}")

        print(f"\nTop Products:")
        for p in stats['top_products']:
            print(f"  - {p['name']}: {p['sold']} sold")


def test_create_product(token):
    """Test creating a new product"""
    print("\n=== Testing Create Product ===")
    headers = {'Authorization': f'Bearer {token}'}

    product_data = {
        'name': 'Test Product - Admin Created',
        'description': 'This is a test product created by admin',
        'price': 99.99,
        'category_id': 1,
        'stock_quantity': 50,
        'image_url': '/static/uploads/test-product.jpg'
    }

    response = requests.post(f'{BASE_URL}/admin/products',
                            json=product_data,
                            headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        print(f"Product created: {data['product']['name']} (ID: {data['product']['id']})")
        return data['product']['id']
    return None


def test_update_product(token, product_id):
    """Test updating a product"""
    print(f"\n=== Testing Update Product #{product_id} ===")
    headers = {'Authorization': f'Bearer {token}'}

    update_data = {
        'price': 79.99,
        'stock_quantity': 100
    }

    response = requests.put(f'{BASE_URL}/admin/products/{product_id}',
                           json=update_data,
                           headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Updated: {data['product']['name']} - ${data['product']['price']}")


def test_get_low_stock(token):
    """Test getting low stock products"""
    print("\n=== Testing Get Low Stock Products ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/admin/products/low-stock',
                           params={'threshold': 30},
                           headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Low stock products: {data['count']}")
        for p in data['products'][:5]:
            print(f"  - {p['name']}: {p['stock_quantity']} remaining")


def test_create_category(token):
    """Test creating a category"""
    print("\n=== Testing Create Category ===")
    headers = {'Authorization': f'Bearer {token}'}

    category_data = {
        'name': 'Test Category',
        'description': 'Category created by admin test'
    }

    response = requests.post(f'{BASE_URL}/admin/categories',
                            json=category_data,
                            headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        print(f"Category created: {data['category']['name']} (ID: {data['category']['id']})")
        return data['category']['id']
    return None


def test_update_category(token, category_id):
    """Test updating a category"""
    print(f"\n=== Testing Update Category #{category_id} ===")
    headers = {'Authorization': f'Bearer {token}'}

    update_data = {
        'description': 'Updated description for test category'
    }

    response = requests.put(f'{BASE_URL}/admin/categories/{category_id}',
                           json=update_data,
                           headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("Category updated successfully")


def test_get_all_orders(token):
    """Test getting all orders"""
    print("\n=== Testing Get All Orders ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/admin/orders', headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Total orders: {data['pagination']['total']}")
        for order in data['orders'][:5]:
            print(f"  Order #{order['id']}: ${order['total_amount']} - {order['status']}")


def test_get_all_users(token):
    """Test getting all users"""
    print("\n=== Testing Get All Users ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/admin/users', headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Total users: {data['pagination']['total']}")
        for user in data['users']:
            print(f"  {user['email']} - {user['role']}")
        return data['users']
    return []


def test_get_user_details(token, user_id):
    """Test getting user details"""
    print(f"\n=== Testing Get User #{user_id} Details ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/admin/users/{user_id}', headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        user = response.json()
        print(f"User: {user['email']}")
        print(f"  Total Orders: {user['stats']['total_orders']}")
        print(f"  Total Spent: ${user['stats']['total_spent']}")


def test_get_all_reviews(token):
    """Test getting all reviews"""
    print("\n=== Testing Get All Reviews ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/admin/reviews', headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Total reviews: {data['pagination']['total']}")
        for review in data['reviews'][:5]:
            print(f"  {review['user_name']}: {review['rating']} stars - {review['comment'][:50]}...")


def test_delete_product(token, product_id):
    """Test deleting a product"""
    print(f"\n=== Testing Delete Product #{product_id} ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.delete(f'{BASE_URL}/admin/products/{product_id}',
                              headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("Product deleted successfully")


def test_unauthorized_access():
    """Test that non-admin users cannot access admin endpoints"""
    print("\n=== Testing Unauthorized Access ===")

    # Try to access admin endpoint without token
    response = requests.get(f'{BASE_URL}/admin/dashboard/stats')
    print(f"No token - Status: {response.status_code}")

    # Try with regular user token
    user_resp = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'john.doe@example.com',
        'password': 'NewPass123'
    })
    if user_resp.status_code == 200:
        user_token = user_resp.json()['access_token']
        headers = {'Authorization': f'Bearer {user_token}'}
        response = requests.get(f'{BASE_URL}/admin/dashboard/stats', headers=headers)
        print(f"Regular user token - Status: {response.status_code}")
        if response.status_code == 403:
            print("  Correctly blocked non-admin access")


if __name__ == '__main__':
    print("Starting Admin Tests...")
    print("Make sure the Flask server is running on http://localhost:5001")

    admin_token = get_admin_token()
    if not admin_token:
        print("Failed to get admin token")
        exit(1)

    # Test dashboard
    test_dashboard_stats(admin_token)

    # Test product management
    product_id = test_create_product(admin_token)
    if product_id:
        test_update_product(admin_token, product_id)
    test_get_low_stock(admin_token)

    # Test category management
    category_id = test_create_category(admin_token)
    if category_id:
        test_update_category(admin_token, category_id)

    # Test order management
    test_get_all_orders(admin_token)

    # Test user management
    users = test_get_all_users(admin_token)
    if users and len(users) > 0:
        test_get_user_details(admin_token, users[0]['id'])

    # Test review management
    test_get_all_reviews(admin_token)

    # Test deletion
    if product_id:
        test_delete_product(admin_token, product_id)

    # Test authorization
    test_unauthorized_access()

    print("\n=== Tests Complete ===")
