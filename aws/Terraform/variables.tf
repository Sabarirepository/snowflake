# variables.tf

variable "region" {
  description = "AWS region"
  type        = string
}

variable "aws_access_key" {
  description = "AWS Access Key"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS Secret Key"
  type        = string
  sensitive   = true
}



variable "adherent_bucket_name" {
  description = "S3 bucket name"
  type        = string
}


#variable "bucket_name" {
#  description = "S3 bucket name"
#  type        = string
#}


#variable "new_bucket_name" {
#  description = "Name of the new S3 bucket for adherent users"
#  type        = string
#}


variable "bucket_names" {
  description = "List of S3 bucket names to create"
  type        = list(string)
}


variable "group_name" {
  description = "IAM groups with permissions"
  type = map(object({
    name        = string
    permissions = list(string)
  }))
}

variable "user_names" {
  description = "IAM users and group membership"
  type = map(object({
    user_group       = list(string)
    login_name       = string
    default_password = string
  }))
}

variable "default_password" {
  description = "Default user password"
  type        = string
  sensitive   = true
}