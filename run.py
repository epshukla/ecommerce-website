import os
from app import create_app, db
from app.models import User, Address, Product, Category, Review, Cart, CartItem, Order, OrderItem, Payment, Wishlist, Coupon

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Make database and models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Address': Address,
        'Product': Product,
        'Category': Category,
        'Review': Review,
        'Cart': Cart,
        'CartItem': CartItem,
        'Order': Order,
        'OrderItem': OrderItem,
        'Payment': Payment,
        'Wishlist': Wishlist,
        'Coupon': Coupon
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
