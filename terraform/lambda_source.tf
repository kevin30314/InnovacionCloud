# Data sources for Lambda function code
data "archive_file" "orders_crud_zip" {
  type        = "zip"
  source_file = "lambda/orders_crud/lambda_function.py"
  output_path = "lambda/orders_crud.zip"
}

data "archive_file" "pdf_generator_zip" {
  type        = "zip"
  source_file = "lambda/pdf_generator/lambda_function.py"
  output_path = "lambda/pdf_generator.zip"
}

data "archive_file" "cognito_authorizer_zip" {
  type        = "zip"
  source_file = "lambda/cognito_authorizer/lambda_function.py"
  output_path = "lambda/cognito_authorizer.zip"
}

data "archive_file" "sns_notification_zip" {
  type        = "zip"
  source_file = "lambda/sns_notification/lambda_function.py"
  output_path = "lambda/sns_notification.zip"
}