import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add lambda directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lambda/pdf_generator'))

from lambda_function import lambda_handler, get_order_data, generate_pdf_content

class TestPDFGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_order = {
            'orderId': 'ORD-12345678',
            'createdAt': '2025-01-18T10:30:00Z',
            'customerName': 'Juan Pérez',
            'customerEmail': 'juan@example.com',
            'items': ['Laptop', 'Mouse'],
            'amount': 299.99,
            'status': 'completed'
        }
        
    @patch('lambda_function.table')
    def test_get_order_data_success(self, mock_table):
        """Test successful order data retrieval"""
        # Arrange
        mock_table.query.return_value = {'Items': [self.sample_order]}
        
        # Act
        result = get_order_data('ORD-12345678')
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['orderId'], 'ORD-12345678')
        
    @patch('lambda_function.table')
    def test_get_order_data_not_found(self, mock_table):
        """Test order data not found"""
        # Arrange
        mock_table.query.return_value = {'Items': []}
        
        # Act
        result = get_order_data('ORD-NOTFOUND')
        
        # Assert
        self.assertIsNone(result)
        
    def test_generate_pdf_content(self):
        """Test PDF content generation"""
        # Act
        pdf_content = generate_pdf_content(self.sample_order)
        
        # Assert
        self.assertIsInstance(pdf_content, bytes)
        content_str = pdf_content.decode('utf-8')
        self.assertIn('ORD-12345678', content_str)
        self.assertIn('Juan Pérez', content_str)
        self.assertIn('$299.99', content_str)
        
    @patch('lambda_function.s3')
    @patch('lambda_function.get_order_data')
    def test_lambda_handler_success(self, mock_get_order, mock_s3):
        """Test successful PDF generation via Lambda handler"""
        # Arrange
        event = {
            'pathParameters': {'orderId': 'ORD-12345678'}
        }
        context = {}
        mock_get_order.return_value = self.sample_order
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = 'https://example.com/pdf'
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        self.assertEqual(result['statusCode'], 200)
        response_body = json.loads(result['body'])
        self.assertEqual(response_body['orderId'], 'ORD-12345678')
        self.assertIn('pdfUrl', response_body)
        
    def test_lambda_handler_missing_order_id(self):
        """Test Lambda handler with missing order ID"""
        # Arrange
        event = {'pathParameters': {}}
        context = {}
        
        # Act
        result = lambda_handler(event, context)
        
        # Assert
        self.assertEqual(result['statusCode'], 400)
        response_body = json.loads(result['body'])
        self.assertEqual(response_body['error'], 'Order ID is required')

if __name__ == '__main__':
    unittest.main()