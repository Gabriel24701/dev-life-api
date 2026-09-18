# =========================================================
# 1. O GRUPO DE RECURSOS
# =========================================================

resource "azurerm_resource_group" "rg_dev_life" {
  name     = "rg-dev-life-backend"
  location = "canadacentral"

  tags = {
    Environment = "Desenvolvimento"
    Project     = "Dev Life"
    ManagedBy   = "Terraform"
  }
}

# =========================================================
# 2. BASE DE DADOS (PostgreSQL Flexible Server)
# =========================================================

resource "azurerm_postgresql_flexible_server" "db_server" {
  name                   = "psql-devlife-bielllb-01"
  resource_group_name    = azurerm_resource_group.rg_dev_life.name
  location               = azurerm_resource_group.rg_dev_life.location
  version                = "14"
  administrator_login    = "devlifeadmin"
  administrator_password = var.db_password
  zone                   = "1"
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
}

resource "azurerm_postgresql_flexible_server_database" "db_dev_life" {
  name      = "devlife_db"
  server_id = azurerm_postgresql_flexible_server.db_server.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.db_server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# =========================================================
# 3. SERVIDOR WEB (App Service para o Python/FastAPI)
# =========================================================

resource "azurerm_service_plan" "app_plan" {
  name                = "plan-dev-life-central"
  location            = "centralus"
  resource_group_name = azurerm_resource_group.rg_dev_life.name
  os_type             = "Linux"
  sku_name            = "F1"
}

resource "azurerm_linux_web_app" "api_app" {
  name                = "app-devlife-api-bielllb-01"
  location            = "centralus"
  resource_group_name = azurerm_resource_group.rg_dev_life.name
  service_plan_id     = azurerm_service_plan.app_plan.id

  site_config {
    always_on = false

    application_stack {
      docker_image_name = "bielllb/dev-life-api:latest"
      docker_registry_url = "https://index.docker.io"
    }
  }

  app_settings = {
    "WEBSITES_PORT" = "8000"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE"   = "false"
    "DATABASE_URL"                          = "postgresql://${azurerm_postgresql_flexible_server.db_server.administrator_login}:${urlencode(var.db_password)}@${azurerm_postgresql_flexible_server.db_server.name}.postgres.database.azure.com:5432/${azurerm_postgresql_flexible_server_database.db_dev_life.name}?sslmode=require"
    "GOOGLE_CLIENT_ID"                      = var.google_client_id
    "RABBITMQ_URL"                          = var.rabbitmq_url
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.api_insights.connection_string
  }
  tags = {
    "hidden-link: /app-insights-resource-id" = "/subscriptions/cc0a0efc-329c-4488-851b-f9633ca7479c/resourceGroups/rg-dev-life-backend/providers/microsoft.insights/components/appi-devlife-api"
  }
}

# =========================================================
# 4. MENSAGERIA (Container Apps Job para o worker RabbitMQ)
# =========================================================

resource "azurerm_log_analytics_workspace" "worker_logs" {
  name                = "log-devlife-worker"
  location            = "centralus"
  resource_group_name = azurerm_resource_group.rg_dev_life.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "worker_env" {
  name                       = "cae-devlife-worker"
  location                   = "centralus"
  resource_group_name        = azurerm_resource_group.rg_dev_life.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.worker_logs.id
}

resource "azurerm_container_app_job" "worker_job" {
  name                         = "job-devlife-worker"
  location                     = "centralus"
  resource_group_name          = azurerm_resource_group.rg_dev_life.name
  container_app_environment_id = azurerm_container_app_environment.worker_env.id

  replica_timeout_in_seconds = 300
  replica_retry_limit        = 1

  schedule_trigger_config {
    cron_expression          = "*/15 * * * *"
    parallelism              = 1
    replica_completion_count = 1
  }

  secret {
    name  = "rabbitmq-url"
    value = var.rabbitmq_url
  }

  template {
    container {
      name    = "worker"
      image   = "bielllb/dev-life-api:latest"
      cpu     = 0.25
      memory  = "0.5Gi"
      command = ["python", "worker.py"]

      env {
        name        = "RABBITMQ_URL"
        secret_name = "rabbitmq-url"
      }
    }
  }
}
