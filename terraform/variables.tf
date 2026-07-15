variable "resource_group_name" {
  description = "Infrastructure API Demo Resource Group"
  type        = string
  default     = "rg-infra-api-demo"
}

variable "subscription_id" {
  description = "Azure subscription ID -- required explicitly as of azurerm provider v4.0"
  type        = string
}
