"""
Módulo de validação de dados para o backend CxIA.
Funções para validar email, senha e campos obrigatórios.
"""

import re
from typing import List, Dict, Any


def validar_email(email: str) -> bool:
    """
    Valida o formato de um endereço de email.
    
    Args:
        email (str): Endereço de email para validação.
    
    Returns:
        bool: True se o email tiver formato válido, False caso contrário.
    """
    if not email or not isinstance(email, str):
        return False
    
    # Padrão regex para validação de email
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))


def validar_senha_forca(senha: str) -> bool:
    """
    Valida a força da senha.
    
    Requisitos:
    - Mínimo 8 caracteres
    - Pelo menos 1 número
    - Pelo menos 1 letra maiúscula
    
    Args:
        senha (str): Senha em texto puro para validação.
    
    Returns:
        bool: True se a senha atender aos requisitos, False caso contrário.
    """
    if not senha or not isinstance(senha, str):
        return False
    
    if len(senha) < 8:
        return False
    
    if not re.search(r'\d', senha):
        return False
    
    if not re.search(r'[A-Z]', senha):
        return False
    
    return True


def validar_campos_obrigatorios(dados: Dict[str, Any], campos: List[str]) -> bool:
    """
    Verifica se todos os campos obrigatórios estão presentes e não vazios.
    
    Args:
        dados (Dict[str, Any]): Dicionário com os dados a serem validados.
        campos (List[str]): Lista de nomes de campos obrigatórios.
    
    Returns:
        bool: True se todos os campos estiverem presentes e não vazios, False caso contrário.
    """
    if not dados or not isinstance(dados, dict):
        return False
    
    if not campos or not isinstance(campos, list):
        return False
    
    for campo in campos:
        if campo not in dados:
            return False
        
        valor = dados[campo]
        
        # Verifica se é None
        if valor is None:
            return False
        
        # Verifica se é string vazia
        if isinstance(valor, str) and not valor.strip():
            return False
        
        # Verifica se é lista vazia (quando aplicável)
        if isinstance(valor, list) and len(valor) == 0:
            return False
    
    return True
