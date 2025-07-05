variable "group_name" {
  type        = string
  description = "IAM group name"
}

variable "bucket_name" {
  type        = string
  description = "S3 bucket name"
}

variable "user_names" {
  type        = list(string)
  description = "List of IAM users to create"
}

variable "default_password" {
  type        = string
  description = "Default password for IAM users"
  sensitive   = true
}
