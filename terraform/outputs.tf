output "kube_config" {
  value     = azurerm_kubernetes_cluster.aks-infra-api-demo.kube_config_raw
  sensitive = true
}

output "cluster_name" {
  value = azurerm_kubernetes_cluster.aks-infra-api-demo.name
}
