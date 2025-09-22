# Lambda Execution Role
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# Lambda Basic Execution Policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_execution_role.name
}

# Lambda DynamoDB and S3 Policy
resource "aws_iam_policy" "lambda_dynamodb_s3_policy" {
  name = "${var.project_name}-lambda-dynamodb-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem"
        ]
        Resource = [
          aws_dynamodb_table.orders.arn,
          "${aws_dynamodb_table.orders.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GeneratePresignedPost"
        ]
        Resource = "${aws_s3_bucket.invoices.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.invoices.arn
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_s3" {
  policy_arn = aws_iam_policy.lambda_dynamodb_s3_policy.arn
  role       = aws_iam_role.lambda_execution_role.name
}

# Lambda Function - Orders CRUD
resource "aws_lambda_function" "orders_crud" {
  filename         = "lambda/orders_crud.zip"
  function_name    = "${var.project_name}-orders-crud"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.orders_crud_zip.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = 30

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.orders.name
      S3_BUCKET      = aws_s3_bucket.invoices.bucket
    }
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-orders-crud-lambda"
  })
}

# Lambda Function - PDF Invoice Generator
resource "aws_lambda_function" "pdf_generator" {
  filename         = "lambda/pdf_generator.zip"
  function_name    = "${var.project_name}-pdf-generator"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.pdf_generator_zip.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = 60

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.invoices.bucket
    }
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-pdf-generator-lambda"
  })
}

# Lambda Provisioned Concurrency (for peak hours)
resource "aws_lambda_provisioned_concurrency_config" "orders_crud_provisioned" {
  function_name                     = aws_lambda_function.orders_crud.function_name
  provisioned_concurrent_executions = 2
  qualifier                         = aws_lambda_function.orders_crud.version
}

# CloudWatch Event Rule for Lambda Provisioned Concurrency (Peak hours)
resource "aws_cloudwatch_event_rule" "lambda_peak_hours" {
  name        = "${var.project_name}-lambda-peak-hours"
  description = "Trigger Lambda provisioned concurrency during peak hours"
  
  schedule_expression = "cron(0 9-17 * * MON-FRI *)"  # 9 AM to 5 PM, Monday to Friday

  tags = local.common_tags
}

# CloudWatch Alarms for Lambda
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project_name}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors Lambda errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.orders_crud.function_name
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "${var.project_name}-lambda-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors Lambda throttles"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.orders_crud.function_name
  }

  tags = local.common_tags
}