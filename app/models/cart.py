from datetime import datetime
from app import db


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)

    @property
    def subtotal(self):
        """Calculate cart subtotal"""
        return sum(item.product.price * item.quantity for item in self.items)

    def to_dict(self):
        """Convert cart object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_items': self.total_items,
            'subtotal': float(self.subtotal),
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Cart {self.id} - User: {self.user_id}>'


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    # Unique constraint to prevent duplicate products in the same cart
    __table_args__ = (db.UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),)

    @property
    def subtotal(self):
        """Calculate item subtotal"""
        return self.product.price * self.quantity

    def to_dict(self):
        """Convert cart item object to dictionary"""
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None,
            'quantity': self.quantity,
            'subtotal': float(self.subtotal)
        }

    def __repr__(self):
        return f'<CartItem {self.id} - Product: {self.product_id}, Qty: {self.quantity}>'
