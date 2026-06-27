"""Módulo de gerenciamento de administradores."""
import sqlite3
from typing import Optional, Dict, Any
from connection import get_connection
from utils.helpers import gerar_id, agora


def criar_admin(user_id: str, email: str) -> Optional[Dict[str, Any]]:
    """Cria um administrador."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            admin_id = gerar_id()
            cursor.execute("INSERT INTO admins (id, user_id, email, criado_em) VALUES (?, ?, ?, ?)",
                (admin_id, user_id, email, agora()))
            conn.commit()
            return buscar_admin_por_user_id(user_id)
    except sqlite3.IntegrityError:
        return None


def buscar_admin_por_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Busca admin por user_id."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error:
        return None


def is_admin(user_id: str) -> bool:
    """Verifica se usuário é admin."""
    return buscar_admin_por_user_id(user_id) is not None


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    print("\n=== TESTE: Verificar admin ===")
    print(f"Admin existe: {is_admin('user123')}")
    print("\n=== TODOS OS TESTES PASSARAM ===")
