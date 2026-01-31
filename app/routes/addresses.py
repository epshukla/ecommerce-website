"""Address management routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Address
from app.utils.validators import validate_required_fields

bp = Blueprint('addresses', __name__, url_prefix='/api/addresses')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_addresses():
    """Get all addresses for current user"""
    try:
        current_user_id = get_jwt_identity()

        addresses = Address.query.filter_by(user_id=current_user_id).all()

        return jsonify({
            'addresses': [addr.to_dict() for addr in addresses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_address():
    """Create a new address"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        required = ['address_line1', 'city', 'state', 'postal_code', 'country']
        is_valid, missing = validate_required_fields(data, required)
        if not is_valid:
            return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

        # If setting as default, unset other defaults
        if data.get('is_default', False):
            Address.query.filter_by(user_id=current_user_id, is_default=True).update({'is_default': False})

        address = Address(
            user_id=current_user_id,
            address_line1=data['address_line1'],
            address_line2=data.get('address_line2', ''),
            city=data['city'],
            state=data['state'],
            postal_code=data['postal_code'],
            country=data['country'],
            is_default=data.get('is_default', False)
        )

        db.session.add(address)
        db.session.commit()

        return jsonify({
            'message': 'Address created successfully',
            'address': address.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    """Update an address"""
    try:
        current_user_id = get_jwt_identity()

        address = Address.query.get(address_id)
        if not address or address.user_id != current_user_id:
            return jsonify({'error': 'Address not found'}), 404

        data = request.get_json()

        # If setting as default, unset other defaults
        if data.get('is_default', False):
            Address.query.filter_by(user_id=current_user_id, is_default=True).update({'is_default': False})

        # Update fields
        if 'address_line1' in data:
            address.address_line1 = data['address_line1']
        if 'address_line2' in data:
            address.address_line2 = data['address_line2']
        if 'city' in data:
            address.city = data['city']
        if 'state' in data:
            address.state = data['state']
        if 'postal_code' in data:
            address.postal_code = data['postal_code']
        if 'country' in data:
            address.country = data['country']
        if 'is_default' in data:
            address.is_default = data['is_default']

        db.session.commit()

        return jsonify({
            'message': 'Address updated successfully',
            'address': address.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    """Delete an address"""
    try:
        current_user_id = get_jwt_identity()

        address = Address.query.get(address_id)
        if not address or address.user_id != current_user_id:
            return jsonify({'error': 'Address not found'}), 404

        db.session.delete(address)
        db.session.commit()

        return jsonify({'message': 'Address deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:address_id>/set-default', methods=['POST'])
@jwt_required()
def set_default_address(address_id):
    """Set an address as default"""
    try:
        current_user_id = get_jwt_identity()

        address = Address.query.get(address_id)
        if not address or address.user_id != current_user_id:
            return jsonify({'error': 'Address not found'}), 404

        # Unset other defaults
        Address.query.filter_by(user_id=current_user_id, is_default=True).update({'is_default': False})

        # Set this as default
        address.is_default = True
        db.session.commit()

        return jsonify({
            'message': 'Default address set successfully',
            'address': address.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
