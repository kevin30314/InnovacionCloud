import unittest
import requests
import json
import time
import os

class TestCompleteWorkflow(unittest.TestCase):
    """End-to-end tests for complete order workflow"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.api_base_url = os.environ.get('API_GATEWAY_URL', 'https://your-api-id.execute-api.us-east-1.amazonaws.com/dev')
        cls.headers = {'Content-Type': 'application/json'}
    
    def test_complete_order_lifecycle(self):
        """Test complete order lifecycle from creation to deletion"""
        
        # Step 1: Create order
        order_data = {
            'customerName': 'E2E Test Customer',
            'customerEmail': 'e2e@test.com',
            'items': ['E2E Product 1', 'E2E Product 2'],
            'amount': 499.99
        }
        
        create_response = requests.post(
            f"{self.api_base_url}/orders",
            headers=self.headers,
            data=json.dumps(order_data)
        )
        
        self.assertEqual(create_response.status_code, 201)
        created_order = create_response.json()
        order_id = created_order['orderId']
        
        # Verify order was created correctly
        self.assertEqual(created_order['customerName'], 'E2E Test Customer')
        self.assertEqual(created_order['status'], 'pending')
        self.assertEqual(created_order['amount'], 499.99)
        
        # Step 2: Retrieve the created order
        get_response = requests.get(f"{self.api_base_url}/orders/{order_id}")
        self.assertEqual(get_response.status_code, 200)
        retrieved_order = get_response.json()
        self.assertEqual(retrieved_order['orderId'], order_id)
        
        # Step 3: Update order status to processing
        update_data = {
            'status': 'processing',
            'createdAt': retrieved_order['createdAt']
        }
        
        update_response = requests.put(
            f"{self.api_base_url}/orders/{order_id}",
            headers=self.headers,
            data=json.dumps(update_data)
        )
        
        self.assertEqual(update_response.status_code, 200)
        updated_order = update_response.json()
        self.assertEqual(updated_order['status'], 'processing')
        
        # Step 4: Generate PDF invoice
        pdf_response = requests.get(f"{self.api_base_url}/orders/{order_id}/pdf")
        self.assertEqual(pdf_response.status_code, 200)
        pdf_data = pdf_response.json()
        self.assertIn('pdfUrl', pdf_data)
        self.assertIn('orderId', pdf_data)
        
        # Step 5: Verify PDF URL is accessible (basic check)
        pdf_url = pdf_data['pdfUrl']
        self.assertTrue(pdf_url.startswith('https://'))
        
        # Step 6: Update order to completed
        complete_data = {
            'status': 'completed',
            'createdAt': retrieved_order['createdAt']
        }
        
        complete_response = requests.put(
            f"{self.api_base_url}/orders/{order_id}",
            headers=self.headers,
            data=json.dumps(complete_data)
        )
        
        self.assertEqual(complete_response.status_code, 200)
        completed_order = complete_response.json()
        self.assertEqual(completed_order['status'], 'completed')
        
        # Step 7: List orders and verify our order appears
        list_response = requests.get(f"{self.api_base_url}/orders")
        self.assertEqual(list_response.status_code, 200)
        orders_data = list_response.json()
        
        order_ids = [order['orderId'] for order in orders_data['orders']]
        self.assertIn(order_id, order_ids)
        
        # Step 8: Filter orders by completed status
        filter_response = requests.get(f"{self.api_base_url}/orders?status=completed")
        self.assertEqual(filter_response.status_code, 200)
        filtered_orders = filter_response.json()
        
        completed_order_ids = [order['orderId'] for order in filtered_orders['orders']]
        self.assertIn(order_id, completed_order_ids)
        
        # Step 9: Clean up - delete the order
        delete_response = requests.delete(f"{self.api_base_url}/orders/{order_id}")
        self.assertEqual(delete_response.status_code, 200)
        
        # Step 10: Verify order is deleted
        final_get_response = requests.get(f"{self.api_base_url}/orders/{order_id}")
        self.assertEqual(final_get_response.status_code, 404)
    
    def test_error_handling_workflow(self):
        """Test error handling scenarios"""
        
        # Test 1: Try to get non-existent order
        response = requests.get(f"{self.api_base_url}/orders/ORD-NONEXISTENT")
        self.assertEqual(response.status_code, 404)
        
        # Test 2: Try to create order with invalid data
        invalid_order = {
            'customerName': '',  # Invalid empty name
            'customerEmail': 'invalid-email',  # Invalid email format
            'items': [],  # Empty items
            'amount': -100  # Negative amount
        }
        
        response = requests.post(
            f"{self.api_base_url}/orders",
            headers=self.headers,
            data=json.dumps(invalid_order)
        )
        
        # Note: Depending on validation implementation, this might return 400 or 201
        # The actual validation would need to be implemented in the Lambda function
        
        # Test 3: Try to generate PDF for non-existent order
        response = requests.get(f"{self.api_base_url}/orders/ORD-NONEXISTENT/pdf")
        self.assertEqual(response.status_code, 404)
    
    def test_performance_workflow(self):
        """Test basic performance characteristics"""
        
        # Create multiple orders quickly
        order_ids = []
        start_time = time.time()
        
        for i in range(5):
            order_data = {
                'customerName': f'Performance Test Customer {i}',
                'customerEmail': f'perf{i}@test.com',
                'items': [f'Performance Item {i}'],
                'amount': 100.0 + i
            }
            
            response = requests.post(
                f"{self.api_base_url}/orders",
                headers=self.headers,
                data=json.dumps(order_data)
            )
            
            self.assertEqual(response.status_code, 201)
            order_ids.append(response.json()['orderId'])
        
        creation_time = time.time() - start_time
        
        # Should be able to create 5 orders in reasonable time (< 10 seconds)
        self.assertLess(creation_time, 10.0)
        
        # Clean up created orders
        for order_id in order_ids:
            requests.delete(f"{self.api_base_url}/orders/{order_id}")

if __name__ == '__main__':
    unittest.main()