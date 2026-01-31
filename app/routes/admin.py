from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app import db
from app.models import Product, Category, Order, User, Payment, Review
from app.utils.decorators import admin_required
from app.utils.validators import validate_required_fields
from decimal import Decimal
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ==================== Dashboard Analytics ====================

@bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get overall dashboard statistics"""
    try:
        # Total counts
        total_users = User.query.filter_by(role='user').count()
        total_products = Product.query.count()
        total_orders = Order.query.count()

        # Revenue stats
        completed_orders = Order.query.filter_by(payment_status='completed').all()
        total_revenue = sum(float(order.total_amount) for order in completed_orders)

        # Recent orders (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_orders = Order.query.filter(Order.created_at >= thirty_days_ago).count()

        # Order status breakdown
        pending_orders = Order.query.filter_by(status='pending').count()
        processing_orders = Order.query.filter_by(status='processing').count()
        shipped_orders = Order.query.filter_by(status='shipped').count()
        delivered_orders = Order.query.filter_by(status='delivered').count()

        # Low stock products
        low_stock = Product.query.filter(Product.stock_quantity < 10).count()

        # Top selling products (by order items)
        from app.models import OrderItem
        top_products = db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem).group_by(Product.id).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()

        return jsonify({
            'overview': {
                'total_users': total_users,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'recent_orders_30d': recent_orders
            },
            'orders': {
                'pending': pending_orders,
                'processing': processing_orders,
                'shipped': shipped_orders,
                'delivered': delivered_orders
            },
            'inventory': {
                'low_stock_count': low_stock
            },
            'top_products': [{'name': p[0], 'sold': int(p[1])} for p in top_products]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Product Management ====================

@bp.route('/products', methods=['POST'])
@admin_required
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()

        # Validate required fields
        required = ['name', 'price', 'category_id', 'stock_quantity']
        is_valid, missing = validate_required_fields(data, required)
        if not is_valid:
            return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

        # Create product
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=Decimal(str(data['price'])),
            category_id=data['category_id'],
            stock_quantity=data['stock_quantity'],
            image_url=data.get('image_url', '')
        )

        db.session.add(product)
        db.session.commit()

        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update a product"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        data = request.get_json()

        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = Decimal(str(data['price']))
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'stock_quantity' in data:
            product.stock_quantity = data['stock_quantity']
        if 'image_url' in data:
            product.image_url = data['image_url']

        db.session.commit()

        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        db.session.delete(product)
        db.session.commit()

        return jsonify({'message': 'Product deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/products/low-stock', methods=['GET'])
@admin_required
def get_low_stock_products():
    """Get products with low stock"""
    try:
        threshold = request.args.get('threshold', 10, type=int)
        products = Product.query.filter(Product.stock_quantity < threshold).all()

        return jsonify({
            'products': [p.to_dict() for p in products],
            'count': len(products)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Category Management ====================

@bp.route('/categories', methods=['POST'])
@admin_required
def create_category():
    """Create a new category"""
    try:
        data = request.get_json()

        if 'name' not in data:
            return jsonify({'error': 'Category name is required'}), 400

        category = Category(
            name=data['name'],
            description=data.get('description', ''),
            parent_id=data.get('parent_id')
        )

        db.session.add(category)
        db.session.commit()

        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """Update a category"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        data = request.get_json()

        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'parent_id' in data:
            category.parent_id = data['parent_id']

        db.session.commit()

        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """Delete a category"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        # Check if category has products
        if category.products:
            return jsonify({'error': 'Cannot delete category with products'}), 400

        db.session.delete(category)
        db.session.commit()

        return jsonify({'message': 'Category deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== Order Management ====================

@bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    """Get all orders with filters"""
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Filters
        status = request.args.get('status')
        payment_status = request.args.get('payment_status')

        query = Order.query.order_by(Order.created_at.desc())

        if status:
            query = query.filter_by(status=status)
        if payment_status:
            query = query.filter_by(payment_status=payment_status)

        orders = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': orders.total,
                'pages': orders.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== User Management ====================

@bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        users = User.query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_details(user_id):
    """Get detailed user information"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get user stats
        user_orders = Order.query.filter_by(user_id=user_id).all()
        total_spent = sum(float(o.total_amount) for o in user_orders if o.payment_status == 'completed')

        user_data = user.to_dict()
        user_data['stats'] = {
            'total_orders': len(user_orders),
            'total_spent': total_spent,
            'addresses': [addr.to_dict() for addr in user.addresses]
        }

        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>/toggle-role', methods=['POST'])
@admin_required
def toggle_user_role(user_id):
    """Toggle user role between user and admin"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Toggle role
        user.role = 'admin' if user.role == 'user' else 'user'
        db.session.commit()

        return jsonify({
            'message': f'User role updated to {user.role}',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== Reviews Management ====================

@bp.route('/reviews', methods=['GET'])
@admin_required
def get_all_reviews():
    """Get all reviews"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        reviews = Review.query.order_by(Review.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'reviews': [review.to_dict() for review in reviews.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': reviews.total,
                'pages': reviews.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@admin_required
def delete_review(review_id):
    """Delete a review"""
    try:
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'error': 'Review not found'}), 404

        db.session.delete(review)
        db.session.commit()

        return jsonify({'message': 'Review deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
