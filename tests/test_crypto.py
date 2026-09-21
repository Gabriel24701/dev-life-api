import pytest

from security import crypto


@pytest.fixture(autouse=True)
def _reset_fernet_cache(monkeypatch):
    """_get_fernet() guarda a instancia num cache de modulo
    (_fernet_instance). Sem resetar isso a cada teste, o primeiro teste que
    cria a instancia com sucesso "vazaria" pros testes seguintes, inclusive
    os que testam a ausencia/vazio de SECRET_KEY (que nunca chegariam a
    checar a env var de novo, ja achariam o cache preenchido)."""
    monkeypatch.setattr(crypto, "_fernet_instance", None)


def test_encrypt_decrypt_roundtrip_retorna_o_valor_original(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "uma-chave-de-teste-qualquer")

    encrypted = crypto.encrypt_token("gho_tokenfake123")

    assert crypto.decrypt_token(encrypted) == "gho_tokenfake123"


def test_valor_criptografado_e_diferente_do_original(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "uma-chave-de-teste-qualquer")

    encrypted = crypto.encrypt_token("gho_tokenfake123")

    assert encrypted != "gho_tokenfake123"


def test_duas_chamadas_com_mesmo_input_geram_outputs_diferentes(monkeypatch):
    """Fernet embute um IV aleatorio e o timestamp da criacao em cada token
    gerado, entao criptografar o mesmo texto duas vezes produz duas saidas
    diferentes mesmo com a mesma chave. Isso e esperado e correto, nao e um
    bug: as duas ainda decriptografam pro mesmo valor original."""
    monkeypatch.setenv("SECRET_KEY", "uma-chave-de-teste-qualquer")

    first = crypto.encrypt_token("gho_tokenfake123")
    second = crypto.encrypt_token("gho_tokenfake123")

    assert first != second
    assert crypto.decrypt_token(first) == "gho_tokenfake123"
    assert crypto.decrypt_token(second) == "gho_tokenfake123"


def test_encrypt_token_sem_secret_key_configurada_levanta_erro_claro(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        crypto.encrypt_token("gho_tokenfake123")


def test_encrypt_token_com_secret_key_vazia_levanta_erro_claro(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "")

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        crypto.encrypt_token("gho_tokenfake123")
