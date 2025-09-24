# Cognito User Pool
resource "aws_cognito_user_pool" "orders_user_pool" {
  name = "${var.project_name}-user-pool"

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # User attributes
  username_attributes = ["email"]
  
  # Auto-verified attributes
  auto_verified_attributes = ["email"]

  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = local.common_tags
}

# Cognito User Pool Client
resource "aws_cognito_user_pool_client" "orders_client" {
  name         = "${var.project_name}-client"
  user_pool_id = aws_cognito_user_pool.orders_user_pool.id

  # Client settings
  generate_secret                      = false
  prevent_user_existence_errors        = "ENABLED"
  enable_token_revocation             = true
  enable_propagate_additional_user_context_data = false

  # Auth flows
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  # Token validity
  access_token_validity  = 60    # 1 hour
  id_token_validity     = 60    # 1 hour
  refresh_token_validity = 30   # 30 days

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  # Supported identity providers
  supported_identity_providers = ["COGNITO"]

  # OAuth settings
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  
  callback_urls = [
    "http://localhost:3000/callback",
    "https://${var.project_name}.example.com/callback"
  ]
  
  logout_urls = [
    "http://localhost:3000/logout",
    "https://${var.project_name}.example.com/logout"
  ]
}

# Cognito User Pool Domain
resource "aws_cognito_user_pool_domain" "orders_domain" {
  domain       = "${var.project_name}-auth-${random_id.bucket_suffix.hex}"
  user_pool_id = aws_cognito_user_pool.orders_user_pool.id
}

# Lambda function for Cognito Authorizer
resource "aws_lambda_function" "cognito_authorizer" {
  filename         = "lambda/cognito_authorizer.zip"
  function_name    = "${var.project_name}-cognito-authorizer"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.cognito_authorizer_zip.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = 30

  environment {
    variables = {
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.orders_user_pool.id
      COGNITO_CLIENT_ID    = aws_cognito_user_pool_client.orders_client.id
    }
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-cognito-authorizer-lambda"
  })
}

# API Gateway Authorizer
resource "aws_api_gateway_authorizer" "cognito_authorizer" {
  name                   = "${var.project_name}-cognito-authorizer"
  rest_api_id           = aws_api_gateway_rest_api.orders_api.id
  authorizer_uri        = aws_lambda_function.cognito_authorizer.invoke_arn
  authorizer_credentials = aws_iam_role.api_gateway_authorizer_role.arn
  type                  = "TOKEN"
  identity_source       = "method.request.header.Authorization"
  authorizer_result_ttl_in_seconds = 300
}

# IAM Role for API Gateway to invoke authorizer Lambda
resource "aws_iam_role" "api_gateway_authorizer_role" {
  name = "${var.project_name}-api-gateway-authorizer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# IAM Policy for API Gateway to invoke Lambda
resource "aws_iam_policy" "api_gateway_lambda_invoke" {
  name = "${var.project_name}-api-gateway-lambda-invoke"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "lambda:InvokeFunction"
        Resource = aws_lambda_function.cognito_authorizer.arn
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "api_gateway_lambda_invoke" {
  policy_arn = aws_iam_policy.api_gateway_lambda_invoke.arn
  role       = aws_iam_role.api_gateway_authorizer_role.name
}

# Lambda permission for API Gateway to invoke authorizer
resource "aws_lambda_permission" "api_gateway_authorizer" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cognito_authorizer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.orders_api.execution_arn}/authorizers/${aws_api_gateway_authorizer.cognito_authorizer.id}"
}