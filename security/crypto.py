"""Criptografia simetrica reversivel para segredos que precisam ser
recuperados em texto plano depois de guardados (ex.: github_access_token,
github_refresh_token). Diferente de security/auth.py (hash de senha,
irreversivel por design, so serve pra comparar), aqui o valor original
precisa voltar intacto pra ser usado numa chamada real a API do GitHub.
"""

import base64
import hashlib
import os

from cryptography.fernet import Fernet


def _derive_fernet_key(secret_key: str) -> bytes:
    """Deriva uma chave Fernet valida (32 bytes url-safe base64) a partir do
    SECRET_KEY existente. Fernet exige exatamente 32 bytes codificados em
    urlsafe-base64; SECRET_KEY e uma string arbitraria de tamanho e formato
    quaisquer, entao nao da pra usar direto como chave. sha256 sempre
    produz 32 bytes de digest (resolve o tamanho); urlsafe_b64encode
    codifica esses 32 bytes exatamente no formato que Fernet exige.
    """
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


_fernet_instance: Fernet | None = None


def _get_fernet() -> Fernet:
    """Instancia o Fernet sob demanda, na primeira chamada real a
    encrypt_token/decrypt_token, nao no import do modulo.

    SECRET_KEY nao tem fallback aqui, diferente de security/auth.py (que
    cai num valor de dev conhecido se a env var nao estiver setada). Cair
    no mesmo fallback aqui seria pior do que nao criptografar nada: esse
    valor de dev esta commitado neste repositorio publico, entao
    "criptografar" um access_token real do GitHub com essa chave daria uma
    falsa sensacao de seguranca. Por isso o erro explicito em vez de um
    fallback silencioso.

    A checagem acontece so no primeiro uso, nao no import do modulo, pra
    uma instancia local sem nenhuma integracao GitHub configurada
    continuar subindo normalmente (routes/github_routes.py importa este
    modulo, e main.py importa todas as routes incondicionalmente).
    """
    global _fernet_instance
    if _fernet_instance is None:
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise RuntimeError(
                "SECRET_KEY precisa estar definida e nao vazia para "
                "criptografar ou descriptografar tokens do GitHub."
            )
        _fernet_instance = Fernet(_derive_fernet_key(secret_key))
    return _fernet_instance


def encrypt_token(plain: str) -> str:
    """Criptografa um token em texto plano (ex.: access_token do GitHub) e
    devolve o resultado como string, pronta pra guardar numa coluna Text.
    """
    return _get_fernet().encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_token(encrypted: str) -> str:
    """Reverte encrypt_token: recebe o valor guardado no banco e devolve o
    token original em texto plano, pronto pra uma chamada real a API do
    GitHub.
    """
    return _get_fernet().decrypt(encrypted.encode("utf-8")).decode("utf-8")
