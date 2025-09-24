import unittest
import requests
import json
import os
from datetime import datetime

class TestAPIEndpoints(unittest.TestCase):
    """Integration tests for API Gateway endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with API Gateway URL"""
        # This should be set as environment variable or from Terraform output
        cls.api_base_url = os.environ.get('API_GATEWAY_URL', 'https://your-api-id.execute-api.us-east-1.amazonaws.com/dev')
        cls.headers = {
            'Content-Type': 'application/json'
        }
        cls.test_order_id = None
    
    def test_01_create_order(self):
        """Test creating a new order via API"""
        order_data = {
            'customerName': 'Integration Test User',
            'customerEmail': 'test@integration.com',
            'items': ['Test Item 1', 'Test Item 2'],
            'amount': 199.99
        }
        
        response = requests.post(
            f"{self.api_base_url}/orders",
            headers=self.headers,
            data=json.dumps(order_data)
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('orderId', response_data)
        self.assertEqual(response_data['customerName'], 'Integration Test User')
        self.assertEqual(response_data['status'], 'pending')
        
        # Store order ID for subsequent tests
        TestAPIEndpoints.test_order_id = response_data['orderId']
    
    def test_02_get_order(self):
        """Test retrieving a specific order"""
        if not self.test_order_id:
            self.skipTest("No order ID available from create test")
        
        response = requests.get(f"{self.api_base_url}/orders/{self.test_order_id}")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['orderId'], self.test_order_id)
        self.assertEqual(response_data['customerName'], 'Integration Test User')
    
    def test_03_list_orders(self):
        """Test listing all orders"""
        response = requests.get(f"{self.api_base_url}/orders")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('orders', response_data)
        self.assertIn('count', response_data)
        self.assertIsInstance(response_data['orders'], list)
    
    def test_04_list_orders_with_filter(self):
        """Test listing orders with status filter"""
        response = requests.get(f"{self.api_base_url}/orders?status=pending&limit=10")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('orders', response_data)
        
        # Check that all returned orders have pending status
        for order in response_data['orders']:
            self.assertEqual(order['status'], 'pending')
    
    def test_05_update_order(self):
        """Test updating an order"""
        if not self.test_order_id:
            self.skipTest("No order ID available from create test")
        
        # First get the order to get the createdAt timestamp
        get_response = requests.get(f"{self.api_base_url}/orders/{self.test_order_id}")
        order_data = get_response.json()
        
        update_data = {
            'status': 'completed',
            'createdAt': order_data['createdAt']
        }
        
        response = requests.put(
            f"{self.api_base_url}/orders/{self.test_order_id}",
            headers=self.headers,
            data=json.dumps(update_data)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'completed')
    
    def test_06_generate_pdf(self):
        """Test PDF generation for an order"""
        if not self.test_order_id:
            self.skipTest("No order ID available from create test")
        
        response = requests.get(f"{self.api_base_url}/orders/{self.test_order_id}/pdf")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('pdfUrl', response_data)
        self.assertIn('orderId', response_data)
        self.assertEqual(response_data['orderId'], self.test_order_id)
    
    def test_07_delete_order(self):
        """Test deleting an order"""
        if not self.test_order_id:
            self.skipTest("No order ID available from create test")
        
        response = requests.delete(f"{self.api_base_url}/orders/{self.test_order_id}")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['message'], 'Order deleted successfully')
        
        # Verify order is deleted
        get_response = requests.get(f"{self.api_base_url}/orders/{self.test_order_id}")
        self.assertEqual(get_response.status_code, 404)
    
    def test_get_nonexistent_order(self):
        """Test getting a non-existent order"""
        response = requests.get(f"{self.api_base_url}/orders/ORD-NONEXISTENT")
        
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'Order not found')

if __name__ == '__main__':
    unittest.main()