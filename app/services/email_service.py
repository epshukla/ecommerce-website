"""Email notification service (simulation)"""
from datetime import datetime


class EmailService:
    """
    Email service for sending notifications
    In production, this would integrate with services like SendGrid, Mailgun, or AWS SES
    For now, it simulates email sending and logs to console
    """

    @staticmethod
    def send_email(to_email, subject, body, html_body=None):
        """
        Send email (simulated)

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: HTML formatted body (optional)

        Returns:
            (success: bool, message: str)
        """
        print(f"\n{'='*60}")
        print(f"📧 EMAIL SENT")
        print(f"{'='*60}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nBody:\n{body}")
        if html_body:
            print(f"\nHTML Body:\n{html_body}")
        print(f"{'='*60}\n")

        return True, "Email sent successfully (simulated)"

    @staticmethod
    def send_order_confirmation(user_email, order):
        """Send order confirmation email"""
        subject = f"Order Confirmation - Order #{order.id}"

        body = f"""
Dear Customer,

Thank you for your order!

Order Details:
- Order ID: #{order.id}
- Total Amount: ${order.total_amount}
- Status: {order.status}
- Payment Status: {order.payment_status}

Items:
"""
        for item in order.items:
            body += f"- {item.product.name} x {item.quantity} = ${item.subtotal}\n"

        body += f"""
We'll send you another email when your order ships.

Thank you for shopping with us!

Best regards,
E-Commerce Team
"""

        return EmailService.send_email(user_email, subject, body)

    @staticmethod
    def send_order_shipped(user_email, order):
        """Send order shipped notification"""
        subject = f"Order Shipped - Order #{order.id}"

        body = f"""
Dear Customer,

Great news! Your order has been shipped.

Order ID: #{order.id}
Total: ${order.total_amount}

Your order is on its way and should arrive soon.

Track your order in your account dashboard.

Best regards,
E-Commerce Team
"""

        return EmailService.send_email(user_email, subject, body)

    @staticmethod
    def send_order_delivered(user_email, order):
        """Send order delivered notification"""
        subject = f"Order Delivered - Order #{order.id}"

        body = f"""
Dear Customer,

Your order has been delivered!

Order ID: #{order.id}
Total: ${order.total_amount}

We hope you enjoy your purchase. Please leave a review if you're satisfied!

Best regards,
E-Commerce Team
"""

        return EmailService.send_email(user_email, subject, body)

    @staticmethod
    def send_password_reset(user_email, reset_token):
        """Send password reset email"""
        subject = "Password Reset Request"

        body = f"""
Dear Customer,

We received a request to reset your password.

Reset Token: {reset_token}

If you didn't request this, please ignore this email.

This link will expire in 1 hour.

Best regards,
E-Commerce Team
"""

        return EmailService.send_email(user_email, subject, body)

    @staticmethod
    def send_welcome_email(user_email, user_name):
        """Send welcome email to new users"""
        subject = "Welcome to Our E-Commerce Store!"

        body = f"""
Dear {user_name},

Welcome to our e-commerce platform!

Thank you for creating an account. We're excited to have you as part of our community.

Start shopping now and enjoy:
- Free shipping on orders over $50
- Exclusive deals for members
- Easy returns and exchanges

Happy shopping!

Best regards,
E-Commerce Team
"""

        return EmailService.send_email(user_email, subject, body)

    @staticmethod
    def send_low_stock_alert(admin_email, product):
        """Send low stock alert to admin"""
        subject = f"Low Stock Alert - {product.name}"

        body = f"""
Low Stock Alert!

Product: {product.name}
Product ID: {product.id}
Current Stock: {product.stock_quantity}

Please restock this product soon.

Best regards,
Inventory Management System
"""

        return EmailService.send_email(admin_email, subject, body)
