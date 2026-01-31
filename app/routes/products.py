from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from app import db
from app.models import Product, Category, Review, User
from app.utils.decorators import admin_required

bp = Blueprint('products', __name__, url_prefix='/api/products')


@bp.route('/', methods=['GET'])
def get_products():
    """
    Get all products with optional filtering, sorting, and pagination
    Query params:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 12)
    - category_id: Filter by category
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    - search: Search in product name and description
    - sort_by: Sort field (price, name, rating, created_at)
    - order: Sort order (asc, desc)
    - min_rating: Minimum average rating
    """
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        per_page = min(per_page, 100)  # Max 100 items per page

        # Build query
        query = Product.query

        # Category filter
        category_id = request.args.get('category_id', type=int)
        if category_id:
            query = query.filter(Product.category_id == category_id)

        # Price filters
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        # Search filter
        search = request.args.get('search', '').strip()
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern)
                )
            )

        # Stock filter (only show in-stock by default)
        show_out_of_stock = request.args.get('show_out_of_stock', 'false').lower() == 'true'
        if not show_out_of_stock:
            query = query.filter(Product.stock_quantity > 0)

        # Get all products for rating filter (need to compute average)
        products_list = query.all()

        # Apply rating filter if specified
        min_rating = request.args.get('min_rating', type=float)
        if min_rating is not None:
            products_list = [p for p in products_list if p.average_rating >= min_rating]

        # Sorting
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')

        if sort_by == 'price':
            products_list.sort(key=lambda x: float(x.price), reverse=(order == 'desc'))
        elif sort_by == 'name':
            products_list.sort(key=lambda x: x.name.lower(), reverse=(order == 'desc'))
        elif sort_by == 'rating':
            products_list.sort(key=lambda x: x.average_rating, reverse=(order == 'desc'))
        else:  # created_at or default
            products_list.sort(key=lambda x: x.created_at, reverse=(order == 'desc'))

        # Manual pagination
        total = len(products_list)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_products = products_list[start:end]

        return jsonify({
            'products': [product.to_dict() for product in paginated_products],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product details"""
    try:
        product = Product.query.get(product_id)

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        product_data = product.to_dict()

        # Include reviews
        reviews = [review.to_dict() for review in product.reviews]
        product_data['reviews'] = reviews

        return jsonify(product_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()

        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get category details with products"""
    try:
        category = Category.query.get(category_id)

        if not category:
            return jsonify({'error': 'Category not found'}), 404

        category_data = category.to_dict()
        category_data['products'] = [product.to_dict() for product in category.products]
        category_data['subcategories'] = [sub.to_dict() for sub in category.subcategories]

        return jsonify(category_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    """Get all reviews for a product"""
    try:
        product = Product.query.get(product_id)

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        reviews = [review.to_dict() for review in product.reviews]

        return jsonify({
            'product_id': product_id,
            'reviews': reviews,
            'average_rating': product.average_rating,
            'total_reviews': len(reviews)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def add_product_review(product_id):
    """Add a review for a product"""
    try:
        current_user_id = get_jwt_identity()
        product = Product.query.get(product_id)

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        data = request.get_json()

        # Validate required fields
        if 'rating' not in data:
            return jsonify({'error': 'Rating is required'}), 400

        rating = data['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        # Check if user already reviewed this product
        existing_review = Review.query.filter_by(
            product_id=product_id,
            user_id=current_user_id
        ).first()

        if existing_review:
            return jsonify({'error': 'You have already reviewed this product'}), 409

        # Create review
        review = Review(
            product_id=product_id,
            user_id=current_user_id,
            rating=rating,
            comment=data.get('comment', '')
        )

        db.session.add(review)
        db.session.commit()

        return jsonify({
            'message': 'Review added successfully',
            'review': review.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/search/suggestions', methods=['GET'])
def search_suggestions():
    """Get search suggestions based on partial query"""
    try:
        query = request.args.get('q', '').strip()

        if not query or len(query) < 2:
            return jsonify({'suggestions': []}), 200

        # Search in product names
        search_pattern = f'%{query}%'
        products = Product.query.filter(
            Product.name.ilike(search_pattern)
        ).limit(10).all()

        suggestions = [{'id': p.id, 'name': p.name, 'price': float(p.price)} for p in products]

        return jsonify({'suggestions': suggestions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
