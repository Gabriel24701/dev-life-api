from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import os
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import User
from models.schemas import GoogleLoginPayload, UserCreate, UserResponse, UserUpdate
from security.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado, resolvidos a partir do token JWT."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza o nome do usuário autenticado."""
    current_user.name = user_update.name
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário, garantindo que o e-mail seja único e a senha seja armazenada de forma segura."""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    
    hashed_pw = get_password_hash(user.password)
    
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Autentica o usuário e retorna um token JWT para acesso às rotas protegidas."""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google")
def google_login(payload: GoogleLoginPayload, db: Session = Depends(get_db)):
    """Autentica via Google Identity Services: verifica o ID token, encontra
    a conta existente (por google_sub) ou cria uma nova, e retorna o mesmo
    formato de resposta de /auth/login."""
    try:
        idinfo = id_token.verify_oauth2_token(
            payload.credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Token do Google inválido.")

    if not idinfo.get("email_verified"):
        raise HTTPException(status_code=401, detail="E-mail do Google não verificado.")

    email = idinfo["email"]
    google_sub = idinfo["sub"]

    user = db.query(User).filter(User.google_sub == google_sub).first()
    if not user:
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma conta com este e-mail. Faça login com sua senha.",
            )
        user = User(
            name=idinfo.get("name", email),
            email=email,
            hashed_password=None,
            auth_provider="google",
            google_sub=google_sub,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}