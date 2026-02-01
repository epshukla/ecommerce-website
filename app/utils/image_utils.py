import os
from PIL import Image
from werkzeug.utils import secure_filename
from app.config.upload_config import (
    allowed_file,
    get_unique_filename,
    PRODUCT_UPLOAD_FOLDER,
    MAX_IMAGE_WIDTH,
    MAX_IMAGE_HEIGHT,
    MAX_FILE_SIZE
)

def optimize_image(image_path, max_width=MAX_IMAGE_WIDTH, max_height=MAX_IMAGE_HEIGHT):
    """
    Optimize image by resizing and compressing

    Args:
        image_path: Path to the image file
        max_width: Maximum width for the image
        max_height: Maximum height for the image
    """
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Resize if image is larger than max dimensions
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Save optimized image
            img.save(image_path, 'JPEG', quality=85, optimize=True)

        return True
    except Exception as e:
        print(f"Error optimizing image: {str(e)}")
        return False

def save_product_image(file):
    """
    Save and optimize product image

    Args:
        file: FileStorage object from request.files

    Returns:
        tuple: (success: bool, message: str, filename: str or None)
    """
    # Validate file
    if not file:
        return False, 'No file provided', None

    if file.filename == '':
        return False, 'No file selected', None

    if not allowed_file(file.filename):
        return False, 'Invalid file type. Allowed types: png, jpg, jpeg, gif, webp', None

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return False, f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB', None

    # Generate unique filename
    filename = get_unique_filename(file.filename)
    filepath = os.path.join(PRODUCT_UPLOAD_FOLDER, filename)

    try:
        # Save file
        file.save(filepath)

        # Optimize image
        optimize_image(filepath)

        return True, 'Image uploaded successfully', filename
    except Exception as e:
        # Clean up file if error occurs
        if os.path.exists(filepath):
            os.remove(filepath)
        return False, f'Error saving image: {str(e)}', None

def delete_product_image(filename):
    """
    Delete product image from filesystem

    Args:
        filename: Name of the file to delete

    Returns:
        bool: True if deleted successfully, False otherwise
    """
    if not filename:
        return False

    filepath = os.path.join(PRODUCT_UPLOAD_FOLDER, filename)

    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return False

def get_image_url(filename):
    """
    Get the URL for accessing an image

    Args:
        filename: Name of the image file

    Returns:
        str: URL path to the image
    """
    if not filename:
        return None

    return f"/uploads/products/{filename}"
