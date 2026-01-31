"""Coupon routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Coupon
from app.utils.decorators import admin_required
from datetime import datetime
from decimal import Decimal

bp = Blueprint('coupons', __name__, url_prefix='/api/coupons')


@bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_coupon():
    """Validate a coupon code"""
    try:
        data = request.get_json()

        if 'code' not in data:
            return jsonify({'error': 'Coupon code is required'}), 400

        code = data['code'].upper()
        order_amount = data.get('order_amount', 0)

        coupon = Coupon.query.filter_by(code=code).first()
        if not coupon:
            return jsonify({'error': 'Invalid coupon code'}), 404

        # Check if valid
        is_valid, message = coupon.is_valid()
        if not is_valid:
            return jsonify({'error': message}), 400

        # Calculate discount
        discount, discount_message = coupon.calculate_discount(order_amount)

        return jsonify({
            'valid': True,
            'coupon': coupon.to_dict(),
            'discount': discount,
            'message': discount_message
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['GET'])
def get_active_coupons():
    """Get all active coupons (public)"""
    try:
        coupons = Coupon.query.filter_by(is_active=True).all()

        # Only return active coupons that haven't expired
        now = datetime.utcnow()
        active_coupons = [
            c for c in coupons
            if (not c.valid_until or c.valid_until > now) and
               (not c.usage_limit or c.used_count < c.usage_limit)
        ]

        return jsonify({
            'coupons': [c.to_dict() for c in active_coupons]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Admin routes
@bp.route('/admin', methods=['POST'])
@admin_required
def create_coupon():
    """Create a new coupon (admin only)"""
    try:
        data = request.get_json()

        # Validate required fields
        required = ['code', 'discount_type', 'discount_value']
        for field in required:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Create coupon
        coupon = Coupon(
            code=data['code'].upper(),
            description=data.get('description', ''),
            discount_type=data['discount_type'],
            discount_value=Decimal(str(data['discount_value'])),
            min_order_amount=Decimal(str(data.get('min_order_amount', 0))),
            max_discount=Decimal(str(data['max_discount'])) if 'max_discount' in data else None,
            usage_limit=data.get('usage_limit'),
            is_active=data.get('is_active', True),
            valid_from=datetime.fromisoformat(data['valid_from']) if 'valid_from' in data else datetime.utcnow(),
            valid_until=datetime.fromisoformat(data['valid_until']) if 'valid_until' in data else None
        )

        db.session.add(coupon)
        db.session.commit()

        return jsonify({
            'message': 'Coupon created successfully',
            'coupon': coupon.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/<int:coupon_id>', methods=['PUT'])
@admin_required
def update_coupon(coupon_id):
    """Update a coupon (admin only)"""
    try:
        coupon = Coupon.query.get(coupon_id)
        if not coupon:
            return jsonify({'error': 'Coupon not found'}), 404

        data = request.get_json()

        if 'description' in data:
            coupon.description = data['description']
        if 'is_active' in data:
            coupon.is_active = data['is_active']
        if 'usage_limit' in data:
            coupon.usage_limit = data['usage_limit']
        if 'valid_until' in data:
            coupon.valid_until = datetime.fromisoformat(data['valid_until']) if data['valid_until'] else None

        db.session.commit()

        return jsonify({
            'message': 'Coupon updated successfully',
            'coupon': coupon.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/<int:coupon_id>', methods=['DELETE'])
@admin_required
def delete_coupon(coupon_id):
    """Delete a coupon (admin only)"""
    try:
        coupon = Coupon.query.get(coupon_id)
        if not coupon:
            return jsonify({'error': 'Coupon not found'}), 404

        db.session.delete(coupon)
        db.session.commit()

        return jsonify({'message': 'Coupon deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
