"""Wishlist routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Wishlist, Product

bp = Blueprint('wishlist', __name__, url_prefix='/api/wishlist')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_wishlist():
    """Get user's wishlist"""
    try:
        current_user_id = get_jwt_identity()

        wishlist_items = Wishlist.query.filter_by(user_id=current_user_id).all()

        return jsonify({
            'wishlist': [item.to_dict() for item in wishlist_items],
            'count': len(wishlist_items)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/add/<int:product_id>', methods=['POST'])
@jwt_required()
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    try:
        current_user_id = get_jwt_identity()

        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Check if already in wishlist
        existing = Wishlist.query.filter_by(
            user_id=current_user_id,
            product_id=product_id
        ).first()

        if existing:
            return jsonify({'error': 'Product already in wishlist'}), 409

        # Add to wishlist
        wishlist_item = Wishlist(
            user_id=current_user_id,
            product_id=product_id
        )

        db.session.add(wishlist_item)
        db.session.commit()

        return jsonify({
            'message': 'Product added to wishlist',
            'wishlist_item': wishlist_item.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/remove/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(product_id):
    """Remove product from wishlist"""
    try:
        current_user_id = get_jwt_identity()

        wishlist_item = Wishlist.query.filter_by(
            user_id=current_user_id,
            product_id=product_id
        ).first()

        if not wishlist_item:
            return jsonify({'error': 'Product not in wishlist'}), 404

        db.session.delete(wishlist_item)
        db.session.commit()

        return jsonify({'message': 'Product removed from wishlist'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_wishlist():
    """Clear entire wishlist"""
    try:
        current_user_id = get_jwt_identity()

        Wishlist.query.filter_by(user_id=current_user_id).delete()
        db.session.commit()

        return jsonify({'message': 'Wishlist cleared'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
