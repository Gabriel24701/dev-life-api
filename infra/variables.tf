variable "db_password" {
  description = "A palavra-passe do administrador da Base de Dados PostgreSQL"
  type        = string
  sensitive   = true
}

variable "rabbitmq_url" {
  description = "URL de conexao do RabbitMQ (CloudAMQP), formato amqps://usuario:senha@host/vhost"
  type        = string
  sensitive   = true
}

variable "google_client_id" {
  description = "Client ID OAuth do Google, usado por POST /auth/google para validar a audiencia (aud) do ID token"
  type        = string
}

variable "secret_key" {
  description = "Chave usada para assinar tokens JWT e para criptografar os tokens de acesso do GitHub em repouso"
  type        = string
  sensitive   = true
}

variable "github_client_id" {
  description = "Client ID do OAuth App do GitHub, usado em GET /github/authorize e GET /github/callback"
  type        = string
}

variable "github_client_secret" {
  description = "Client Secret do OAuth App do GitHub, usado na troca do code por access_token em GET /github/callback"
  type        = string
  sensitive   = true
}

variable "github_redirect_uri" {
  description = "URI de redirect registrada no OAuth App do GitHub, para onde o GitHub redireciona apos a autorizacao"
  type        = string
}
