from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Cart, CartItem, Product

bp = Blueprint('cart', __name__, url_prefix='/api/cart')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    """Get current user's cart"""
    try:
        current_user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=current_user_id).first()

        if not cart:
            # Create cart if it doesn't exist
            cart = Cart(user_id=current_user_id)
            db.session.add(cart)
            db.session.commit()

        return jsonify(cart.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add item to cart"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        if 'product_id' not in data:
            return jsonify({'error': 'Product ID is required'}), 400

        product_id = data['product_id']
        quantity = data.get('quantity', 1)

        # Validate quantity
        if not isinstance(quantity, int) or quantity < 1:
            return jsonify({'error': 'Quantity must be a positive integer'}), 400

        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Check stock availability
        if product.stock_quantity < quantity:
            return jsonify({
                'error': 'Insufficient stock',
                'available': product.stock_quantity
            }), 400

        # Get or create cart
        cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not cart:
            cart = Cart(user_id=current_user_id)
            db.session.add(cart)
            db.session.commit()

        # Check if item already in cart
        cart_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_id=product_id
        ).first()

        if cart_item:
            # Update quantity
            new_quantity = cart_item.quantity + quantity

            # Check stock for new quantity
            if product.stock_quantity < new_quantity:
                return jsonify({
                    'error': 'Insufficient stock for requested quantity',
                    'available': product.stock_quantity,
                    'current_in_cart': cart_item.quantity
                }), 400

            cart_item.quantity = new_quantity
        else:
            # Add new item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)

        db.session.commit()

        return jsonify({
            'message': 'Item added to cart',
            'cart': cart.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate quantity
        if 'quantity' not in data:
            return jsonify({'error': 'Quantity is required'}), 400

        quantity = data['quantity']
        if not isinstance(quantity, int) or quantity < 1:
            return jsonify({'error': 'Quantity must be a positive integer'}), 400

        # Get cart item
        cart_item = CartItem.query.get(item_id)
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404

        # Verify cart belongs to user
        if cart_item.cart.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Check stock availability
        if cart_item.product.stock_quantity < quantity:
            return jsonify({
                'error': 'Insufficient stock',
                'available': cart_item.product.stock_quantity
            }), 400

        # Update quantity
        cart_item.quantity = quantity
        db.session.commit()

        return jsonify({
            'message': 'Cart updated',
            'cart': cart_item.cart.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        current_user_id = get_jwt_identity()

        # Get cart item
        cart_item = CartItem.query.get(item_id)
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404

        # Verify cart belongs to user
        if cart_item.cart.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        cart = cart_item.cart
        db.session.delete(cart_item)
        db.session.commit()

        return jsonify({
            'message': 'Item removed from cart',
            'cart': cart.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from cart"""
    try:
        current_user_id = get_jwt_identity()

        cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404

        # Delete all cart items
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()

        return jsonify({
            'message': 'Cart cleared',
            'cart': cart.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/count', methods=['GET'])
@jwt_required()
def get_cart_count():
    """Get total number of items in cart"""
    try:
        current_user_id = get_jwt_identity()

        cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not cart:
            return jsonify({'count': 0}), 200

        return jsonify({
            'count': cart.total_items,
            'subtotal': float(cart.subtotal)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
