import json
import jwt
import os
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

def lambda_handler(event, context):
    """
    Custom JWT Authorizer for API Gateway
    Validates JWT tokens and returns IAM policy
    """
    try:
        # Extract token from Authorization header
        token = extract_token(event)
        
        if not token:
            raise Exception('Unauthorized')
        
        # Validate JWT token
        payload = validate_jwt_token(token)
        
        # Generate IAM policy
        policy = generate_policy(payload['sub'], 'Allow', event['methodArn'])
        
        # Add user context
        policy['context'] = {
            'userId': payload['sub'],
            'email': payload.get('email', ''),
            'username': payload.get('username', '')
        }
        
        return policy
        
    except Exception as e:
        print(f"Authorization failed: {str(e)}")
        # Return deny policy
        return generate_policy('user', 'Deny', event['methodArn'])

def extract_token(event):
    """Extract JWT token from Authorization header"""
    try:
        auth_header = event['headers'].get('Authorization') or event['headers'].get('authorization')
        if not auth_header:
            return None
        
        # Remove 'Bearer ' prefix
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        return auth_header
    except:
        return None

def validate_jwt_token(token):
    """Validate JWT token"""
    try:
        # In production, you would:
        # 1. Get the public key from Cognito JWKS endpoint
        # 2. Verify the token signature
        # 3. Check token expiration
        # 4. Validate issuer and audience
        
        # For demo purposes, we'll decode without verification
        # DO NOT use this in production!
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Basic validation
        if 'sub' not in payload:
            raise InvalidTokenError('Missing subject')
        
        return payload
        
    except ExpiredSignatureError:
        raise Exception('Token expired')
    except InvalidTokenError as e:
        raise Exception(f'Invalid token: {str(e)}')
    except Exception as e:
        raise Exception(f'Token validation failed: {str(e)}')

def generate_policy(principal_id, effect, resource):
    """Generate IAM policy for API Gateway"""
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }
    
    return policy