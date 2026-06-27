"""
Utilitários auxiliares para o backend CxIA.
Funções para geração de IDs, datas e hash de senhas.
"""

import uuid
import hashlib
from datetime import datetime
from typing import Optional


def gerar_id() -> str:
    """
    Gera um UUID4 único como string.
    
    Returns:
        str: UUID no formato padrão (ex: '550e8400-e29b-41d4-a716-446655440000')
    """
    return str(uuid.uuid4())


def agora() -> str:
    """
    Retorna a data/hora atual em formato ISO 8601.
    
    Returns:
        str: Data/hora no formato 'YYYY-MM-DDTHH:MM:SS'
    """
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def hash_senha(senha: str) -> str:
    """
    Gera hash SHA-256 da senha fornecida.
    
    Args:
        senha (str): Senha em texto puro.
    
    Returns:
        str: Hash hexadecimal da senha.
    """
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.
    
    Args:
        senha (str): Senha em texto puro para verificação.
        hash_salvo (str): Hash SHA-256 armazenado no banco.
    
    Returns:
        bool: True se a senha corresponder ao hash, False caso contrário.
    """
    return hash_senha(senha) == hash_salvo
