terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.60.0"
      configuration_aliases = [snowflake.prod, snowflake.dev]
    }
  }
}

#you need separte resource block
resource "snowflake_warehouse" "prod_wh" {
  provider       = snowflake.prod
  name           = var.prod_snowflake_warehouse
  warehouse_size = "XSMALL"
  auto_suspend   = 60
  auto_resume    = true
}


#you need separte resource block
resource "snowflake_warehouse" "dev_wh" {
  provider       = snowflake.dev
  name           = var.dev_snowflake_warehouse
  warehouse_size = "XSMALL"
  auto_suspend   = 60
  auto_resume    = true
}


#you need separte resource block
#resource "snowflake_warehouse" "dev_wh_test" {
#  provider       = snowflake.dev
#  name           = var.dev_snowflake_warehouse_TEST
#  warehouse_size = "XSMALL"
#  auto_suspend   = 60
#  auto_resume    = true
#}

