from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Cart
from app.utils.validators import validate_email_format, validate_password_strength, validate_required_fields
from datetime import timedelta

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        is_valid, missing_fields = validate_required_fields(data, required_fields)

        if not is_valid:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        # Validate email format
        is_valid_email, email_result = validate_email_format(data['email'])
        if not is_valid_email:
            return jsonify({'error': f'Invalid email: {email_result}'}), 400

        email = email_result

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Validate password strength
        is_valid_password, password_message = validate_password_strength(data['password'])
        if not is_valid_password:
            return jsonify({'error': password_message}), 400

        # Create new user
        user = User(
            email=email,
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'user')  # Default to 'user' role
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create cart for user
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()

        # Create access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'password']
        is_valid, missing_fields = validate_required_fields(data, required_fields)

        if not is_valid:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        # Find user by email
        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Create access tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(
            identity=current_user_id,
            expires_delta=timedelta(hours=24)
        )

        return jsonify({
            'access_token': access_token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ['old_password', 'new_password']
        is_valid, missing_fields = validate_required_fields(data, required_fields)

        if not is_valid:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        # Check old password
        if not user.check_password(data['old_password']):
            return jsonify({'error': 'Incorrect old password'}), 401

        # Validate new password strength
        is_valid_password, password_message = validate_password_strength(data['new_password'])
        if not is_valid_password:
            return jsonify({'error': password_message}), 400

        # Update password
        user.set_password(data['new_password'])
        db.session.commit()

        return jsonify({
            'message': 'Password changed successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    # Note: JWT tokens are stateless, so logout is handled client-side
    # by removing the token from storage. This endpoint is here for
    # consistency and can be extended with token blacklisting if needed.
    return jsonify({
        'message': 'Logout successful. Please remove token from client.'
    }), 200
