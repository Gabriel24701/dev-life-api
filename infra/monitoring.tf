# =========================================================
# 5. OBSERVABILIDADE (Application Insights + alertas)
# =========================================================
#
resource "azurerm_application_insights" "api_insights" {
  name                = "appi-devlife-api"
  location            = "centralus"
  resource_group_name = azurerm_resource_group.rg_dev_life.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.worker_logs.id
  retention_in_days   = 90
}

resource "azurerm_monitor_action_group" "email_alerts" {
  name                = "personal-dev-life"
  resource_group_name = azurerm_resource_group.rg_dev_life.name
  location            = "eastus"
  short_name          = "acg-dev-life"
  enabled             = true

  email_receiver {
    name                    = "meu-email_-EmailAction-"
    email_address           = "gabrielbebesilva247@gmail.com"
    use_common_alert_schema = true
  }
}

# Alerta 1: falha de conexao do worker com o RabbitMQ.
#
# A string da query casa com o logger.error de worker.py:102 se aquela
# mensagem mudar, este alerta para de disparar silenciosamente.
#
# Janela de 30min com avaliacao a cada 15min e deliberado: o Job roda
# "*/15 * * * *", entao uma janela de 5min avaliaria quase sempre periodos em
# que o worker sequer executou.
resource "azurerm_monitor_scheduled_query_rules_alert_v2" "worker_rabbitmq_failure" {
  name                = "alert-worker-rabbitmq-conexao"
  resource_group_name = azurerm_resource_group.rg_dev_life.name
  location            = "centralus"
  description         = "Worker nao conseguiu conectar/configurar o RabbitMQ na ultima execucao do Job"
  severity            = 2

  evaluation_frequency = "PT15M"
  window_duration      = "PT30M"
  scopes               = [azurerm_log_analytics_workspace.worker_logs.id]

  criteria {
    query = <<-KQL
      ContainerAppConsoleLogs_CL
      | where ContainerJobName_s == "job-devlife-worker"
      | where Log_s has "Nao foi possivel conectar/configurar o RabbitMQ"
    KQL

    time_aggregation_method = "Count"
    threshold               = 0
    operator                = "GreaterThan"

    failing_periods {
      minimum_failing_periods_to_trigger_alert = 1
      number_of_evaluation_periods             = 1
    }
  }

  auto_mitigation_enabled = true

  action {
    action_groups = [azurerm_monitor_action_group.email_alerts.id]
  }
}

# Alerta 2: erros HTTP 5xx na API (metrica nativa do App Service).
#
# threshold = 0 (qualquer 5xx alerta) e coerente com a decisao de
# sampling_ratio = 1.0 da instrumentacao: volume baixo, prioridade em nao
# perder sinal. Se virar ruido, subir o threshold antes de alargar a janela.
#
# Metric alert e recurso global — a ausencia de location aqui e proposital.
resource "azurerm_monitor_metric_alert" "api_http_5xx" {
  name                = "alert-api-http5xx"
  resource_group_name = azurerm_resource_group.rg_dev_life.name
  scopes              = [azurerm_linux_web_app.api_app.id]
  description         = "A API retornou erros HTTP 5xx"
  severity            = 2

  frequency   = "PT1M"
  window_size = "PT5M"

  criteria {
    metric_namespace = "Microsoft.Web/sites"
    metric_name      = "Http5xx"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 0
  }

  action {
    action_group_id = azurerm_monitor_action_group.email_alerts.id
  }
}
