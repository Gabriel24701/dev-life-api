# Runbook: baseline inicial do Alembic em produção

Este é um procedimento **único** (só roda uma vez, ao introduzir o Alembic).
Depois que a produção estiver "carimbada" na revisão baseline, mudanças de
schema seguem o fluxo normal descrito no `README.md` (seção Migrations).

Requer acesso ao Postgres de produção (Azure Postgres Flexible Server,
`devlife_db`) e às ferramentas `pg_dump`/`psql`/Docker localmente. Nenhum
desses comandos deve ser rodado por CI/automação — é um procedimento manual,
feito uma vez, por alguém com as credenciais de produção em mãos.

## Por quê um Postgres descartável em vez de rodar direto contra produção

`alembic revision --autogenerate` só faz leitura (reflection do schema), mas
dado o histórico de mudanças manuais não documentadas neste projeto
(`owner_id`, `priority`, `tags`, `last_completed_at` nunca tiveram SQL
correspondente), é bem provável que exista *drift* entre `models/models.py`
e o schema real. É mais seguro descobrir esse drift num ambiente sem risco
do que ao vivo. A única operação que efetivamente toca produção neste
runbook é `alembic stamp head`, que é somente metadado (não executa DDL).

## Passo a passo

1. **Dump somente de schema da produção** (idealmente com um usuário/role
   somente leitura):

   ```bash
   pg_dump --schema-only --no-owner --no-privileges \
     -h <host-do-azure-postgres> -U <usuario> -d devlife_db \
     -f prod_schema_snapshot.sql
   ```

2. **Subir um Postgres local descartável** e restaurar o dump nele:

   ```bash
   docker run --rm -d --name alembic-baseline \
     -e POSTGRES_USER=devlife -e POSTGRES_PASSWORD=devlife \
     -e POSTGRES_DB=devlife_baseline -p 5433:5432 postgres:14

   psql -h localhost -p 5433 -U devlife -d devlife_baseline -f prod_schema_snapshot.sql
   ```

3. **Apontar `DATABASE_URL` para esse Postgres descartável** (só na sessão
   de shell atual, nunca commitado):

   ```bash
   # PowerShell
   $env:DATABASE_URL = "postgresql://devlife:devlife@localhost:5433/devlife_baseline"
   ```

4. **Gerar a revisão baseline:**

   ```bash
   alembic revision --autogenerate -m "baseline: schema atual de producao"
   ```

5. **Inspecionar o arquivo gerado em `alembic/versions/`.** O esperado é que
   venha **vazio** (`upgrade()`/`downgrade()` sem operações) — isso confirma
   que os models batem exatamente com o schema real. Se vier com `op.add_column`,
   `op.alter_column` etc. inesperados, é sinal de drift real entre o schema de
   produção e `models/models.py` — resolva isso (ajustando o model ou aceitando
   a mudança deliberadamente) antes de continuar. Não ignore silenciosamente.

6. **Validar a migration contra o Postgres descartável** (nunca contra
   produção nesta etapa):

   ```bash
   alembic upgrade head
   alembic current   # deve mostrar a revisão baseline
   ```

7. **Só agora, apontar para a produção real** e rodar **`stamp`, nunca
   `upgrade`**:

   ```bash
   # PowerShell — usar a DATABASE_URL real de produção
   $env:DATABASE_URL = "<DATABASE_URL de producao>"
   alembic stamp head
   ```

   `stamp` cria a tabela `alembic_version` (se não existir) e grava o id da
   revisão baseline, **sem executar nenhum DDL**. O schema de produção não é
   tocado — só passa a ser "conhecido" pelo Alembic.

8. **Confirmar:**

   ```bash
   alembic current   # deve reportar a revisão baseline, apontando para producao
   ```

   Opcionalmente, rodar mais uma vez `alembic revision --autogenerate` contra
   produção (leitura, seguro) só para confirmar que agora gera diff vazio.

9. **Limpeza:** derrubar o container descartável
   (`docker stop alembic-baseline`) e apagar `prod_schema_snapshot.sql` local
   se ele contiver informação sensível de schema que não precise ficar no
   disco.

## Depois do baseline

- Configurar o secret `PRODUCTION_DATABASE_URL` no GitHub (Settings → Secrets
  and variables → Actions) apontando para a mesma `DATABASE_URL` de produção —
  necessário para o workflow manual
  `.github/workflows/migrate-production.yml`.
- A partir daqui, qualquer mudança de schema segue o fluxo normal: alterar o
  model, `alembic revision --autogenerate`, revisar, testar local, commitar,
  e rodar o workflow manual `migrate-production.yml` quando pronto para
  aplicar em produção.
