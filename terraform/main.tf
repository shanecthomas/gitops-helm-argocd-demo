terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}

  # Follwing least privilege, the Managed Identity is scoped to the resource group only.
  # The following must be manually registered:
  # Microsoft.ContainerService, Microsoft.Compute,
  # Microsoft.Network, Microsoft.ManagedIdentity, Microsoft.OperationalInsights
  resource_provider_registrations = "none"

  subscription_id = var.subscription_id
}

# Terraform does not create or destroy this group — only the cluster inside it.
data "azurerm_resource_group" "rg-infra-api-demo" {
  name = var.resource_group_name
}

resource "azurerm_kubernetes_cluster" "aks-infra-api-demo" {
  name                = "aks-infra-api-demo"
  location            = data.azurerm_resource_group.rg-infra-api-demo.location
  resource_group_name = data.azurerm_resource_group.rg-infra-api-demo.name
  dns_prefix          = "infraapidemo"
  sku_tier            = "Free"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    purpose = "portfolio-demo"
    ttl     = "ephemeral-single-run"
  }
}
