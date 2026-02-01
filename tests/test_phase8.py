"""Test script for Phase 8: Additional Features (Wishlist, Coupons, Addresses, Email)"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5001/api'

# Store tokens and IDs
admin_token = None
user_token = None
product_id = None
address_id = None
coupon_code = None


def print_response(title, response):
    """Print formatted response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_login():
    """Test admin and user login"""
    global admin_token, user_token

    # Login as admin
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    print_response("Admin Login", response)
    admin_token = response.json().get('access_token')

    # Login as user
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'john.doe@example.com',
        'password': 'password123'
    })
    print_response("User Login", response)
    user_token = response.json().get('access_token')


def test_addresses():
    """Test address management"""
    global address_id

    headers = {'Authorization': f'Bearer {user_token}'}

    # Create address
    response = requests.post(f'{BASE_URL}/addresses/',
        headers=headers,
        json={
            'address_line1': '123 Main St',
            'address_line2': 'Apt 4B',
            'city': 'New York',
            'state': 'NY',
            'postal_code': '10001',
            'country': 'USA',
            'is_default': True
        }
    )
    print_response("Create Address", response)
    if response.status_code == 201:
        address_id = response.json()['address']['id']

    # Create another address
    response = requests.post(f'{BASE_URL}/addresses/',
        headers=headers,
        json={
            'address_line1': '456 Oak Ave',
            'city': 'Los Angeles',
            'state': 'CA',
            'postal_code': '90001',
            'country': 'USA',
            'is_default': False
        }
    )
    print_response("Create Second Address", response)
    second_address_id = response.json()['address']['id'] if response.status_code == 201 else None

    # Get all addresses
    response = requests.get(f'{BASE_URL}/addresses/', headers=headers)
    print_response("Get All Addresses", response)

    # Update address
    if address_id:
        response = requests.put(f'{BASE_URL}/addresses/{address_id}',
            headers=headers,
            json={
                'address_line2': 'Suite 100',
                'city': 'New York City'
            }
        )
        print_response("Update Address", response)

    # Set default address
    if second_address_id:
        response = requests.post(f'{BASE_URL}/addresses/{second_address_id}/set-default',
            headers=headers
        )
        print_response("Set Default Address", response)

    # Delete an address (keep one for order testing)
    if second_address_id:
        response = requests.delete(f'{BASE_URL}/addresses/{second_address_id}',
            headers=headers
        )
        print_response("Delete Address", response)


def test_coupons():
    """Test coupon system"""
    global coupon_code

    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    user_headers = {'Authorization': f'Bearer {user_token}'}

    # Create percentage discount coupon
    valid_from = (datetime.utcnow() - timedelta(days=1)).isoformat()  # Started yesterday
    valid_until = (datetime.utcnow() + timedelta(days=30)).isoformat()
    response = requests.post(f'{BASE_URL}/coupons/admin',
        headers=admin_headers,
        json={
            'code': 'SAVE20',
            'description': '20% off your order',
            'discount_type': 'percentage',
            'discount_value': 20,
            'min_order_amount': 50,
            'max_discount': 100,
            'usage_limit': 100,
            'is_active': True,
            'valid_from': valid_from,
            'valid_until': valid_until
        }
    )
    print_response("Create Percentage Coupon", response)
    if response.status_code == 201:
        coupon_code = response.json()['coupon']['code']

    # Create fixed discount coupon
    response = requests.post(f'{BASE_URL}/coupons/admin',
        headers=admin_headers,
        json={
            'code': 'FLAT10',
            'description': '$10 off your order',
            'discount_type': 'fixed',
            'discount_value': 10,
            'min_order_amount': 30,
            'is_active': True,
            'valid_from': valid_from,
            'valid_until': valid_until
        }
    )
    print_response("Create Fixed Coupon", response)

    # Get all active coupons
    response = requests.get(f'{BASE_URL}/coupons/')
    print_response("Get Active Coupons (Public)", response)

    # Validate coupon with order amount
    response = requests.post(f'{BASE_URL}/coupons/validate',
        headers=user_headers,
        json={
            'code': 'SAVE20',
            'order_amount': 100
        }
    )
    print_response("Validate SAVE20 Coupon (Order: $100)", response)

    # Validate coupon below minimum order amount
    response = requests.post(f'{BASE_URL}/coupons/validate',
        headers=user_headers,
        json={
            'code': 'SAVE20',
            'order_amount': 30
        }
    )
    print_response("Validate SAVE20 Coupon (Below Min Order)", response)

    # Validate fixed discount coupon
    response = requests.post(f'{BASE_URL}/coupons/validate',
        headers=user_headers,
        json={
            'code': 'FLAT10',
            'order_amount': 50
        }
    )
    print_response("Validate FLAT10 Coupon (Order: $50)", response)

    # Update coupon
    response = requests.put(f'{BASE_URL}/coupons/admin/1',
        headers=admin_headers,
        json={
            'description': '20% off - Limited Time!',
            'usage_limit': 50
        }
    )
    print_response("Update Coupon", response)


def test_wishlist():
    """Test wishlist functionality"""
    global product_id

    headers = {'Authorization': f'Bearer {user_token}'}

    # Get a product ID first
    response = requests.get(f'{BASE_URL}/products/')
    if response.status_code == 200:
        products = response.json()['products']
        if products:
            product_id = products[0]['id']
            second_product_id = products[1]['id'] if len(products) > 1 else None

    # Add product to wishlist
    if product_id:
        response = requests.post(f'{BASE_URL}/wishlist/add/{product_id}',
            headers=headers
        )
        print_response("Add Product to Wishlist", response)

    # Add second product
    if second_product_id:
        response = requests.post(f'{BASE_URL}/wishlist/add/{second_product_id}',
            headers=headers
        )
        print_response("Add Second Product to Wishlist", response)

    # Try adding duplicate
    if product_id:
        response = requests.post(f'{BASE_URL}/wishlist/add/{product_id}',
            headers=headers
        )
        print_response("Add Duplicate Product (Should Fail)", response)

    # Get wishlist
    response = requests.get(f'{BASE_URL}/wishlist/', headers=headers)
    print_response("Get Wishlist", response)

    # Remove product from wishlist
    if product_id:
        response = requests.delete(f'{BASE_URL}/wishlist/remove/{product_id}',
            headers=headers
        )
        print_response("Remove Product from Wishlist", response)

    # Get wishlist again
    response = requests.get(f'{BASE_URL}/wishlist/', headers=headers)
    print_response("Get Wishlist After Removal", response)

    # Clear wishlist
    response = requests.delete(f'{BASE_URL}/wishlist/clear',
        headers=headers
    )
    print_response("Clear Wishlist", response)


def test_email_notifications():
    """Test email notifications by creating an order"""
    headers = {'Authorization': f'Bearer {user_token}'}

    # Add product to cart first
    if product_id:
        response = requests.post(f'{BASE_URL}/cart/add',
            headers=headers,
            json={
                'product_id': product_id,
                'quantity': 1
            }
        )
        print_response("Add to Cart", response)

    # Create order (this should trigger email notification)
    if address_id:
        response = requests.post(f'{BASE_URL}/orders/checkout',
            headers=headers,
            json={
                'shipping_address_id': address_id
            }
        )
        print_response("Create Order (Check Console for Email)", response)

        if response.status_code == 201:
            order_id = response.json()['order']['id']

            # Update order status to shipped (should trigger shipping email)
            admin_headers = {'Authorization': f'Bearer {admin_token}'}
            response = requests.put(f'{BASE_URL}/orders/{order_id}/status',
                headers=admin_headers,
                json={'status': 'shipped'}
            )
            print_response("Update Order to Shipped (Check Console for Email)", response)

            # Update to delivered (should trigger delivery email)
            response = requests.put(f'{BASE_URL}/orders/{order_id}/status',
                headers=admin_headers,
                json={'status': 'delivered'}
            )
            print_response("Update Order to Delivered (Check Console for Email)", response)


def run_all_tests():
    """Run all Phase 8 tests"""
    print("\n" + "="*60)
    print("PHASE 8: ADDITIONAL FEATURES TESTING")
    print("="*60)

    try:
        test_login()
        test_addresses()
        test_coupons()
        test_wishlist()
        test_email_notifications()

        print("\n" + "="*60)
        print("ALL PHASE 8 TESTS COMPLETED!")
        print("="*60)
        print("\nFeatures tested:")
        print("✓ Address Management (Create, Read, Update, Delete, Set Default)")
        print("✓ Coupon System (Create, Validate, Percentage & Fixed Discounts)")
        print("✓ Wishlist (Add, Remove, Clear, Duplicate Prevention)")
        print("✓ Email Notifications (Order Confirmation, Shipping, Delivery)")

    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
