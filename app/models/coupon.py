from datetime import datetime
from app import db


class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    discount_type = db.Column(db.String(20), nullable=False)  # 'percentage' or 'fixed'
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    min_order_amount = db.Column(db.Numeric(10, 2), default=0)
    max_discount = db.Column(db.Numeric(10, 2))  # For percentage discounts
    usage_limit = db.Column(db.Integer)  # Null = unlimited
    used_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self):
        """Check if coupon is currently valid"""
        now = datetime.utcnow()

        # Check if active
        if not self.is_active:
            return False, "Coupon is inactive"

        # Check date validity
        if self.valid_from and now < self.valid_from:
            return False, "Coupon not yet valid"

        if self.valid_until and now > self.valid_until:
            return False, "Coupon has expired"

        # Check usage limit
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached"

        return True, "Coupon is valid"

    def calculate_discount(self, order_amount):
        """Calculate discount amount for given order amount"""
        # Check minimum order amount
        if order_amount < float(self.min_order_amount):
            return 0, f"Minimum order amount ${self.min_order_amount} required"

        if self.discount_type == 'percentage':
            discount = float(order_amount) * (float(self.discount_value) / 100)

            # Apply max discount cap if set
            if self.max_discount and discount > float(self.max_discount):
                discount = float(self.max_discount)

            return discount, "Discount applied"

        elif self.discount_type == 'fixed':
            return float(self.discount_value), "Discount applied"

        return 0, "Invalid discount type"

    def to_dict(self):
        """Convert coupon to dictionary"""
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value),
            'min_order_amount': float(self.min_order_amount),
            'max_discount': float(self.max_discount) if self.max_discount else None,
            'usage_limit': self.usage_limit,
            'used_count': self.used_count,
            'is_active': self.is_active,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Coupon {self.code}>'
