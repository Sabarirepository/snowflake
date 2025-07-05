resource "aws_iam_user" "etl_users" {
  for_each = toset(var.user_names)
  name     = each.value
}

resource "aws_iam_user_login_profile" "user_passwords" {
  for_each               = aws_iam_user.etl_users
  user                   = each.value.name
  password               = var.default_password
  password_reset_required = true
}

resource "aws_iam_user_group_membership" "user_memberships" {
  for_each = aws_iam_user.etl_users

  user   = each.value.name
  groups = [aws_iam_group.etl_group.name]
}
