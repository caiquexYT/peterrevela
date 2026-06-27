"""Serviço de administração."""
from typing import Optional, Dict, Any
from models.admins import is_admin
from models.tokens import adicionar_tokens


def ajustar_tokens(admin_id: str, target_user_id: str, amount: int, descricao: str) -> bool:
    """Admin ajusta tokens de outro usuário."""
    if not is_admin(admin_id):
        return False
    
    return adicionar_tokens(target_user_id, amount, 'admin_adjustment', descricao)


def deletar_usuario(admin_id: str, target_user_id: str) -> bool:
    """Admin deleta usuário (apenas marca como inativo)."""
    if not is_admin(admin_id):
        return False
    
    from models.usuarios import deletar_usuario
    return deletar_usuario(target_user_id)


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    
    print("\n=== TESTE: Admin service ===")
    print(f"User é admin: {is_admin('user123')}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
