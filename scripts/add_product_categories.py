#!/usr/bin/env python3
"""
Script to add categories to all products
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.models import Product, Category
from run import app


# Category mapping
PRODUCT_CATEGORIES = {
    'iPhone 15 Pro': 'Electronics',
    'Samsung Galaxy S24': 'Electronics',
    'MacBook Pro 16"': 'Electronics',
    'Dell XPS 15': 'Electronics',
    'Wireless Headphones': 'Electronics',
    "Men's Cotton T-Shirt": 'Apparel',
    "Women's Summer Dress": 'Apparel',
    'The Great Gatsby': 'Books',
    'Blender Pro': 'Appliances',
    'Coffee Maker': 'Appliances',
}


def main():
    with app.app_context():
        # Create categories if they don't exist
        categories_to_create = ['Electronics', 'Apparel', 'Books', 'Appliances']
        category_objects = {}

        for cat_name in categories_to_create:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                category = Category(name=cat_name)
                db.session.add(category)
                print(f"Created category: {cat_name}")
            else:
                print(f"Category already exists: {cat_name}")
            category_objects[cat_name] = category

        db.session.commit()
        print("\nCategories created successfully!\n")

        # Update products with categories
        products = Product.query.all()

        for product in products:
            if product.name in PRODUCT_CATEGORIES:
                category_name = PRODUCT_CATEGORIES[product.name]
                category = category_objects[category_name]
                product.category_id = category.id
                print(f"Updated {product.name} -> {category_name}")
            else:
                print(f"No category mapping for: {product.name}")

        db.session.commit()
        print("\nProducts updated with categories successfully!")

        # Display all products with categories
        print("\nAll products with categories:")
        products = Product.query.all()
        for p in products:
            print(f"  - {p.name}: {p.category.name if p.category else 'No category'}")


if __name__ == '__main__':
    main()
