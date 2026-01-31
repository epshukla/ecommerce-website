"""Payment routes"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Payment, Order, User
from app.services.payment_simulator import PaymentSimulator
from app.utils.decorators import admin_required

bp = Blueprint('payments', __name__, url_prefix='/api/payments')


@bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    """
    Initiate payment for an order
    Body: {
        "order_id": 1,
        "payment_method": "credit_card",
        "card_details": {
            "card_number": "4242424242424242",
            "cvv": "123",
            "expiry_month": "12",
            "expiry_year": "25",
            "cardholder_name": "John Doe"
        }
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        if 'order_id' not in data or 'payment_method' not in data:
            return jsonify({'error': 'order_id and payment_method are required'}), 400

        order_id = data['order_id']
        payment_method = data['payment_method']
        card_details = data.get('card_details')

        # Get order and verify ownership
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        if order.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Check if order already has a completed payment
        if order.payment_status == 'completed':
            return jsonify({'error': 'Order already paid'}), 400

        # Check if payment already exists for this order
        existing_payment = Payment.query.filter_by(order_id=order_id).first()
        if existing_payment and existing_payment.status == 'completed':
            return jsonify({'error': 'Payment already completed for this order'}), 400

        # Initiate payment through simulator
        transaction_id, status, message = PaymentSimulator.initiate_payment(
            float(order.total_amount),
            payment_method,
            card_details
        )

        if not transaction_id:
            return jsonify({'error': message}), 400

        # Create or update payment record
        if existing_payment:
            payment = existing_payment
            payment.transaction_id = transaction_id
            payment.payment_method = payment_method
            payment.status = status
        else:
            payment = Payment(
                order_id=order_id,
                amount=order.total_amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                status=status
            )
            db.session.add(payment)

        db.session.commit()

        # Simulate async webhook processing
        PaymentSimulator.simulate_webhook_callback(
            payment.id,
            '/api/payments/webhook',
            payment,
            db
        )

        return jsonify({
            'message': message,
            'transaction_id': transaction_id,
            'status': status,
            'payment': payment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/status/<transaction_id>', methods=['GET'])
@jwt_required()
def check_payment_status(transaction_id):
    """Check payment status by transaction ID"""
    try:
        current_user_id = get_jwt_identity()

        # Find payment by transaction ID
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Verify user owns the order
        if payment.order.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify(payment.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/order/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_payment(order_id):
    """Get payment details for an order"""
    try:
        current_user_id = get_jwt_identity()

        # Get order and verify ownership
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        if order.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Get payment
        payment = Payment.query.filter_by(order_id=order_id).first()
        if not payment:
            return jsonify({'error': 'No payment found for this order'}), 404

        return jsonify(payment.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/refund/<int:payment_id>', methods=['POST'])
@admin_required
def refund_payment(payment_id):
    """
    Refund a payment (admin only)
    Body: {
        "amount": 100.00,  # optional, defaults to full amount
        "reason": "Customer request"
    }
    """
    try:
        data = request.get_json()

        # Get payment
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Check if payment can be refunded
        if payment.status != 'completed':
            return jsonify({'error': 'Only completed payments can be refunded'}), 400

        # Get refund amount (default to full amount)
        refund_amount = data.get('amount', float(payment.amount))
        if refund_amount > float(payment.amount):
            return jsonify({'error': 'Refund amount exceeds payment amount'}), 400

        # Process refund through simulator
        refund_txn_id, status, message = PaymentSimulator.simulate_refund(
            payment.transaction_id,
            refund_amount
        )

        if status != 'completed':
            return jsonify({'error': message}), 400

        # Update payment status
        payment.status = 'refunded'

        # Update order status
        order = payment.order
        order.status = 'cancelled'
        order.payment_status = 'refunded'

        # Restore stock
        for item in order.items:
            item.product.stock_quantity += item.quantity

        db.session.commit()

        return jsonify({
            'message': message,
            'refund_transaction_id': refund_txn_id,
            'payment': payment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/methods', methods=['GET'])
def get_payment_methods():
    """Get list of supported payment methods"""
    return jsonify({
        'payment_methods': [
            {
                'id': 'credit_card',
                'name': 'Credit Card',
                'description': 'Visa, Mastercard, American Express'
            },
            {
                'id': 'debit_card',
                'name': 'Debit Card',
                'description': 'Debit cards with card number'
            },
            {
                'id': 'paypal',
                'name': 'PayPal',
                'description': 'Pay with your PayPal account'
            },
            {
                'id': 'bank_transfer',
                'name': 'Bank Transfer',
                'description': 'Direct bank transfer (manual verification required)'
            }
        ],
        'test_cards': {
            'success': '4242424242424242',
            'declined': '4000000000000002',
            'insufficient_funds': '4000000000009995',
            'expired': '4000000000000069',
            'processing_error': '4000000000000119',
            '3d_secure': '4000000000003220'
        }
    }), 200


@bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """
    Webhook endpoint for payment gateway callbacks
    In production, this would verify webhook signatures
    """
    try:
        data = request.get_json()

        # In a real implementation, verify webhook signature here
        # For simulation, we just log the webhook

        return jsonify({
            'message': 'Webhook received',
            'status': 'processed'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
