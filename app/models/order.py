from datetime import datetime
from app import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False)  # pending, processing, shipped, delivered, cancelled
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    payment_status = db.Column(db.String(50), default='pending', nullable=False)  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')
    shipping_address = db.relationship('Address', foreign_keys=[shipping_address_id])

    @property
    def total_items(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items)

    def to_dict(self):
        """Convert order object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'payment_status': self.payment_status,
            'total_items': self.total_items,
            'shipping_address': self.shipping_address.to_dict() if self.shipping_address else None,
            'items': [item.to_dict() for item in self.items],
            'payment': self.payment.to_dict() if self.payment else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Order {self.id} - User: {self.user_id}, Status: {self.status}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)  # Store price at time of purchase

    @property
    def subtotal(self):
        """Calculate item subtotal"""
        return self.price_at_purchase * self.quantity

    def to_dict(self):
        """Convert order item object to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'price_at_purchase': float(self.price_at_purchase),
            'subtotal': float(self.subtotal)
        }

    def __repr__(self):
        return f'<OrderItem {self.id} - Order: {self.order_id}, Product: {self.product_id}>'
