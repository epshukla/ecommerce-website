"""Seed data script to populate the database with sample data"""
from app import create_app, db
from app.models import User, Address, Product, Category, Review, Cart
from decimal import Decimal

def seed_database():
    """Populate database with sample data"""
    app = create_app('development')

    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        # Create categories
        print("Creating categories...")
        electronics = Category(name='Electronics', description='Electronic devices and gadgets')
        clothing = Category(name='Clothing', description='Fashion and apparel')
        books = Category(name='Books', description='Books and literature')
        home = Category(name='Home & Kitchen', description='Home and kitchen items')

        db.session.add_all([electronics, clothing, books, home])
        db.session.commit()

        # Create subcategories
        phones = Category(name='Smartphones', parent_id=electronics.id, description='Mobile phones')
        laptops = Category(name='Laptops', parent_id=electronics.id, description='Laptop computers')
        mens = Category(name="Men's Clothing", parent_id=clothing.id, description='Clothing for men')
        womens = Category(name="Women's Clothing", parent_id=clothing.id, description='Clothing for women')

        db.session.add_all([phones, laptops, mens, womens])
        db.session.commit()

        # Create users
        print("Creating users...")
        admin = User(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.set_password('admin123')

        customer1 = User(
            email='john.doe@example.com',
            first_name='John',
            last_name='Doe',
            role='user'
        )
        customer1.set_password('password123')

        customer2 = User(
            email='jane.smith@example.com',
            first_name='Jane',
            last_name='Smith',
            role='user'
        )
        customer2.set_password('password123')

        db.session.add_all([admin, customer1, customer2])
        db.session.commit()

        # Create addresses
        print("Creating addresses...")
        address1 = Address(
            user_id=customer1.id,
            address_line1='123 Main St',
            address_line2='Apt 4B',
            city='New York',
            state='NY',
            postal_code='10001',
            country='USA',
            is_default=True
        )

        address2 = Address(
            user_id=customer2.id,
            address_line1='456 Oak Ave',
            city='Los Angeles',
            state='CA',
            postal_code='90001',
            country='USA',
            is_default=True
        )

        db.session.add_all([address1, address2])
        db.session.commit()

        # Create products
        print("Creating products...")
        products = [
            Product(
                name='iPhone 15 Pro',
                description='Latest Apple smartphone with advanced features',
                price=Decimal('999.99'),
                category_id=phones.id,
                stock_quantity=50,
                image_url='/static/uploads/iphone15.jpg'
            ),
            Product(
                name='Samsung Galaxy S24',
                description='Flagship Samsung smartphone',
                price=Decimal('899.99'),
                category_id=phones.id,
                stock_quantity=45,
                image_url='/static/uploads/galaxy-s24.jpg'
            ),
            Product(
                name='MacBook Pro 16"',
                description='Powerful laptop for professionals',
                price=Decimal('2499.99'),
                category_id=laptops.id,
                stock_quantity=20,
                image_url='/static/uploads/macbook-pro.jpg'
            ),
            Product(
                name='Dell XPS 15',
                description='High-performance Windows laptop',
                price=Decimal('1799.99'),
                category_id=laptops.id,
                stock_quantity=25,
                image_url='/static/uploads/dell-xps.jpg'
            ),
            Product(
                name="Men's Cotton T-Shirt",
                description='Comfortable cotton t-shirt in various colors',
                price=Decimal('24.99'),
                category_id=mens.id,
                stock_quantity=100,
                image_url='/static/uploads/mens-tshirt.jpg'
            ),
            Product(
                name="Women's Summer Dress",
                description='Light and elegant summer dress',
                price=Decimal('49.99'),
                category_id=womens.id,
                stock_quantity=75,
                image_url='/static/uploads/womens-dress.jpg'
            ),
            Product(
                name='The Great Gatsby',
                description='Classic American novel by F. Scott Fitzgerald',
                price=Decimal('12.99'),
                category_id=books.id,
                stock_quantity=200,
                image_url='/static/uploads/gatsby.jpg'
            ),
            Product(
                name='Coffee Maker',
                description='Programmable coffee maker with timer',
                price=Decimal('79.99'),
                category_id=home.id,
                stock_quantity=60,
                image_url='/static/uploads/coffee-maker.jpg'
            ),
            Product(
                name='Blender Pro',
                description='High-speed blender for smoothies and more',
                price=Decimal('129.99'),
                category_id=home.id,
                stock_quantity=40,
                image_url='/static/uploads/blender.jpg'
            ),
            Product(
                name='Wireless Headphones',
                description='Noise-cancelling Bluetooth headphones',
                price=Decimal('199.99'),
                category_id=electronics.id,
                stock_quantity=80,
                image_url='/static/uploads/headphones.jpg'
            )
        ]

        db.session.add_all(products)
        db.session.commit()

        # Create reviews
        print("Creating reviews...")
        reviews = [
            Review(product_id=products[0].id, user_id=customer1.id, rating=5,
                   comment='Excellent phone! Love the camera quality.'),
            Review(product_id=products[0].id, user_id=customer2.id, rating=4,
                   comment='Great phone but a bit pricey.'),
            Review(product_id=products[2].id, user_id=customer1.id, rating=5,
                   comment='Best laptop I have ever owned!'),
            Review(product_id=products[4].id, user_id=customer2.id, rating=4,
                   comment='Good quality shirt, fits well.'),
            Review(product_id=products[6].id, user_id=customer1.id, rating=5,
                   comment='Timeless classic, highly recommend!'),
        ]

        db.session.add_all(reviews)
        db.session.commit()

        # Create carts for users
        print("Creating carts...")
        cart1 = Cart(user_id=customer1.id)
        cart2 = Cart(user_id=customer2.id)

        db.session.add_all([cart1, cart2])
        db.session.commit()

        print("Database seeded successfully!")
        print("\nSample credentials:")
        print("Admin: admin@example.com / admin123")
        print("Customer 1: john.doe@example.com / password123")
        print("Customer 2: jane.smith@example.com / password123")

if __name__ == '__main__':
    seed_database()
