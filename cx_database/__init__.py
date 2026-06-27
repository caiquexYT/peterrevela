"""
CX Database - Banco de dados local para CX SaaS.

Este módulo fornece toda a camada de dados para o sistema CX SaaS,
replicando funcionalidades do Supabase/PostgreSQL usando SQLite puro.

Usage:
    from cx_database.services.auth_service import registrar_usuario_completo, login
    from cx_database.services.token_service import consumir_tokens, get_saldo
    from cx_database.models import criar_conversa, listar_mensagens_por_conversa
"""

__version__ = "1.0.0"

from .setup import setup_completo, resetar_banco, verificar_setup
from .connection import get_connection, DATABASE_PATH

__all__ = [
    'setup_completo',
    'resetar_banco',
    'verificar_setup',
    'get_connection',
    'DATABASE_PATH',
]
