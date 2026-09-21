import logging
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import jwt
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from database.database import get_db
from models.models import User
from models.schemas import (
    GitHubAuthorizeResponse,
    GitHubConnectionResponse,
    GitHubContributionDay,
    GitHubContributionsResponse,
)
from security.auth import ALGORITHM, SECRET_KEY, get_current_user
from security.crypto import decrypt_token, encrypt_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["GitHub"])

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/github/callback")

# Proposito fixo gravado no state, conferido no callback. Existe pra alem da
# assinatura/expiracao: garante que um JWT qualquer assinado com o mesmo
# SECRET_KEY (ex.: um token de sessao comum) nunca seja aceito aqui so por
# ter uma assinatura valida.
STATE_PURPOSE = "github_connect"
STATE_EXPIRE_MINUTES = 10

# Uso unico do state (nonce), independente da protecao de reuso que o
# proprio GitHub possa ou nao aplicar sobre o "code" (a documentacao oficial
# confirma so a expiracao de 10min do code, nao confirma reuso explicitamente
# -- ver decisao registrada na conversa desta fase). Em memoria do processo:
# suficiente pro tamanho atual do deploy (uma instancia, plano F1); se um dia
# escalar pra multiplas instancias, isso deixa de proteger entre elas.
_used_github_states: set[str] = set()

# Cache em memoria do calendario de contribuicoes por usuario. 5 minutos:
# suficiente pra evitar bater na API do GitHub a cada refresh de tela em
# uso normal (rate limit da GraphQL API e por token, 5000 pontos/hora),
# sem atrasar de forma perceptivel uma contribuicao recente aparecendo no
# calendario. Mesma limitacao do _used_github_states: por processo, nao
# compartilhado entre instancias.
CONTRIBUTIONS_CACHE_TTL_SECONDS = 5 * 60
_contributions_cache: dict[int, tuple[float, GitHubContributionsResponse]] = {}

CONTRIBUTIONS_QUERY = """
query {
  viewer {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


@router.get("/authorize", response_model=GitHubAuthorizeResponse)
def github_authorize(current_user: User = Depends(get_current_user)):
    """Gera a URL de autorizacao do GitHub para o usuario logado conectar
    sua conta. Protegida por JWT normal (chamada via fetch do frontend, ja
    logado) -- diferente do callback abaixo, que e atingido por um redirect
    puro do navegador sem nenhum header customizado.

    O state carrega a identidade de quem iniciou o fluxo, assinado com o
    mesmo SECRET_KEY da sessao, mas com claims proprias (connect_user_id,
    nao sub; purpose) para nunca ser aceito por engano como token de sessao
    normal em get_current_user, que so olha a claim sub.

    Sem scope: o calendario de contribuicoes e o username sao dados
    publicos do proprio dono do token, nenhum escopo especial e necessario.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=STATE_EXPIRE_MINUTES)
    state = jwt.encode(
        {
            "connect_user_id": current_user.id,
            "purpose": STATE_PURPOSE,
            "jti": uuid.uuid4().hex,
            "exp": expire,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    query = urlencode(
        {
            "client_id": GITHUB_CLIENT_ID,
            "redirect_uri": GITHUB_REDIRECT_URI,
            "state": state,
        }
    )
    return GitHubAuthorizeResponse(authorize_url=f"https://github.com/login/oauth/authorize?{query}")


@router.get("/callback", response_model=GitHubConnectionResponse)
def github_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Publico (sem Depends(get_current_user)) de proposito: o GitHub chega
    aqui via redirect do navegador, sem Authorization header. A identidade
    de quem esta conectando vem inteiramente do state decodificado abaixo.
    """
    try:
        payload = jwt.decode(state, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão de conexão com o GitHub expirada ou inválida, tente novamente.",
        )

    if payload.get("purpose") != STATE_PURPOSE:
        raise HTTPException(status_code=401, detail="Sessão de conexão com o GitHub inválida.")

    jti = payload.get("jti")
    if not jti or jti in _used_github_states:
        raise HTTPException(status_code=401, detail="Este link de conexão com o GitHub já foi usado.")
    _used_github_states.add(jti)

    connect_user_id = payload.get("connect_user_id")
    user = db.query(User).filter(User.id == connect_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": GITHUB_REDIRECT_URI,
        },
        headers={"Accept": "application/json"},
        timeout=5,
    )
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Não foi possível conectar ao GitHub.")

    refresh_token = token_data.get("refresh_token")

    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=5,
    )
    github_username = user_response.json().get("login")

    user.github_access_token = encrypt_token(access_token)
    user.github_refresh_token = encrypt_token(refresh_token) if refresh_token else None
    user.github_username = github_username
    db.commit()
    db.refresh(user)

    return GitHubConnectionResponse(connected=True, github_username=user.github_username)


@router.get("/contributions", response_model=GitHubContributionsResponse)
def github_contributions(current_user: User = Depends(get_current_user)):
    """Consulta o calendario de contribuicoes dos ultimos 12 meses (default
    do proprio contributionsCollection quando from/to nao sao passados).

    Sem renovacao automatica de token (decisao consciente desta fase): se o
    GitHub recusar o token (401), devolve 401 com mensagem clara pedindo pra
    reconectar, em vez de tentar renovar sozinho.
    """
    if not current_user.github_access_token:
        raise HTTPException(status_code=409, detail="Conta GitHub não conectada.")

    cached = _contributions_cache.get(current_user.id)
    if cached and (time.monotonic() - cached[0]) < CONTRIBUTIONS_CACHE_TTL_SECONDS:
        return cached[1]

    access_token = decrypt_token(current_user.github_access_token)

    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": CONTRIBUTIONS_QUERY},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=5,
    )

    if response.status_code == 401:
        raise HTTPException(
            status_code=401,
            detail="Token do GitHub expirado ou inválido. Reconecte sua conta.",
        )

    calendar = response.json()["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]
    days = [
        GitHubContributionDay(date=day["date"], count=day["contributionCount"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]
    result = GitHubContributionsResponse(
        total_contributions=calendar["totalContributions"], days=days
    )

    _contributions_cache[current_user.id] = (time.monotonic(), result)
    return result


@router.delete("", status_code=204)
def github_disconnect(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Desconecta a conta GitHub localmente. Nao revoga o grant do lado do
    GitHub (decisao explicita desta fase)."""
    current_user.github_access_token = None
    current_user.github_refresh_token = None
    current_user.github_username = None
    db.commit()
