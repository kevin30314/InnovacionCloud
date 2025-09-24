# SNS Topic for Order Events
resource "aws_sns_topic" "order_events" {
  name = "${var.project_name}-order-events"

  tags = local.common_tags
}

# SNS Topic Policy
resource "aws_sns_topic_policy" "order_events_policy" {
  arn = aws_sns_topic.order_events.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = [
          "SNS:Publish"
        ]
        Resource = aws_sns_topic.order_events.arn
      }
    ]
  })
}

# SQS Queue for Order Processing
resource "aws_sqs_queue" "order_processing" {
  name                      = "${var.project_name}-order-processing"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 1209600  # 14 days
  receive_wait_time_seconds = 10       # Long polling
  
  # Dead letter queue configuration
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_processing_dlq.arn
    maxReceiveCount     = 3
  })

  tags = local.common_tags
}

# SQS Dead Letter Queue
resource "aws_sqs_queue" "order_processing_dlq" {
  name                      = "${var.project_name}-order-processing-dlq"
  message_retention_seconds = 1209600  # 14 days

  tags = local.common_tags
}

# SQS Queue for Email Notifications
resource "aws_sqs_queue" "email_notifications" {
  name                      = "${var.project_name}-email-notifications"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 1209600
  receive_wait_time_seconds = 10

  # Dead letter queue configuration
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.email_notifications_dlq.arn
    maxReceiveCount     = 3
  })

  tags = local.common_tags
}

# Email Notifications Dead Letter Queue
resource "aws_sqs_queue" "email_notifications_dlq" {
  name                      = "${var.project_name}-email-notifications-dlq"
  message_retention_seconds = 1209600

  tags = local.common_tags
}

# SNS Subscription - Order Processing Queue
resource "aws_sns_topic_subscription" "order_processing_subscription" {
  topic_arn = aws_sns_topic.order_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.order_processing.arn

  filter_policy = jsonencode({
    eventType = ["ORDER_CREATED", "ORDER_STATUS_CHANGED"]
  })
}

# SNS Subscription - Email Notifications Queue
resource "aws_sns_topic_subscription" "email_notifications_subscription" {
  topic_arn = aws_sns_topic.order_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.email_notifications.arn

  filter_policy = jsonencode({
    eventType = ["ORDER_CREATED", "ORDER_COMPLETED"]
  })
}

# SQS Queue Policy for SNS
resource "aws_sqs_queue_policy" "order_processing_policy" {
  queue_url = aws_sqs_queue.order_processing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action = "sqs:SendMessage"
        Resource = aws_sqs_queue.order_processing.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.order_events.arn
          }
        }
      }
    ]
  })
}

resource "aws_sqs_queue_policy" "email_notifications_policy" {
  queue_url = aws_sqs_queue.email_notifications.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action = "sqs:SendMessage"
        Resource = aws_sqs_queue.email_notifications.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.order_events.arn
          }
        }
      }
    ]
  })
}

# Lambda function for SNS notifications
resource "aws_lambda_function" "sns_notification" {
  filename         = "lambda/sns_notification.zip"
  function_name    = "${var.project_name}-sns-notification"
  role            = aws_iam_role.lambda_sns_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.sns_notification_zip.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = 30

  environment {
    variables = {
      SNS_TOPIC_ARN  = aws_sns_topic.order_events.arn
      DYNAMODB_TABLE = aws_dynamodb_table.orders.name
    }
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-sns-notification-lambda"
  })
}

# IAM Role for Lambda SNS function
resource "aws_iam_role" "lambda_sns_role" {
  name = "${var.project_name}-lambda-sns-role"

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

# IAM Policy for Lambda SNS function
resource "aws_iam_policy" "lambda_sns_policy" {
  name = "${var.project_name}-lambda-sns-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.order_events.arn
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:DescribeStream",
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator",
          "dynamodb:ListStreams"
        ]
        Resource = "${aws_dynamodb_table.orders.arn}/stream/*"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "lambda_sns_policy" {
  policy_arn = aws_iam_policy.lambda_sns_policy.arn
  role       = aws_iam_role.lambda_sns_role.name
}

# CloudWatch Alarms for SQS
resource "aws_cloudwatch_metric_alarm" "sqs_dlq_messages" {
  alarm_name          = "${var.project_name}-sqs-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfVisibleMessages"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "0"
  alarm_description   = "This metric monitors messages in DLQ"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    QueueName = aws_sqs_queue.order_processing_dlq.name
  }

  tags = local.common_tags
}