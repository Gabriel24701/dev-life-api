output "api_url" {
  description = "URL publica da API (App Service)"
  value       = "https://${azurerm_linux_web_app.api_app.default_hostname}"
}

output "resource_group_name" {
  description = "Nome do Resource Group que contem toda a infraestrutura"
  value       = azurerm_resource_group.rg_dev_life.name
}

output "postgres_fqdn" {
  description = "FQDN do servidor PostgreSQL, util para montar strings de conexao em scripts"
  value       = azurerm_postgresql_flexible_server.db_server.fqdn
}

output "log_analytics_workspace_id" {
  description = "Resource ID do workspace de logs (worker e App Insights escrevem nele)"
  value       = azurerm_log_analytics_workspace.worker_logs.id
}

output "application_insights_connection_string" {
  description = "Connection string do Application Insights"
  value       = azurerm_application_insights.api_insights.connection_string
  sensitive   = true
}
