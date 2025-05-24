terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.60.0"
    }
  }
}

provider "snowflake" {
  alias    = "prod"
  account  = var.prod_snowflake_account
  username = var.prod_snowflake_username
  password = var.prod_snowflake_password
  role     = var.prod_snowflake_role
}

provider "snowflake" {
  alias    = "dev"
  account  = var.dev_snowflake_account
  username = var.dev_snowflake_username
  password = var.dev_snowflake_password
  role     = var.dev_snowflake_role
}

module "warehouse_module" {
  source = "./Inframodule"
  
  providers = {
    snowflake.prod = snowflake.prod
    snowflake.dev  = snowflake.dev
  }

  prod_snowflake_warehouse = var.prod_snowflake_warehouse
  dev_snowflake_warehouse  = var.dev_snowflake_warehouse
  dev_snowflake_warehouse_TEST  = var.dev_snowflake_warehouse_TEST
}