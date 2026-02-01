"""Test script for payment endpoints"""
import requests
import json
import time

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


def create_test_order(token):
    """Create an order for payment testing"""
    print("\n=== Creating Test Order ===")
    headers = {'Authorization': f'Bearer {token}'}

    # Clear cart and add items
    requests.delete(f'{BASE_URL}/cart/clear', headers=headers)
    requests.post(f'{BASE_URL}/cart/add',
                 json={'product_id': 1, 'quantity': 1},
                 headers=headers)

    # Checkout
    response = requests.post(f'{BASE_URL}/orders/checkout',
                            json={'shipping_address_id': 1},
                            headers=headers)

    if response.status_code == 201:
        order_id = response.json()['order']['id']
        print(f"Order #{order_id} created")
        return order_id
    return None


def test_get_payment_methods():
    """Test getting supported payment methods"""
    print("\n=== Testing Get Payment Methods ===")
    response = requests.get(f'{BASE_URL}/payments/methods')
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nSupported payment methods:")
        for method in data['payment_methods']:
            print(f"  - {method['name']}: {method['description']}")

        print(f"\nTest cards:")
        for card_type, card_number in data['test_cards'].items():
            print(f"  - {card_type}: {card_number}")


def test_successful_payment(token, order_id):
    """Test successful payment with test card"""
    print("\n=== Testing Successful Payment ===")
    headers = {'Authorization': f'Bearer {token}'}

    payment_data = {
        'order_id': order_id,
        'payment_method': 'credit_card',
        'card_details': {
            'card_number': '4242424242424242',
            'cvv': '123',
            'expiry_month': '12',
            'expiry_year': '28',
            'cardholder_name': 'John Doe'
        }
    }

    response = requests.post(f'{BASE_URL}/payments/initiate',
                            json=payment_data,
                            headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        transaction_id = data['transaction_id']
        print(f"Transaction ID: {transaction_id}")
        print(f"Initial Status: {data['status']}")

        # Wait for async processing
        print("Waiting for payment processing...")
        time.sleep(4)

        # Check payment status
        status_response = requests.get(f'{BASE_URL}/payments/status/{transaction_id}',
                                      headers=headers)
        if status_response.status_code == 200:
            payment = status_response.json()
            print(f"Final Status: {payment['status']}")
            return transaction_id
    else:
        print(f"Error: {response.json()}")

    return None


def test_declined_payment(token, order_id):
    """Test declined payment"""
    print("\n=== Testing Declined Payment ===")
    headers = {'Authorization': f'Bearer {token}'}

    payment_data = {
        'order_id': order_id,
        'payment_method': 'credit_card',
        'card_details': {
            'card_number': '4000000000000002',  # Declined card
            'cvv': '123',
            'expiry_month': '12',
            'expiry_year': '28',
            'cardholder_name': 'John Doe'
        }
    }

    response = requests.post(f'{BASE_URL}/payments/initiate',
                            json=payment_data,
                            headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        transaction_id = data['transaction_id']
        print(f"Transaction ID: {transaction_id}")

        # Wait for async processing
        time.sleep(4)

        # Check payment status
        status_response = requests.get(f'{BASE_URL}/payments/status/{transaction_id}',
                                      headers=headers)
        if status_response.status_code == 200:
            payment = status_response.json()
            print(f"Final Status: {payment['status']}")


def test_insufficient_funds(token, order_id):
    """Test insufficient funds"""
    print("\n=== Testing Insufficient Funds ===")
    headers = {'Authorization': f'Bearer {token}'}

    payment_data = {
        'order_id': order_id,
        'payment_method': 'credit_card',
        'card_details': {
            'card_number': '4000000000009995',  # Insufficient funds
            'cvv': '123',
            'expiry_month': '12',
            'expiry_year': '28',
            'cardholder_name': 'John Doe'
        }
    }

    response = requests.post(f'{BASE_URL}/payments/initiate',
                            json=payment_data,
                            headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        transaction_id = response.json()['transaction_id']
        time.sleep(4)

        status_response = requests.get(f'{BASE_URL}/payments/status/{transaction_id}',
                                      headers=headers)
        if status_response.status_code == 200:
            payment = status_response.json()
            print(f"Final Status: {payment['status']}")


def test_paypal_payment(token, order_id):
    """Test PayPal payment"""
    print("\n=== Testing PayPal Payment ===")
    headers = {'Authorization': f'Bearer {token}'}

    payment_data = {
        'order_id': order_id,
        'payment_method': 'paypal'
    }

    response = requests.post(f'{BASE_URL}/payments/initiate',
                            json=payment_data,
                            headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        transaction_id = response.json()['transaction_id']
        print(f"Transaction ID: {transaction_id}")

        time.sleep(4)

        status_response = requests.get(f'{BASE_URL}/payments/status/{transaction_id}',
                                      headers=headers)
        if status_response.status_code == 200:
            payment = status_response.json()
            print(f"Final Status: {payment['status']}")


def test_invalid_card_number(token, order_id):
    """Test invalid card number"""
    print("\n=== Testing Invalid Card Number ===")
    headers = {'Authorization': f'Bearer {token}'}

    payment_data = {
        'order_id': order_id,
        'payment_method': 'credit_card',
        'card_details': {
            'card_number': '1234',  # Invalid
            'cvv': '123',
            'expiry_month': '12',
            'expiry_year': '28',
            'cardholder_name': 'John Doe'
        }
    }

    response = requests.post(f'{BASE_URL}/payments/initiate',
                            json=payment_data,
                            headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Error: {response.json()['error']}")


def test_expired_card(token, order_id):
    """Test expired card"""
    print("\n=== Testing Expired Card ===")
    headers = {'Authorization': f'Bearer {token}'}

    payment_data = {
        'order_id': order_id,
        'payment_method': 'credit_card',
        'card_details': {
            'card_number': '4242424242424242',
            'cvv': '123',
            'expiry_month': '01',
            'expiry_year': '20',  # Expired
            'cardholder_name': 'John Doe'
        }
    }

    response = requests.post(f'{BASE_URL}/payments/initiate',
                            json=payment_data,
                            headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Error: {response.json()['error']}")


def test_get_order_payment(token, order_id):
    """Test getting payment for an order"""
    print(f"\n=== Testing Get Order Payment ===")
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{BASE_URL}/payments/order/{order_id}',
                           headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        payment = response.json()
        print(f"Payment ID: {payment['id']}")
        print(f"Amount: ${payment['amount']}")
        print(f"Method: {payment['payment_method']}")
        print(f"Status: {payment['status']}")
        return payment['id']
    return None


def test_refund_payment(admin_token, payment_id):
    """Test refunding a payment (admin)"""
    print(f"\n=== Testing Refund Payment ===")
    headers = {'Authorization': f'Bearer {admin_token}'}

    refund_data = {
        'reason': 'Customer request'
    }

    response = requests.post(f'{BASE_URL}/payments/refund/{payment_id}',
                            json=refund_data,
                            headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Message: {data['message']}")
        print(f"Refund Transaction ID: {data['refund_transaction_id']}")
        print(f"Payment Status: {data['payment']['status']}")
    else:
        print(f"Error: {response.json()}")


if __name__ == '__main__':
    print("Starting Payment Tests...")
    print("Make sure the Flask server is running on http://localhost:5001")

    # Get tokens
    user_token = get_auth_token('john.doe@example.com', 'NewPass123')
    admin_token = get_auth_token('admin@example.com', 'admin123')

    if not user_token:
        print("Failed to get user token")
        exit(1)

    # Test payment methods info
    test_get_payment_methods()

    # Test successful payment
    order_id = create_test_order(user_token)
    if order_id:
        test_successful_payment(user_token, order_id)

    # Test declined payment
    order_id2 = create_test_order(user_token)
    if order_id2:
        test_declined_payment(user_token, order_id2)

    # Test insufficient funds
    order_id3 = create_test_order(user_token)
    if order_id3:
        test_insufficient_funds(user_token, order_id3)

    # Test PayPal
    order_id4 = create_test_order(user_token)
    if order_id4:
        test_paypal_payment(user_token, order_id4)

    # Test validation errors
    order_id5 = create_test_order(user_token)
    if order_id5:
        test_invalid_card_number(user_token, order_id5)
        test_expired_card(user_token, order_id5)

    # Test get order payment
    if order_id:
        payment_id = test_get_order_payment(user_token, order_id)

        # Test refund (admin only)
        if payment_id and admin_token:
            test_refund_payment(admin_token, payment_id)

    print("\n=== Tests Complete ===")
