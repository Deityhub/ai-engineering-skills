# Terraform Module Template
# Usage: Copy to modules/<name>/main.tf and customize

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Variables with validation
variable "name" {
  description = "Name prefix for all resources"
  type        = string
  validation {
    condition     = length(var.name) <= 63
    error_message = "Name must be 63 characters or less."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
  validation {
    condition     = length(var.tags) > 0
    error_message = "At least one tag is required."
  }
}

variable "enabled" {
  description = "Whether to create resources"
  type        = bool
  default     = true
}

# Locals for computed values
locals {
  common_tags = merge(var.tags, {
    Name        = var.name
    Environment = var.environment
    ManagedBy   = "terraform"
  })
}

# Resources go here
# resource "aws_xxx" "this" {
#   count = var.enabled ? 1 : 0
#   ...
#   tags = local.common_tags
# }

# Outputs
output "id" {
  description = "Resource ID"
  value       = var.enabled ? aws_xxx.this[0].id : null
}

output "arn" {
  description = "Resource ARN"
  value       = var.enabled ? aws_xxx.this[0].arn : null
}