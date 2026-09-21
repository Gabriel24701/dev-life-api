"""adiciona campos de integracao github ao user

Revision ID: 2edabbf8a3ad
Revises: 8b9b5db169b4
Create Date: 2026-09-20 14:38:12.821682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2edabbf8a3ad'
down_revision: Union[str, None] = '8b9b5db169b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tudo abaixo usa SQL cru com IF NOT EXISTS, nao op.add_column()/
    # op.create_index() comuns. Motivo: o job migrations_check do CI roda
    # Base.metadata.create_all() ANTES desta migration, e create_all() sempre
    # reflete o models.py atual (indice unico em github_username, tipos Text
    # nos tokens, e o proprio index=True de tasks.description que ja existia
    # antes desta mudanca), entao tudo abaixo ja existe quando este upgrade
    # roda ali. op.add_column()/op.create_index() comuns falhariam com
    # "already exists" nesse cenario.
    #
    # Em producao real essas colunas ainda nao existem. Ja o
    # ix_tasks_description e um caso especial: ele foi declarado no
    # upgrade() da baseline (8b9b5db169b4), mas a baseline so foi *stamped*
    # em producao, nunca *upgraded* (stamp so grava metadado, nao roda DDL,
    # ver docs/alembic-baseline-runbook.md). Ou seja, esse indice
    # provavelmente nunca existiu de fato em producao ate esta migration
    # rodar de verdade. O IF NOT EXISTS cobre os dois cenarios com o mesmo
    # SQL: cria pra valer em producao, e nao quebra no create_all() do CI.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_tasks_description ON tasks (description)"
    )
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS github_username VARCHAR")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_github_username "
        "ON users (github_username)"
    )
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS github_access_token TEXT")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS github_refresh_token TEXT")


def downgrade() -> None:
    # ix_tasks_description nao e desfeito aqui de proposito: ele pertence
    # semanticamente a baseline (8b9b5db169b4), que ja tem seu proprio
    # drop_index pra ele. Descer alem da baseline continua removendo o
    # indice, so que no downgrade da baseline, nao duplicado aqui.
    op.execute("DROP INDEX IF EXISTS ix_users_github_username")
    op.drop_column('users', 'github_refresh_token')
    op.drop_column('users', 'github_access_token')
    op.drop_column('users', 'github_username')
