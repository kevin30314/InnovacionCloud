import unittest
import boto3
import os
from moto import mock_dynamodb
from datetime import datetime, timezone
import uuid

class TestDynamoDBOperations(unittest.TestCase):
    """Integration tests for DynamoDB operations"""
    
    @mock_dynamodb
    def setUp(self):
        """Set up test DynamoDB table"""
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Create test table
        self.table = self.dynamodb.create_table(
            TableName='test-orders',
            KeySchema=[
                {'AttributeName': 'orderId', 'KeyType': 'HASH'},
                {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'orderId', 'AttributeType': 'S'},
                {'AttributeName': 'createdAt', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'StatusIndex',
                    'KeySchema': [
                        {'AttributeName': 'status', 'KeyType': 'HASH'},
                        {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        # Wait for table to be created
        self.table.wait_until_exists()
    
    @mock_dynamodb
    def test_put_and_get_order(self):
        """Test putting and getting an order from DynamoDB"""
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()
        
        order = {
            'orderId': order_id,
            'createdAt': created_at,
            'customerName': 'Test Customer',
            'customerEmail': 'test@example.com',
            'items': ['Item 1', 'Item 2'],
            'amount': 299.99,
            'status': 'pending'
        }
        
        # Put item
        self.table.put_item(Item=order)
        
        # Get item
        response = self.table.query(
            KeyConditionExpression='orderId = :order_id',
            ExpressionAttributeValues={':order_id': order_id}
        )
        
        self.assertEqual(len(response['Items']), 1)
        retrieved_order = response['Items'][0]
        self.assertEqual(retrieved_order['orderId'], order_id)
        self.assertEqual(retrieved_order['customerName'], 'Test Customer')
    
    @mock_dynamodb
    def test_query_by_status(self):
        """Test querying orders by status using GSI"""
        # Create multiple orders with different statuses
        orders = []
        for i, status in enumerate(['pending', 'completed', 'pending']):
            order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            created_at = datetime.now(timezone.utc).isoformat()
            
            order = {
                'orderId': order_id,
                'createdAt': created_at,
                'customerName': f'Customer {i}',
                'customerEmail': f'customer{i}@example.com',
                'items': [f'Item {i}'],
                'amount': 100.0 + i,
                'status': status
            }
            orders.append(order)
            self.table.put_item(Item=order)
        
        # Query for pending orders
        response = self.table.query(
            IndexName='StatusIndex',
            KeyConditionExpression='#status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'pending'}
        )
        
        self.assertEqual(len(response['Items']), 2)
        for item in response['Items']:
            self.assertEqual(item['status'], 'pending')
    
    @mock_dynamodb
    def test_update_order(self):
        """Test updating an order"""
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()
        
        # Create initial order
        order = {
            'orderId': order_id,
            'createdAt': created_at,
            'customerName': 'Test Customer',
            'status': 'pending',
            'amount': 100.0
        }
        self.table.put_item(Item=order)
        
        # Update order
        updated_at = datetime.now(timezone.utc).isoformat()
        response = self.table.update_item(
            Key={'orderId': order_id, 'createdAt': created_at},
            UpdateExpression='SET #status = :status, updatedAt = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'completed',
                ':updated_at': updated_at
            },
            ReturnValues='ALL_NEW'
        )
        
        updated_order = response['Attributes']
        self.assertEqual(updated_order['status'], 'completed')
        self.assertEqual(updated_order['updatedAt'], updated_at)
    
    @mock_dynamodb
    def test_delete_order(self):
        """Test deleting an order"""
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()
        
        # Create order
        order = {
            'orderId': order_id,
            'createdAt': created_at,
            'customerName': 'Test Customer',
            'status': 'pending'
        }
        self.table.put_item(Item=order)
        
        # Verify order exists
        response = self.table.query(
            KeyConditionExpression='orderId = :order_id',
            ExpressionAttributeValues={':order_id': order_id}
        )
        self.assertEqual(len(response['Items']), 1)
        
        # Delete order
        self.table.delete_item(
            Key={'orderId': order_id, 'createdAt': created_at}
        )
        
        # Verify order is deleted
        response = self.table.query(
            KeyConditionExpression='orderId = :order_id',
            ExpressionAttributeValues={':order_id': order_id}
        )
        self.assertEqual(len(response['Items']), 0)

if __name__ == '__main__':
    unittest.main()