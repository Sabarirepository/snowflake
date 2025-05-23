terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.60.0"
    }
  }
}

resource "snowflake_warehouse" "prod_wh" {
  name           = var.snowflake_warehouse
  warehouse_size = "XSMALL"
  auto_suspend   = 60
  auto_resume    = true
}