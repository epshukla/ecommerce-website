"""Input validation utilities"""
import re
import os
from email_validator import validate_email, EmailNotValidError


def validate_email_format(email):
    """Validate email format"""
    try:
        # In development mode, allow test domains like example.com
        check_deliverability = os.getenv('FLASK_ENV') != 'development'
        valid = validate_email(email, check_deliverability=check_deliverability)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)


def validate_password_strength(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, "Password is valid"


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in the data
    Returns: (is_valid, missing_fields)
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]

    if missing_fields:
        return False, missing_fields

    return True, []
