import json
import boto3
import uuid
from datetime import datetime, timezone
import os
from botocore.exceptions import ClientError
import base64

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'serverless-orders-orders'))

S3_BUCKET = os.environ['S3_BUCKET']

def lambda_handler(event, context):
    """
    Lambda function to generate PDF invoices and return signed URLs
    """
    try:
        path_parameters = event.get('pathParameters') or {}
        order_id = path_parameters.get('orderId')
        
        if not order_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Order ID is required'})
            }
        
        # Get order data
        order_data = get_order_data(order_id)
        if not order_data:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Order not found'})
            }
        
        # Generate PDF content (mock PDF for demonstration)
        pdf_content = generate_pdf_content(order_data)
        
        # Save PDF to S3
        pdf_key = f"invoices/{order_id}/{uuid.uuid4().hex}.pdf"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=pdf_key,
            Body=pdf_content,
            ContentType='application/pdf',
            Metadata={
                'orderId': order_id,
                'generatedAt': datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Generate presigned URL (valid for 1 hour)
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': pdf_key},
            ExpiresIn=3600
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'PDF generated successfully',
                'orderId': order_id,
                'pdfUrl': presigned_url,
                'expiresAt': (datetime.now(timezone.utc).timestamp() + 3600)
            })
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

def get_order_data(order_id):
    """Get order data from DynamoDB"""
    try:
        response = table.query(
            KeyConditionExpression='orderId = :order_id',
            ExpressionAttributeValues={':order_id': order_id}
        )
        
        if response['Items']:
            return response['Items'][0]
        return None
    
    except Exception as e:
        print(f"Error getting order data: {str(e)}")
        return None

def generate_pdf_content(order_data):
    """
    Generate PDF content for the invoice
    In a real implementation, you would use a PDF library like reportlab
    For demonstration, we'll create a simple text-based PDF
    """
    
    # Mock PDF content as a simple text file (in real scenario use reportlab or similar)
    pdf_content = f"""
PDF Invoice - Order {order_data['orderId']}
=====================================

Date: {order_data['createdAt']}
Customer: {order_data.get('customerName', 'N/A')}
Email: {order_data.get('customerEmail', 'N/A')}

Items:
{chr(10).join(['- ' + item for item in order_data.get('items', [])])}

Total Amount: ${order_data.get('amount', 0):.2f}
Status: {order_data.get('status', 'pending')}

Generated on: {datetime.now(timezone.utc).isoformat()}
    """.strip()
    
    return pdf_content.encode('utf-8')

def create_presigned_post(bucket_name, object_name, expiration=3600):
    """
    Generate a presigned URL S3 POST request to upload a file
    """
    try:
        response = s3.generate_presigned_post(
            Bucket=bucket_name,
            Key=object_name,
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(f"Error creating presigned post: {e}")
        return None

    return response