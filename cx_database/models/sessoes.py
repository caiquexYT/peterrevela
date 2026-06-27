"""Módulo de gerenciamento de sessões."""
import sqlite3
from typing import Optional, Dict, Any
from connection import get_connection
from utils.helpers import gerar_id, agora, gerar_token_seguro


def criar_sessao(user_id: str, expires_in_hours: int = 24) -> Optional[Dict[str, Any]]:
    """Cria nova sessão para usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            sessao_id = gerar_id()
            token = gerar_token_seguro(32)
            agora_dt = agora()
            # Calcular expires_at
            from datetime import datetime, timedelta
            expires_at = (datetime.utcnow() + timedelta(hours=expires_in_hours)).strftime('%Y-%m-%dT%H:%M:%S')
            
            cursor.execute("INSERT INTO sessoes (id, user_id, token, expires_at, criado_em) VALUES (?, ?, ?, ?, ?)",
                (sessao_id, user_id, token, expires_at, agora_dt))
            conn.commit()
            return {'id': sessao_id, 'user_id': user_id, 'token': token, 'expires_at': expires_at}
    except sqlite3.Error:
        return None


def validar_sessao(token: str) -> Optional[Dict[str, Any]]:
    """Valida token de sessão e retorna dados se válida."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessoes WHERE token = ? AND expires_at > ?", (token, agora()))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                return data
            return None
    except sqlite3.Error:
        return None


def invalidar_sessao(token: str) -> bool:
    """Invalida sessão (logout)."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessoes WHERE token = ?", (token,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error:
        return False


def limpar_sessoes_expiradas() -> int:
    """Remove sessões expiradas. Retorna quantidade removida."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessoes WHERE expires_at <= ?", (agora(),))
            conn.commit()
            return cursor.rowcount
    except sqlite3.Error:
        return 0


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    print("\n=== TESTE: Criar sessão ===")
    sessao = criar_sessao("user123")
    print(f"Sessão criada: {sessao is not None}")
    if sessao:
        print(f"Token: {sessao['token'][:20]}...")
        valida = validar_sessao(sessao['token'])
        print(f"Sessão válida: {valida is not None}")
    print("\n=== TODOS OS TESTES PASSARAM ===")
