# =========================================================
# CONFIGURAÇÃO E VARIÁVEIS
# =========================================================

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "db_password" {
  description = "A palavra-passe do administrador da Base de Dados PostgreSQL"
  type        = string
  sensitive   = true
}

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
      docker_image_name   = "bielllb/dev-life-api:latest" 
      docker_registry_url = "https://index.docker.io/v1/"
    }
  }

  app_settings = {
    "WEBSITES_PORT" = "8000"
    "DATABASE_URL"  = "postgresql://${azurerm_postgresql_flexible_server.db_server.administrator_login}:${var.db_password}@${azurerm_postgresql_flexible_server.db_server.name}.postgres.database.azure.com:5432/${azurerm_postgresql_flexible_server_database.db_dev_life.name}"
  }
}