"""Test script for authentication endpoints"""
import requests
import json

BASE_URL = 'http://localhost:5001/api/auth'

def test_register():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    data = {
        'email': 'test@example.com',
        'password': 'TestPass123',
        'first_name': 'Test',
        'last_name': 'User'
    }

    response = requests.post(f'{BASE_URL}/register', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 201:
        return response.json().get('access_token')
    return None


def test_login():
    """Test user login"""
    print("\n=== Testing Login ===")
    data = {
        'email': 'john.doe@example.com',
        'password': 'password123'
    }

    response = requests.post(f'{BASE_URL}/login', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        return response.json().get('access_token')
    return None


def test_get_current_user(token):
    """Test getting current user"""
    print("\n=== Testing Get Current User ===")
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(f'{BASE_URL}/me', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_change_password(token):
    """Test changing password"""
    print("\n=== Testing Change Password ===")
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'old_password': 'password123',
        'new_password': 'NewPass123'
    }

    response = requests.post(f'{BASE_URL}/change-password', json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_invalid_login():
    """Test login with invalid credentials"""
    print("\n=== Testing Invalid Login ===")
    data = {
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    }

    response = requests.post(f'{BASE_URL}/login', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_weak_password():
    """Test registration with weak password"""
    print("\n=== Testing Weak Password ===")
    data = {
        'email': 'weak@example.com',
        'password': 'weak',
        'first_name': 'Weak',
        'last_name': 'Password'
    }

    response = requests.post(f'{BASE_URL}/register', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_logout(token):
    """Test logout"""
    print("\n=== Testing Logout ===")
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.post(f'{BASE_URL}/logout', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == '__main__':
    print("Starting Authentication Tests...")
    print("Make sure the Flask server is running on http://localhost:5000")

    # Test registration with new user
    test_register()

    # Test login with existing user
    token = test_login()

    if token:
        # Test authenticated endpoints
        test_get_current_user(token)
        test_change_password(token)
        test_logout(token)

    # Test error cases
    test_invalid_login()
    test_weak_password()

    print("\n=== Tests Complete ===")
