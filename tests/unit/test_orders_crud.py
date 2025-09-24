import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add lambda directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lambda/orders_crud'))

from lambda_function import lambda_handler, get_order, list_orders, create_order, update_order, delete_order

class TestOrdersCRUD(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_table = Mock()
        self.sample_order = {
            'orderId': 'ORD-12345678',
            'createdAt': '2025-01-18T10:30:00Z',
            'customerName': 'Juan Pérez',
            'customerEmail': 'juan@example.com',
            'items': ['Laptop', 'Mouse'],
            'amount': 299.99,
            'status': 'pending'
        }
        
    @patch('lambda_function.table')
    def test_get_order_success(self, mock_table):
        """Test successful order retrieval"""
        # Arrange
        mock_table.query.return_value = {'Items': [self.sample_order]}
        
        # Act
        result = get_order('ORD-12345678')
        
        # Assert
        self.assertEqual(result['statusCode'], 200)
        response_body = json.loads(result['body'])
        self.assertEqual(response_body['orderId'], 'ORD-12345678')
        
    @patch('lambda_function.table')
    def test_get_order_not_found(self, mock_table):
        """Test order not found scenario"""
        # Arrange
        mock_table.query.return_value = {'Items': []}
        
        # Act
        result = get_order('ORD-NOTFOUND')
        
        # Assert
        self.assertEqual(result['statusCode'], 404)
        response_body = json.loads(result['body'])
        self.assertEqual(response_body['error'], 'Order not found')
        
    @patch('lambda_function.table')
    def test_create_order_success(self, mock_table):
        """Test successful order creation"""
        # Arrange
        order_data = {
            'customerName': 'María García',
            'customerEmail': 'maria@example.com',
            'items': ['Smartphone'],
            'amount': 599.99
        }
        mock_table.put_item.return_value = {}
        
        # Act
        result = create_order(order_data)
        
        # Assert
        self.assertEqual(result['statusCode'], 201)
        response_body = json.loads(result['body'])
        self.assertEqual(response_body['customerName'], 'María García')
        self.assertEqual(response_body['status'], 'pending')
        
    @patch('lambda_function.table')
    def test_list_orders_with_status_filter(self, mock_table):
        """Test listing orders with status filter"""
        # Arrange
        mock_table.query.return_value = {'Items': [self.sample_order]}
        query_params = {'status': 'pending', 'limit': '10'}
        
        # Act
        result = list_orders(query_params)
        
        # Assert
        self.assertEqual(result['statusCode'], 200)
        response_body = json.loads(result['body'])
        self.assertEqual(len(response_body['orders']), 1)
        
    @patch('lambda_function.table')
    def test_update_order_success(self, mock_table):
        """Test successful order update"""
        # Arrange
        update_data = {'status': 'completed', 'createdAt': '2025-01-18T10:30:00Z'}
        mock_table.update_item.return_value = {'Attributes': {**self.sample_order, 'status': 'completed'}}
        
        # Act
        result = update_order('ORD-12345678', update_data)
        
        # Assert
        self.assertEqual(result['statusCode'], 200)
        response_body = json.loads(result['body'])
        self.assertEqual(response_body['status'], 'completed')
        
    @patch('lambda_function.table')
    def test_delete_order_success(self, mock_table):
        """Test successful order deletion"""
        # Arrange
        mock_table.query.return_value = {'Items': [self.sample_order]}
        mock_table.delete_item.return_value = {}
        
        # Act
        result = delete_order('ORD-12345678')
        
        # Assert
        self.assertEqual(result['statusCode'], 200)
        response_body = json.loads(result['body'])
        self.assertEqual(response_body['message'], 'Order deleted successfully')
        
    @patch('lambda_function.table')
    def test_delete_order_not_found(self, mock_table):
        """Test delete order when order doesn't exist"""
        # Arrange
        mock_table.query.return_value = {'Items': []}
        
        # Act
        result = delete_order('ORD-NOTFOUND')
        
        # Assert
        self.assertEqual(result['statusCode'], 404)
        response_body = json.loads(result['body'])
        self.assertEqual(response_body['error'], 'Order not found')

if __name__ == '__main__':
    unittest.main()