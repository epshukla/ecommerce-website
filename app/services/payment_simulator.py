"""Payment Gateway Simulator Service"""
import random
import string
import time
from datetime import datetime
from threading import Thread


class PaymentSimulator:
    """
    Simulates a third-party payment gateway
    Medium complexity with delayed processing and webhooks
    """

    # Test card numbers and their behaviors
    TEST_CARDS = {
        '4242424242424242': {'status': 'completed', 'message': 'Payment successful'},
        '4000000000000002': {'status': 'failed', 'message': 'Card declined'},
        '4000000000009995': {'status': 'failed', 'message': 'Insufficient funds'},
        '4000000000000069': {'status': 'failed', 'message': 'Expired card'},
        '4000000000000119': {'status': 'failed', 'message': 'Processing error'},
        '4000000000003220': {'status': 'processing', 'message': '3D Secure authentication required'},
    }

    # Supported payment methods
    PAYMENT_METHODS = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']

    @staticmethod
    def generate_transaction_id():
        """Generate unique transaction ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f'TXN-{timestamp}-{random_str}'

    @staticmethod
    def validate_card_number(card_number):
        """Basic card number validation"""
        # Remove spaces and dashes
        card_number = card_number.replace(' ', '').replace('-', '')

        # Check if it's digits only
        if not card_number.isdigit():
            return False, 'Card number must contain only digits'

        # Check length (13-19 digits)
        if len(card_number) < 13 or len(card_number) > 19:
            return False, 'Invalid card number length'

        return True, 'Valid'

    @staticmethod
    def validate_cvv(cvv):
        """Validate CVV"""
        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            return False, 'Invalid CVV'
        return True, 'Valid'

    @staticmethod
    def validate_expiry(expiry_month, expiry_year):
        """Validate card expiry date"""
        try:
            month = int(expiry_month)
            year = int(expiry_year)

            if month < 1 or month > 12:
                return False, 'Invalid month'

            # Handle 2-digit year
            if year < 100:
                year += 2000

            current_year = datetime.utcnow().year
            current_month = datetime.utcnow().month

            if year < current_year or (year == current_year and month < current_month):
                return False, 'Card expired'

            return True, 'Valid'
        except ValueError:
            return False, 'Invalid expiry date format'

    @classmethod
    def initiate_payment(cls, amount, payment_method, card_details=None):
        """
        Initiate payment processing
        Returns: (transaction_id, initial_status, message)
        """
        # Validate payment method
        if payment_method not in cls.PAYMENT_METHODS:
            return None, 'failed', f'Invalid payment method. Supported: {", ".join(cls.PAYMENT_METHODS)}'

        # Validate amount
        if amount <= 0:
            return None, 'failed', 'Invalid amount'

        # For card payments, validate card details
        if payment_method in ['credit_card', 'debit_card']:
            if not card_details:
                return None, 'failed', 'Card details required'

            # Validate card number
            is_valid, message = cls.validate_card_number(card_details.get('card_number', ''))
            if not is_valid:
                return None, 'failed', message

            # Validate CVV
            is_valid, message = cls.validate_cvv(card_details.get('cvv', ''))
            if not is_valid:
                return None, 'failed', message

            # Validate expiry
            is_valid, message = cls.validate_expiry(
                card_details.get('expiry_month', ''),
                card_details.get('expiry_year', '')
            )
            if not is_valid:
                return None, 'failed', message

        # Generate transaction ID
        transaction_id = cls.generate_transaction_id()

        # Initial status is always 'processing' for medium complexity
        return transaction_id, 'processing', 'Payment initiated successfully'

    @classmethod
    def process_payment(cls, transaction_id, amount, payment_method, card_details=None):
        """
        Process payment (simulates actual payment processing)
        This determines the final status based on test cards or payment method
        Returns: (final_status, message)
        """
        # Simulate processing delay (1-3 seconds)
        processing_time = random.uniform(1, 3)
        time.sleep(processing_time)

        # For card payments, check test card number
        if payment_method in ['credit_card', 'debit_card'] and card_details:
            card_number = card_details.get('card_number', '').replace(' ', '').replace('-', '')

            # Check if it's a test card
            if card_number in cls.TEST_CARDS:
                result = cls.TEST_CARDS[card_number]
                return result['status'], result['message']

            # For non-test cards, simulate 90% success rate
            if random.random() < 0.9:
                return 'completed', 'Payment successful'
            else:
                failure_reasons = [
                    'Card declined by issuer',
                    'Transaction limit exceeded',
                    'Suspicious activity detected'
                ]
                return 'failed', random.choice(failure_reasons)

        # For PayPal, simulate 95% success rate
        elif payment_method == 'paypal':
            if random.random() < 0.95:
                return 'completed', 'PayPal payment successful'
            else:
                return 'failed', 'PayPal authentication failed'

        # For bank transfer, always mark as pending (requires manual verification)
        elif payment_method == 'bank_transfer':
            return 'pending', 'Bank transfer initiated. Awaiting confirmation.'

        # Default success
        return 'completed', 'Payment successful'

    @classmethod
    def simulate_webhook_callback(cls, payment_id, callback_url, payment_obj, db):
        """
        Simulate async webhook callback after payment processing
        Runs in background thread
        """
        def webhook_task():
            from app.models import Order

            # Process the payment
            final_status, message = cls.process_payment(
                payment_obj.transaction_id,
                float(payment_obj.amount),
                payment_obj.payment_method,
                {}  # Card details not stored for security
            )

            # Update payment status
            payment_obj.status = final_status

            # Update order payment status
            order = Order.query.get(payment_obj.order_id)
            if order:
                order.payment_status = final_status
                if final_status == 'completed':
                    order.status = 'processing'  # Move order to processing
                elif final_status == 'failed':
                    order.status = 'cancelled'
                    # Restore stock on failed payment
                    for item in order.items:
                        item.product.stock_quantity += item.quantity

            db.session.commit()

        # Start background thread for async processing
        thread = Thread(target=webhook_task)
        thread.daemon = True
        thread.start()

    @classmethod
    def check_payment_status(cls, transaction_id):
        """
        Check current payment status
        In real gateway, this would query the payment provider's API
        """
        # In our simulation, this is handled by the database
        # Just return a success response
        return True, 'Status check successful'

    @classmethod
    def simulate_refund(cls, transaction_id, amount):
        """
        Simulate payment refund
        Returns: (refund_transaction_id, status, message)
        """
        # Generate refund transaction ID
        refund_txn_id = cls.generate_transaction_id().replace('TXN', 'RFD')

        # Simulate 95% refund success rate
        if random.random() < 0.95:
            return refund_txn_id, 'completed', 'Refund processed successfully'
        else:
            return None, 'failed', 'Refund processing failed. Contact support.'
