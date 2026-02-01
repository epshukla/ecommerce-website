import os
from werkzeug.utils import secure_filename

# Base upload directory
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
PRODUCT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'products')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Image configuration
MAX_IMAGE_WIDTH = 2000
MAX_IMAGE_HEIGHT = 2000

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(filename):
    """Generate unique filename using timestamp"""
    import time
    import uuid
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_name = f"{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
    return secure_filename(unique_name)

# Ensure upload directories exist
os.makedirs(PRODUCT_UPLOAD_FOLDER, exist_ok=True)
