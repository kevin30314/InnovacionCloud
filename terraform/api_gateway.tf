# API Gateway REST API
resource "aws_api_gateway_rest_api" "orders_api" {
  name        = "${var.project_name}-api"
  description = "Serverless Orders API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = local.common_tags
}

# API Gateway Resource - Orders
resource "aws_api_gateway_resource" "orders" {
  rest_api_id = aws_api_gateway_rest_api.orders_api.id
  parent_id   = aws_api_gateway_rest_api.orders_api.root_resource_id
  path_part   = "orders"
}

# API Gateway Resource - Order by ID
resource "aws_api_gateway_resource" "order_by_id" {
  rest_api_id = aws_api_gateway_rest_api.orders_api.id
  parent_id   = aws_api_gateway_resource.orders.id
  path_part   = "{orderId}"
}

# API Gateway Resource - PDF
resource "aws_api_gateway_resource" "pdf" {
  rest_api_id = aws_api_gateway_rest_api.orders_api.id
  parent_id   = aws_api_gateway_resource.order_by_id.id
  path_part   = "pdf"
}

# API Gateway Method - GET /orders
resource "aws_api_gateway_method" "get_orders" {
  rest_api_id   = aws_api_gateway_rest_api.orders_api.id
  resource_id   = aws_api_gateway_resource.orders.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

# API Gateway Method - POST /orders
resource "aws_api_gateway_method" "post_orders" {
  rest_api_id   = aws_api_gateway_rest_api.orders_api.id
  resource_id   = aws_api_gateway_resource.orders.id
  http_method   = "POST"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

# API Gateway Method - GET /orders/{orderId}
resource "aws_api_gateway_method" "get_order_by_id" {
  rest_api_id   = aws_api_gateway_rest_api.orders_api.id
  resource_id   = aws_api_gateway_resource.order_by_id.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

# API Gateway Method - PUT /orders/{orderId}
resource "aws_api_gateway_method" "put_order_by_id" {
  rest_api_id   = aws_api_gateway_rest_api.orders_api.id
  resource_id   = aws_api_gateway_resource.order_by_id.id
  http_method   = "PUT"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

# API Gateway Method - DELETE /orders/{orderId}
resource "aws_api_gateway_method" "delete_order_by_id" {
  rest_api_id   = aws_api_gateway_rest_api.orders_api.id
  resource_id   = aws_api_gateway_resource.order_by_id.id
  http_method   = "DELETE"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

# API Gateway Method - GET /orders/{orderId}/pdf
resource "aws_api_gateway_method" "get_order_pdf" {
  rest_api_id   = aws_api_gateway_rest_api.orders_api.id
  resource_id   = aws_api_gateway_resource.pdf.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

# API Gateway Request Validator
resource "aws_api_gateway_request_validator" "orders_validator" {
  name                        = "${var.project_name}-request-validator"
  rest_api_id                = aws_api_gateway_rest_api.orders_api.id
  validate_request_body      = true
  validate_request_parameters = true
}

# API Gateway Usage Plan
resource "aws_api_gateway_usage_plan" "orders_usage_plan" {
  name         = "${var.project_name}-usage-plan"
  description  = "Usage plan for orders API"

  api_stages {
    api_id = aws_api_gateway_rest_api.orders_api.id
    stage  = aws_api_gateway_stage.orders_api_stage.stage_name
  }

  quota_settings {
    limit  = 10000
    period = "DAY"
  }

  throttle_settings {
    rate_limit  = 100
    burst_limit = 200
  }

  tags = local.common_tags
}

# Lambda Integrations
resource "aws_api_gateway_integration" "orders_crud_integration" {
  count = 5  # For GET, POST, PUT, DELETE methods

  rest_api_id = aws_api_gateway_rest_api.orders_api.id
  resource_id = count.index < 2 ? aws_api_gateway_resource.orders.id : aws_api_gateway_resource.order_by_id.id
  http_method = [
    aws_api_gateway_method.get_orders.http_method,
    aws_api_gateway_method.post_orders.http_method,
    aws_api_gateway_method.get_order_by_id.http_method,
    aws_api_gateway_method.put_order_by_id.http_method,
    aws_api_gateway_method.delete_order_by_id.http_method
  ][count.index]

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.orders_crud.invoke_arn
}

# PDF Generator Integration
resource "aws_api_gateway_integration" "pdf_generator_integration" {
  rest_api_id = aws_api_gateway_rest_api.orders_api.id
  resource_id = aws_api_gateway_resource.pdf.id
  http_method = aws_api_gateway_method.get_order_pdf.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.pdf_generator.invoke_arn
}

# Lambda Permissions
resource "aws_lambda_permission" "api_gateway_orders_crud" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.orders_crud.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.orders_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_pdf_generator" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pdf_generator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.orders_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "orders_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.orders_crud_integration,
    aws_api_gateway_integration.pdf_generator_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.orders_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.orders.id,
      aws_api_gateway_method.get_orders.id,
      aws_api_gateway_method.post_orders.id,
      aws_api_gateway_integration.orders_crud_integration,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "orders_api_stage" {
  deployment_id = aws_api_gateway_deployment.orders_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.orders_api.id
  stage_name    = var.api_stage_name

  # Enable caching
  cache_cluster_enabled = true
  cache_cluster_size    = "0.5"

  # Method settings for caching
  method_settings {
    method_path = "*/*"
    caching_enabled = true
    cache_ttl_in_seconds = 300
    cache_key_parameters = ["method.request.path.orderId"]
  }

  tags = local.common_tags
}

# API Gateway CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "api_gateway_5xx_errors" {
  alarm_name          = "${var.project_name}-api-gateway-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "60"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors API Gateway 5xx errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ApiName = aws_api_gateway_rest_api.orders_api.name
    Stage   = aws_api_gateway_stage.orders_api_stage.stage_name
  }

  tags = local.common_tags
}