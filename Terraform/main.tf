terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.60.0"
    }
  }
}

provider "snowflake" {
  account   = var.snowflake_account
  username  = var.snowflake_username
  password  = var.snowflake_password
  role      = var.snowflake_role
}


module "warehouse_module" {
  source = "./Inframodule"

  snowflake_warehouse = var.snowflake_warehouse
  snowflake_account   = var.snowflake_account
  snowflake_username  = var.snowflake_username
  snowflake_password  = var.snowflake_password
  snowflake_role      = var.snowflake_role
}