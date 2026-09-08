-- Migration 0001: suporte a login via Google
-- Rodar manualmente contra o Postgres de produção (não há Alembic configurado).
-- Idempotente onde possível (IF NOT EXISTS), mas revise antes de rodar.

-- 1. hashed_password passa a ser opcional (contas Google-only não têm senha local)
ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;

-- 2. Distingue o tipo de conta ('local' | 'google'). Contas existentes ficam 'local'
--    automaticamente via DEFAULT, sem precisar de UPDATE manual.
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(10) NOT NULL DEFAULT 'local';

-- 3. ID estável da conta Google (claim "sub" do ID token) — chave de vínculo pra
--    logins recorrentes via Google, independente de mudança de e-mail.
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_sub VARCHAR UNIQUE;
