"""
Módulo de funções auxiliares para o sistema CX.

Este módulo contém utilitários gerais como geração de IDs únicos,
formatação de datas e manipulação de senhas com hash.
"""

import uuid
import hashlib
from datetime import datetime


def gerar_id() -> str:
    """
    Gera um ID único universal (UUID4) como string.

    Returns:
        str: UUID4 no formato padrão (ex: '550e8400-e29b-41d4-a716-446655440000')
    """
    return str(uuid.uuid4())


def agora() -> str:
    """
    Retorna a data e hora atual no formato ISO 8601.

    Returns:
        str: Datetime atual no formato 'YYYY-MM-DDTHH:MM:SS'
    
    Example:
        >>> agora()
        '2025-01-20T14:30:00'
    """
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def hash_senha(senha: str) -> str:
    """
    Gera o hash SHA-256 de uma senha.

    Args:
        senha (str): Senha em texto puro.

    Returns:
        str: Hash hexadecimal da senha (64 caracteres).
    
    Example:
        >>> hash_senha("minha_senha")
        'a1b2c3...'  # hash de 64 caracteres
    """
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash armazenado.

    Args:
        senha (str): Senha em texto puro fornecida pelo usuário.
        hash_salvo (str): Hash SHA-256 armazenado no banco de dados.

    Returns:
        bool: True se a senha corresponder ao hash, False caso contrário.
    
    Example:
        >>> hash = hash_senha("minha_senha")
        >>> verificar_senha("minha_senha", hash)
        True
        >>> verificar_senha("senha_errada", hash)
        False
    """
    hash_gerado = hash_senha(senha)
    return hash_gerado == hash_salvo


if __name__ == "__main__":
    print("=== TESTE: gerar_id ===")
    id1 = gerar_id()
    id2 = gerar_id()
    print(f"ID 1: {id1}")
    print(f"ID 2: {id2}")
    print(f"IDs únicos: {id1 != id2}")
    
    print("\n=== TESTE: agora ===")
    data_atual = agora()
    print(f"Data/hora atual: {data_atual}")
    
    print("\n=== TESTE: hash_senha e verificar_senha ===")
    senha_teste = "MinhaSenha123!"
    hash_resultante = hash_senha(senha_teste)
    print(f"Senha original: {senha_teste}")
    print(f"Hash gerado: {hash_resultante}")
    print(f"Tamanho do hash: {len(hash_resultante)} caracteres")
    
    print("\nVerificando senha correta:")
    resultado_correto = verificar_senha(senha_teste, hash_resultante)
    print(f"Resultado: {resultado_correto}")
    
    print("\nVerificando senha incorreta:")
    resultado_incorreto = verificar_senha("SenhaErrada", hash_resultante)
    print(f"Resultado: {resultado_incorreto}")
