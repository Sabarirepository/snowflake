terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.60.0"
      configuration_aliases = [snowflake.prod, snowflake.dev]
    }
  }
}


#rsg - Create Prod Roles
resource "snowflake_role" "prod_roles" {
  provider       = snowflake.prod
  for_each       = toset(var.prod_wh_roles)
  name = each.key
}


#rsg - Create Dev Roles
resource "snowflake_role" "dev_roles" {
  provider       = snowflake.dev
  for_each      = toset(var.dev_wh_roles)
  name           = each.key
}





#rsg - Create Prod Users
resource "snowflake_user" "prod_users" {
  provider       = snowflake.prod
  for_each       = toset(var.prod_wh_users)
  
  name                = each.key
  login_name          = each.key
  email               = each.key
  password            = "TempPassword123!"  # Replace this with a secure method in real use
  must_change_password = true
}


#rsg - Create Prod Users
resource "snowflake_user" "dev_users" {
  provider       = snowflake.dev
  for_each       = toset(var.dev_wh_users)
  name = each.key
}


