"""Test script for product endpoints"""
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


def test_get_all_products():
    """Test getting all products"""
    print("\n=== Testing Get All Products ===")
    response = requests.get(f'{BASE_URL}/products/')
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total products: {data['pagination']['total']}")
    print(f"Products on page 1: {len(data['products'])}")
    if data['products']:
        print(f"First product: {data['products'][0]['name']} - ${data['products'][0]['price']}")


def test_search_products():
    """Test product search"""
    print("\n=== Testing Product Search ===")
    response = requests.get(f'{BASE_URL}/products/', params={'search': 'phone'})
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Search results for 'phone': {data['pagination']['total']} products")
    for product in data['products']:
        print(f"  - {product['name']}: ${product['price']}")


def test_filter_by_category():
    """Test filtering by category"""
    print("\n=== Testing Filter by Category ===")
    response = requests.get(f'{BASE_URL}/products/', params={'category_id': 5})
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Products in category 5: {data['pagination']['total']}")
    for product in data['products']:
        print(f"  - {product['name']}")


def test_price_filter():
    """Test price filtering"""
    print("\n=== Testing Price Filter ===")
    response = requests.get(f'{BASE_URL}/products/', params={
        'min_price': 50,
        'max_price': 500
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Products between $50-$500: {data['pagination']['total']}")
    for product in data['products'][:5]:
        print(f"  - {product['name']}: ${product['price']}")


def test_sorting():
    """Test product sorting"""
    print("\n=== Testing Sort by Price (Low to High) ===")
    response = requests.get(f'{BASE_URL}/products/', params={
        'sort_by': 'price',
        'order': 'asc'
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print("First 5 cheapest products:")
    for product in data['products'][:5]:
        print(f"  - {product['name']}: ${product['price']}")


def test_pagination():
    """Test pagination"""
    print("\n=== Testing Pagination ===")
    response = requests.get(f'{BASE_URL}/products/', params={
        'page': 1,
        'per_page': 3
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Page 1 of {data['pagination']['pages']}, showing {len(data['products'])} items")


def test_get_product_detail():
    """Test getting product details"""
    print("\n=== Testing Get Product Detail ===")
    response = requests.get(f'{BASE_URL}/products/1')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        product = response.json()
        print(f"Product: {product['name']}")
        print(f"Price: ${product['price']}")
        print(f"Stock: {product['stock_quantity']}")
        print(f"Average Rating: {product['average_rating']}")
        print(f"Reviews: {len(product.get('reviews', []))}")


def test_get_categories():
    """Test getting all categories"""
    print("\n=== Testing Get Categories ===")
    response = requests.get(f'{BASE_URL}/products/categories')
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total categories: {len(data['categories'])}")
    for category in data['categories'][:5]:
        print(f"  - {category['name']}")


def test_add_review(token):
    """Test adding a product review"""
    print("\n=== Testing Add Product Review ===")
    headers = {'Authorization': f'Bearer {token}'}
    review_data = {
        'rating': 5,
        'comment': 'Great product! Highly recommend.'
    }
    response = requests.post(f'{BASE_URL}/products/2/reviews',
                            json=review_data,
                            headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_search_suggestions():
    """Test search suggestions"""
    print("\n=== Testing Search Suggestions ===")
    response = requests.get(f'{BASE_URL}/products/search/suggestions', params={'q': 'lap'})
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Suggestions for 'lap':")
    for suggestion in data['suggestions']:
        print(f"  - {suggestion['name']}")


def test_rating_filter():
    """Test filtering by rating"""
    print("\n=== Testing Rating Filter ===")
    response = requests.get(f'{BASE_URL}/products/', params={'min_rating': 4})
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Products with rating >= 4: {data['pagination']['total']}")
    for product in data['products']:
        print(f"  - {product['name']}: {product['average_rating']} stars")


if __name__ == '__main__':
    print("Starting Product Tests...")
    print("Make sure the Flask server is running on http://localhost:5001")

    # Test public endpoints
    test_get_all_products()
    test_search_products()
    test_filter_by_category()
    test_price_filter()
    test_sorting()
    test_pagination()
    test_get_product_detail()
    test_get_categories()
    test_search_suggestions()
    test_rating_filter()

    # Test authenticated endpoints
    token = get_auth_token()
    if token:
        test_add_review(token)
    else:
        print("\nCould not get auth token, skipping review test")

    print("\n=== Tests Complete ===")
