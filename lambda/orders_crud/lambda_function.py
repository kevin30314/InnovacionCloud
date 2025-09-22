import json
import boto3
import uuid
from datetime import datetime, timezone
import os

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    """
    Lambda function to handle CRUD operations for orders
    """
    try:
        http_method = event['httpMethod']
        path_parameters = event.get('pathParameters') or {}
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        query_parameters = event.get('queryStringParameters') or {}
        
        if http_method == 'GET':
            if path_parameters.get('orderId'):
                # Get single order
                return get_order(path_parameters['orderId'])
            else:
                # List orders
                return list_orders(query_parameters)
        
        elif http_method == 'POST':
            # Create new order
            return create_order(body)
        
        elif http_method == 'PUT':
            # Update order
            return update_order(path_parameters['orderId'], body)
        
        elif http_method == 'DELETE':
            # Delete order
            return delete_order(path_parameters['orderId'])
        
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }

def get_order(order_id):
    """Get a single order by ID"""
    try:
        response = table.query(
            KeyConditionExpression='orderId = :order_id',
            ExpressionAttributeValues={':order_id': order_id}
        )
        
        if response['Items']:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response['Items'][0], default=str)
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Order not found'})
            }
    
    except Exception as e:
        print(f"Error getting order: {str(e)}")
        raise

def list_orders(query_parameters):
    """List orders with optional filtering"""
    try:
        # Parse query parameters
        status = query_parameters.get('status')
        limit = int(query_parameters.get('limit', 50))
        
        if status:
            # Query by status using GSI
            response = table.query(
                IndexName='StatusIndex',
                KeyConditionExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': status},
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )
        else:
            # Scan all items
            response = table.scan(Limit=limit)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'orders': response['Items'],
                'count': len(response['Items'])
            }, default=str)
        }
    
    except Exception as e:
        print(f"Error listing orders: {str(e)}")
        raise

def create_order(order_data):
    """Create a new order"""
    try:
        # Generate order ID and timestamp
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()
        
        # Prepare order item
        order = {
            'orderId': order_id,
            'createdAt': created_at,
            'customerName': order_data.get('customerName', ''),
            'customerEmail': order_data.get('customerEmail', ''),
            'items': order_data.get('items', []),
            'amount': float(order_data.get('amount', 0)),
            'status': 'pending',
            'updatedAt': created_at
        }
        
        # Put item in DynamoDB
        table.put_item(Item=order)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(order, default=str)
        }
    
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        raise

def update_order(order_id, update_data):
    """Update an existing order"""
    try:
        # Get current timestamp
        updated_at = datetime.now(timezone.utc).isoformat()
        
        # Build update expression
        update_expression = "SET updatedAt = :updated_at"
        expression_attribute_values = {':updated_at': updated_at}
        
        # Add fields to update
        if 'status' in update_data:
            update_expression += ", #status = :status"
            expression_attribute_values[':status'] = update_data['status']
        
        if 'customerName' in update_data:
            update_expression += ", customerName = :customer_name"
            expression_attribute_values[':customer_name'] = update_data['customerName']
        
        if 'amount' in update_data:
            update_expression += ", amount = :amount"
            expression_attribute_values[':amount'] = float(update_data['amount'])
        
        if 'items' in update_data:
            update_expression += ", items = :items"
            expression_attribute_values[':items'] = update_data['items']
        
        # Update item
        response = table.update_item(
            Key={'orderId': order_id, 'createdAt': update_data.get('createdAt', '')},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames={'#status': 'status'} if 'status' in update_data else {},
            ReturnValues='ALL_NEW'
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response['Attributes'], default=str)
        }
    
    except Exception as e:
        print(f"Error updating order: {str(e)}")
        raise

def delete_order(order_id):
    """Delete an order"""
    try:
        # First, get the order to get the sort key
        response = table.query(
            KeyConditionExpression='orderId = :order_id',
            ExpressionAttributeValues={':order_id': order_id}
        )
        
        if not response['Items']:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Order not found'})
            }
        
        order = response['Items'][0]
        
        # Delete the item
        table.delete_item(
            Key={
                'orderId': order_id,
                'createdAt': order['createdAt']
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Order deleted successfully'})
        }
    
    except Exception as e:
        print(f"Error deleting order: {str(e)}")
        raise