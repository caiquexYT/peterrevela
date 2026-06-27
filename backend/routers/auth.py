"""
Roteador de autenticação para a API CxIA.
Endpoints: /auth/registro, /auth/login, /auth/logout, /auth/me
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional

from schemas import RegistroInput, LoginInput, AuthResponse, UsuarioResponse
from services.auth_service import registrar_usuario, login, logout, get_usuario_por_token, criar_usuario_guest

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registro", response_model=AuthResponse)
async def registro(dados: RegistroInput):
    """
    Registra um novo usuário no sistema.
    
    - **nome**: Nome completo do usuário
    - **email**: Email único (será verificado se já existe)
    - **senha**: Senha com mínimo 8 caracteres, 1 número e 1 maiúscula
    
    Retorna usuário criado + token JWT.
    """
    usuario, token = registrar_usuario(
        nome=dados.nome,
        email=dados.email,
        senha=dados.senha
    )
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado ou erro ao registrar")
    
    # Calcular data de expiração (30 dias)
    from datetime import datetime, timedelta
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    return {
        "user": usuario,
        "token": token,
        "expires_at": expires_at
    }


@router.post("/login", response_model=AuthResponse)
async def login_endpoint(dados: LoginInput):
    """
    Realiza login do usuário.
    
    - **email**: Email cadastrado
    - **senha**: Senha do usuário
    
    Retorna dados do usuário + token JWT.
    """
    usuario, token = login(email=dados.email, senha=dados.senha)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    
    from datetime import datetime, timedelta
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    return {
        "user": usuario,
        "token": token,
        "expires_at": expires_at
    }


@router.post("/logout")
async def logout_endpoint(authorization: Optional[str] = Header(None)):
    """
    Realiza logout invalidando o token.
    
    Requer header Authorization: Bearer <token>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = authorization.replace("Bearer ", "")
    sucesso = logout(token)
    
    if not sucesso:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    return {"message": "Logout realizado com sucesso"}


@router.get("/me", response_model=UsuarioResponse)
async def get_me(authorization: Optional[str] = Header(None)):
    """
    Obtém dados do usuário logado.
    
    Requer header Authorization: Bearer <token>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = authorization.replace("Bearer ", "")
    usuario = get_usuario_por_token(token)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    return usuario


@router.post("/guest", response_model=AuthResponse)
async def criar_guest():
    """
    Cria um usuário convidado (guest) temporário.
    
    Usuários guest têm acesso limitado e não possuem senha.
    """
    usuario, token = criar_usuario_guest()
    
    if not usuario:
        raise HTTPException(status_code=500, detail="Erro ao criar usuário guest")
    
    from datetime import datetime, timedelta
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    return {
        "user": usuario,
        "token": token,
        "expires_at": expires_at
    }
