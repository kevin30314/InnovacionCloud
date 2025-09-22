variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "serverless-orders"
}

variable "api_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "dev"
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.9"
}

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode"
  type        = string
  default     = "ON_DEMAND"
}

variable "enable_point_in_time_recovery" {
  description = "Enable DynamoDB point in time recovery"
  type        = bool
  default     = true
}

variable "enable_contributor_insights" {
  description = "Enable DynamoDB contributor insights"
  type        = bool
  default     = true
}