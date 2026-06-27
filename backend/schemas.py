"""
Schemas Pydantic para validação de dados da API CxIA.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============ AUTH ============

class RegistroInput(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=8, max_length=100)


class LoginInput(BaseModel):
    email: EmailStr
    senha: str


class AuthResponse(BaseModel):
    user: Dict[str, Any]
    token: str
    expires_at: str


# ============ USUÁRIOS ============

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    photo_url: Optional[str] = None


class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str
    photo_url: Optional[str] = None
    provider: str
    is_guest: bool
    criado_em: str
    atualizado_em: str


# ============ CONVERSAS ============

class CriarConversaInput(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)


class AtualizarConversaInput(BaseModel):
    titulo: Optional[str] = None
    is_private: Optional[bool] = None


class ConversaResponse(BaseModel):
    id: str
    user_id: str
    titulo: str
    modo: str
    is_private: bool
    criado_em: str
    atualizado_em: str


class ListarConversasResponse(BaseModel):
    conversas: List[ConversaResponse]


# ============ MENSAGENS ============

class CriarMensagemInput(BaseModel):
    conversa_id: str
    role: str = Field(..., pattern="^(user|assistant|system|model)$")
    content: str
    thinking_time: Optional[float] = None
    attachment: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None


class MensagemResponse(BaseModel):
    id: str
    conversa_id: str
    role: str
    content: str
    thinking_time: Optional[float] = None
    criado_em: str


class ListarMensagensResponse(BaseModel):
    mensagens: List[MensagemResponse]


# ============ TOKENS ============

class ConsumoTokensInput(BaseModel):
    amount: int = Field(..., gt=0)
    descricao: str


class TokenSaldoResponse(BaseModel):
    tokens_usados: int
    limite_tokens: int
    tokens_restantes: int
    janela_inicio: str
    plano: str


class ConsumoResult(BaseModel):
    allowed: bool
    tokens_restantes: int
    reset_in_ms: Optional[int] = None


class UpgradePlanoInput(BaseModel):
    novo_plano: str = Field(..., pattern="^(free|premium|premium_max)$")


# ============ HEALTH CHECK ============

class HealthResponse(BaseModel):
    status: str
    version: str
