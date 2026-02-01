#!/usr/bin/env python3
"""
Script to update product image from a URL or local file

Usage:
    python scripts/update_product_image.py <product_name> <image_url_or_path>

Example:
    python scripts/update_product_image.py "Blender" "https://example.com/blender.jpg"
    python scripts/update_product_image.py "Laptop" "images/laptop.jpg"
"""

import os
import sys
import requests
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.models import Product
from app.utils.image_utils import optimize_image
from run import app


def download_image(url, save_path):
    """Download image from URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    product_name = sys.argv[1]
    image_source = sys.argv[2]

    # Generate unique filename
    timestamp = int(datetime.now().timestamp())
    ext = 'jpg'
    if image_source.startswith('http'):
        # Extract extension from URL if possible
        url_ext = image_source.split('.')[-1].lower()
        if url_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            ext = url_ext
    else:
        # Get extension from local file
        ext = image_source.split('.')[-1].lower()

    filename = f"{product_name.lower().replace(' ', '_')}_{timestamp}.{ext}"
    image_path = f"uploads/products/{filename}"

    # Download or copy image
    if image_source.startswith('http'):
        print(f"Downloading image from: {image_source}")
        if not download_image(image_source, image_path):
            print("Failed to download image")
            sys.exit(1)
    else:
        print(f"Copying image from: {image_source}")
        import shutil
        try:
            shutil.copy(image_source, image_path)
        except Exception as e:
            print(f"Error copying image: {str(e)}")
            sys.exit(1)

    # Optimize image
    print(f"Optimizing image: {image_path}")
    optimize_image(image_path)
    print("Image optimized successfully!")

    # Update product in database
    with app.app_context():
        product = Product.query.filter(Product.name.ilike(f'%{product_name}%')).first()

        if product:
            print(f"Found product: {product.name} (ID: {product.id})")
            product.image_url = f'/uploads/products/{filename}'
            db.session.commit()
            print(f"Updated product image URL to: {product.image_url}")
        else:
            print(f"No product found matching: {product_name}")
            print("\nAvailable products:")
            products = Product.query.all()
            for p in products:
                print(f"  - {p.name} (ID: {p.id})")
            sys.exit(1)


if __name__ == '__main__':
    main()
