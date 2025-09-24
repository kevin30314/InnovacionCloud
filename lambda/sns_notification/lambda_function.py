import json
import boto3
import os
from datetime import datetime, timezone

# Initialize AWS clients
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE')

def lambda_handler(event, context):
    """
    Lambda function to handle SNS notifications for order events
    Triggered by DynamoDB Streams or direct invocation
    """
    try:
        # Process each record in the event
        for record in event.get('Records', []):
            if record.get('eventSource') == 'aws:dynamodb':
                # Handle DynamoDB Stream event
                handle_dynamodb_event(record)
            else:
                # Handle direct invocation
                handle_direct_event(record)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Notifications processed successfully'})
        }
        
    except Exception as e:
        print(f"Error processing notifications: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to process notifications'})
        }

def handle_dynamodb_event(record):
    """Handle DynamoDB Stream event"""
    event_name = record['eventName']
    
    if event_name == 'INSERT':
        # New order created
        order_data = record['dynamodb']['NewImage']
        send_order_created_notification(order_data)
        
    elif event_name == 'MODIFY':
        # Order updated
        old_image = record['dynamodb'].get('OldImage', {})
        new_image = record['dynamodb']['NewImage']
        
        # Check if status changed
        old_status = old_image.get('status', {}).get('S', '')
        new_status = new_image.get('status', {}).get('S', '')
        
        if old_status != new_status:
            send_order_status_notification(new_image, old_status, new_status)

def handle_direct_event(event_data):
    """Handle direct Lambda invocation"""
    event_type = event_data.get('eventType')
    order_data = event_data.get('orderData')
    
    if event_type == 'order_created':
        send_order_created_notification(order_data)
    elif event_type == 'order_updated':
        send_order_status_notification(order_data, 
                                     event_data.get('oldStatus'), 
                                     event_data.get('newStatus'))

def send_order_created_notification(order_data):
    """Send notification for new order"""
    try:
        # Extract order information
        order_id = get_dynamodb_value(order_data, 'orderId')
        customer_name = get_dynamodb_value(order_data, 'customerName')
        amount = get_dynamodb_value(order_data, 'amount')
        
        message = {
            'eventType': 'ORDER_CREATED',
            'orderId': order_id,
            'customerName': customer_name,
            'amount': amount,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'message': f'New order {order_id} created for {customer_name} - ${amount}'
        }
        
        # Send SNS notification
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message),
            Subject=f'New Order Created: {order_id}',
            MessageAttributes={
                'eventType': {
                    'DataType': 'String',
                    'StringValue': 'ORDER_CREATED'
                },
                'orderId': {
                    'DataType': 'String',
                    'StringValue': order_id
                }
            }
        )
        
        print(f"Order created notification sent for {order_id}")
        
    except Exception as e:
        print(f"Failed to send order created notification: {str(e)}")

def send_order_status_notification(order_data, old_status, new_status):
    """Send notification for order status change"""
    try:
        # Extract order information
        order_id = get_dynamodb_value(order_data, 'orderId')
        customer_name = get_dynamodb_value(order_data, 'customerName')
        
        message = {
            'eventType': 'ORDER_STATUS_CHANGED',
            'orderId': order_id,
            'customerName': customer_name,
            'oldStatus': old_status,
            'newStatus': new_status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'message': f'Order {order_id} status changed from {old_status} to {new_status}'
        }
        
        # Send SNS notification
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message),
            Subject=f'Order Status Updated: {order_id}',
            MessageAttributes={
                'eventType': {
                    'DataType': 'String',
                    'StringValue': 'ORDER_STATUS_CHANGED'
                },
                'orderId': {
                    'DataType': 'String',
                    'StringValue': order_id
                },
                'newStatus': {
                    'DataType': 'String',
                    'StringValue': new_status
                }
            }
        )
        
        print(f"Order status notification sent for {order_id}: {old_status} -> {new_status}")
        
    except Exception as e:
        print(f"Failed to send order status notification: {str(e)}")

def get_dynamodb_value(item, key):
    """Extract value from DynamoDB item format"""
    if isinstance(item, dict) and key in item:
        value = item[key]
        if isinstance(value, dict):
            # DynamoDB format
            if 'S' in value:
                return value['S']
            elif 'N' in value:
                return float(value['N'])
            elif 'BOOL' in value:
                return value['BOOL']
        else:
            # Regular format
            return value
    return ''