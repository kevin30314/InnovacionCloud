import unittest
import sys
import os

# Add lambda directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lambda/orders_crud'))

class OrderValidator:
    """Order validation utility class"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_amount(amount):
        """Validate order amount"""
        try:
            amount_float = float(amount)
            return amount_float > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_customer_name(name):
        """Validate customer name"""
        return isinstance(name, str) and len(name.strip()) > 0
    
    @staticmethod
    def validate_items(items):
        """Validate order items"""
        return isinstance(items, list) and len(items) > 0

class TestValidators(unittest.TestCase):
    
    def test_validate_email_valid(self):
        """Test valid email validation"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org'
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(OrderValidator.validate_email(email))
    
    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user@.com',
            ''
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(OrderValidator.validate_email(email))
    
    def test_validate_amount_valid(self):
        """Test valid amount validation"""
        valid_amounts = [1.0, 100, '50.99', 0.01]
        
        for amount in valid_amounts:
            with self.subTest(amount=amount):
                self.assertTrue(OrderValidator.validate_amount(amount))
    
    def test_validate_amount_invalid(self):
        """Test invalid amount validation"""
        invalid_amounts = [0, -1, 'invalid', None, '']
        
        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                self.assertFalse(OrderValidator.validate_amount(amount))
    
    def test_validate_customer_name_valid(self):
        """Test valid customer name validation"""
        valid_names = ['Juan Pérez', 'María García', 'A']
        
        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(OrderValidator.validate_customer_name(name))
    
    def test_validate_customer_name_invalid(self):
        """Test invalid customer name validation"""
        invalid_names = ['', '   ', None, 123]
        
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(OrderValidator.validate_customer_name(name))
    
    def test_validate_items_valid(self):
        """Test valid items validation"""
        valid_items = [['item1'], ['item1', 'item2'], ['Laptop', 'Mouse']]
        
        for items in valid_items:
            with self.subTest(items=items):
                self.assertTrue(OrderValidator.validate_items(items))
    
    def test_validate_items_invalid(self):
        """Test invalid items validation"""
        invalid_items = [[], None, 'not a list', 123]
        
        for items in invalid_items:
            with self.subTest(items=items):
                self.assertFalse(OrderValidator.validate_items(items))

if __name__ == '__main__':
    unittest.main()