"""
Utilitários para geração e verificação de tokens JWT.
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


# Chave secreta para JWT (deve vir de variável de ambiente em produção)
JWT_SECRET = os.getenv("JWT_SECRET", "cxia-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 30


def criar_token(user_id: str, email: str, extra_data: Dict[str, Any] = None) -> str:
    """
    Cria um token JWT para autenticação do usuário.
    
    Args:
        user_id (str): ID único do usuário.
        email (str): Email do usuário.
        extra_data (Dict, opcional): Dados adicionais para incluir no token.
    
    Returns:
        str: Token JWT codificado.
    """
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    if extra_data:
        payload.update(extra_data)
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verificar_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica e decodifica um token JWT.
    
    Args:
        token (str): Token JWT a ser verificado.
    
    Returns:
        dict | None: Payload do token se válido, None se inválido ou expirado.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Token inválido: {e}")
        return None


def refresh_token(token: str) -> Optional[str]:
    """
    Renova um token JWT válido, estendendo sua validade.
    
    Args:
        token (str): Token JWT atual.
    
    Returns:
        str | None: Novo token renovado, ou None se o token original for inválido.
    """
    payload = verificar_token(token)
    
    if not payload:
        return None
    
    # Criar novo token com os mesmos dados
    return criar_token(
        user_id=payload["user_id"],
        email=payload["email"]
    )


if __name__ == "__main__":
    # Testes manuais
    print("=== TESTE: Criar token ===")
    token = criar_token("user-123", "teste@email.com", {"plano": "free"})
    print(f"Token gerado: {token[:50]}...")
    
    print("\n=== TESTE: Verificar token ===")
    payload = verificar_token(token)
    print(f"Payload: {payload}")
    
    print("\n=== TESTE: Token inválido ===")
    invalido = verificar_token("token-invalido")
    print(f"Resultado: {invalido}")
    
    print("\n=== TESTE: Refresh token ===")
    novo_token = refresh_token(token)
    print(f"Novo token: {novo_token[:50]}..." if novo_token else "Falha no refresh")
