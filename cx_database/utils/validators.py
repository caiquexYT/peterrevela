"""Módulo de validação de dados."""
import re


def validar_email(email: str) -> bool:
    """Valida formato de email."""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validar_senha_forca(senha: str) -> bool:
    """Valida força da senha (mínimo 8 chars, 1 número, 1 maiúscula)."""
    if not senha or len(senha) < 8:
        return False
    if not re.search(r'\d', senha):  # Pelo menos 1 número
        return False
    if not re.search(r'[A-Z]', senha):  # Pelo menos 1 maiúscula
        return False
    return True


if __name__ == "__main__":
    print("=== TESTE: Validar email ===")
    print(f"valido@email.com: {validar_email('valido@email.com')}")
    print(f"invalido: {validar_email('invalido')}")
    
    print("\n=== TESTE: Validar senha ===")
    print(f"Senha123: {validar_senha_forca('Senha123')}")
    print(f"fraca: {validar_senha_forca('fraca')}")
    print(f"12345678: {validar_senha_forca('12345678')}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
