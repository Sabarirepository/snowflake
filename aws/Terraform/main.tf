provider "aws" {
  region     = var.region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

# Create S3 bucket
#resource "aws_s3_bucket" "main_bucket" {
#  bucket = var.bucket_name
#}

resource "aws_s3_bucket" "main_buckets" {
  for_each = toset(var.bucket_names)

  bucket = each.key
}


# Create IAM Groups
resource "aws_iam_group" "groups" {
  for_each = var.group_name
  name     = each.value.name
}

# Inline policy documents
data "aws_iam_policy_document" "s3_full_access" {
  statement {
    actions   = ["s3:*"]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "adherent_bucket_access" {
  statement {
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::${var.adherent_bucket_name}",
      "arn:aws:s3:::${var.adherent_bucket_name}/*"
    ]
  }
}

resource "aws_iam_policy" "s3_full_access" {
  name        = "S3FullAccessPolicy"
  description = "Provides full access to S3"
  policy      = data.aws_iam_policy_document.s3_full_access.json
}

resource "aws_iam_policy" "adherent_bucket_access" {
  name   = "AdherentBucketFullAccess"
  policy = data.aws_iam_policy_document.adherent_bucket_access.json
}

# Single local value block for all policy ARNs
locals {
  policy_arns = {
    s3_full_access                = aws_iam_policy.s3_full_access.arn
    AmazonDynamoDBReadOnlyAccess = "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess"
    AdherentBucketFullAccess     = aws_iam_policy.adherent_bucket_access.arn
  }
}

# IAM Group Policy Attachments
resource "aws_iam_group_policy_attachment" "attachments" {
  for_each = {
    for item in flatten([
      for group_key, group in var.group_name : [
        for permission in group.permissions : {
          key        = "${group_key}-${permission}"
          group      = group_key
          permission = permission
        }
      ]
    ]) : item.key => item
  }

  group      = aws_iam_group.groups[each.value.group].name
  policy_arn = local.policy_arns[each.value.permission]
}

# Create IAM users
resource "aws_iam_user" "users" {
  for_each = var.user_names
  name     = each.key
}

# User login profiles (console access)
resource "aws_iam_user_login_profile" "user_login" {
  for_each                = var.user_names
  user                    = aws_iam_user.users[each.key].name
  password_reset_required = true
}

# Add users to groups
resource "aws_iam_user_group_membership" "user_groups" {
  for_each = var.user_names
  user     = aws_iam_user.users[each.key].name
  groups   = [
    for g in each.value.user_group : aws_iam_group.groups[g].name
  ]
}
