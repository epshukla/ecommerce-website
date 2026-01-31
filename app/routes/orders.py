from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Order, OrderItem, Cart, CartItem, Product, Address, User
from decimal import Decimal

bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    """Create order from cart"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate shipping address
        if 'shipping_address_id' not in data:
            return jsonify({'error': 'Shipping address is required'}), 400

        shipping_address_id = data['shipping_address_id']

        # Verify address belongs to user
        address = Address.query.get(shipping_address_id)
        if not address or address.user_id != current_user_id:
            return jsonify({'error': 'Invalid shipping address'}), 400

        # Get user's cart
        cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not cart or not cart.items:
            return jsonify({'error': 'Cart is empty'}), 400

        # Validate stock for all items
        for cart_item in cart.items:
            if cart_item.product.stock_quantity < cart_item.quantity:
                return jsonify({
                    'error': f'Insufficient stock for {cart_item.product.name}',
                    'product': cart_item.product.name,
                    'requested': cart_item.quantity,
                    'available': cart_item.product.stock_quantity
                }), 400

        # Calculate total
        total_amount = cart.subtotal

        # Create order
        order = Order(
            user_id=current_user_id,
            total_amount=total_amount,
            shipping_address_id=shipping_address_id,
            status='pending',
            payment_status='pending'
        )
        db.session.add(order)
        db.session.flush()  # Get order ID

        # Create order items and reduce stock
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.price
            )
            db.session.add(order_item)

            # Reduce stock
            cart_item.product.stock_quantity -= cart_item.quantity

        # Clear cart
        CartItem.query.filter_by(cart_id=cart.id).delete()

        db.session.commit()

        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get all orders for current user"""
    try:
        current_user_id = get_jwt_identity()

        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Query orders
        orders_query = Order.query.filter_by(user_id=current_user_id).order_by(Order.created_at.desc())

        # Filter by status if provided
        status = request.args.get('status')
        if status:
            orders_query = orders_query.filter_by(status=status)

        # Paginate
        orders = orders_query.paginate(page=page, per_page=per_page, error_out=False)

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


@bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get specific order details"""
    try:
        current_user_id = get_jwt_identity()

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Verify order belongs to user
        if order.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify(order.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    try:
        current_user_id = get_jwt_identity()

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Verify order belongs to user
        if order.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Check if order can be cancelled
        if order.status in ['delivered', 'cancelled']:
            return jsonify({'error': f'Cannot cancel order with status: {order.status}'}), 400

        # Restore stock
        for item in order.items:
            item.product.stock_quantity += item.quantity

        # Update order status
        order.status = 'cancelled'
        order.payment_status = 'failed'

        db.session.commit()

        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (admin or system use)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Check if user is admin
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Validate status
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        new_status = data.get('status')

        if not new_status or new_status not in valid_statuses:
            return jsonify({
                'error': 'Invalid status',
                'valid_statuses': valid_statuses
            }), 400

        order.status = new_status
        db.session.commit()

        return jsonify({
            'message': 'Order status updated',
            'order': order.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_order_stats():
    """Get order statistics for current user"""
    try:
        current_user_id = get_jwt_identity()

        orders = Order.query.filter_by(user_id=current_user_id).all()

        stats = {
            'total_orders': len(orders),
            'pending': len([o for o in orders if o.status == 'pending']),
            'processing': len([o for o in orders if o.status == 'processing']),
            'shipped': len([o for o in orders if o.status == 'shipped']),
            'delivered': len([o for o in orders if o.status == 'delivered']),
            'cancelled': len([o for o in orders if o.status == 'cancelled']),
            'total_spent': float(sum(o.total_amount for o in orders if o.status != 'cancelled'))
        }

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
