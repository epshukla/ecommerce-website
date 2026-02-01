from flask import Blueprint, send_from_directory, jsonify, request
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.config.upload_config import PRODUCT_UPLOAD_FOLDER
from app.utils.image_utils import save_product_image, delete_product_image
import os

bp = Blueprint('uploads', __name__, url_prefix='/uploads')

@bp.route('/products/<filename>')
def serve_product_image(filename):
    """Serve product images"""
    return send_from_directory(PRODUCT_UPLOAD_FOLDER, filename)

@bp.route('/products/upload', methods=['POST'])
@jwt_required()
def upload_product_image():
    """Upload a product image (admin only)"""
    # Get current user
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    # Check if file is in request
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    # Save and optimize image
    success, message, filename = save_product_image(file)

    if success:
        return jsonify({
            'message': message,
            'filename': filename,
            'url': f'/uploads/products/{filename}'
        }), 201
    else:
        return jsonify({'error': message}), 400

@bp.route('/products/delete/<filename>', methods=['DELETE'])
@jwt_required()
def delete_image(filename):
    """Delete a product image (admin only)"""
    # Get current user
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    # Delete image
    if delete_product_image(filename):
        return jsonify({'message': 'Image deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete image'}), 400
