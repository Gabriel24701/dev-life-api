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
