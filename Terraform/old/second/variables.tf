variable "prod_snowflake_account" {
  description = "Production Snowflake account identifier"
  type        = string
}

variable "dev_snowflake_account" {
  description = "Development Snowflake account identifier"
  type        = string
}

variable "prod_snowflake_username" {
  description = "Production Snowflake username"
  type        = string
}

variable "dev_snowflake_username" {
  description = "Development Snowflake username"
  type        = string
}

variable "prod_snowflake_password" {
  description = "Production Snowflake password"
  type        = string
  sensitive   = true
}

variable "dev_snowflake_password" {
  description = "Development Snowflake password"
  type        = string
  sensitive   = true
}

variable "prod_snowflake_role" {
  description = "Production Snowflake role"
  type        = string
}

variable "dev_snowflake_role" {
  description = "Development Snowflake role"
  type        = string
}

variable "prod_snowflake_warehouse" {
  description = "Production Snowflake warehouse name"
  type        = string
}

variable "dev_snowflake_warehouse" {
  description = "Development Snowflake warehouse name"
  type        = string
}

variable "dev_snowflake_warehouse_TEST" {
  description = "Development Snowflake warehouse name"
  type        = string
}
