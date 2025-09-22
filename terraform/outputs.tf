output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = "https://${aws_api_gateway_rest_api.orders_api.id}.execute-api.${var.aws_region}.amazonaws.com/${var.api_stage_name}"
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.orders.name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for invoices"
  value       = aws_s3_bucket.invoices.bucket
}

output "lambda_orders_crud_function_name" {
  description = "Name of the orders CRUD Lambda function"
  value       = aws_lambda_function.orders_crud.function_name
}

output "lambda_pdf_generator_function_name" {
  description = "Name of the PDF generator Lambda function"
  value       = aws_lambda_function.pdf_generator.function_name
}

output "cloudwatch_dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.serverless_dashboard.dashboard_name}"
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = aws_sns_topic.alerts.arn
}