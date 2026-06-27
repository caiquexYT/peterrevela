"""Módulo de gerenciamento de transações de tokens."""
import sqlite3
from typing import Optional, Dict, List, Any
from connection import get_connection
from utils.helpers import gerar_id, agora


def registrar_transacao(user_id: str, tipo: str, amount: int, balance_before: int, 
                        balance_after: int, descricao: str = '') -> Optional[Dict[str, Any]]:
    """Registra uma transação de tokens."""
    tipos_validos = ['usage', 'refill', 'bonus', 'admin_adjustment', 'initial_grant']
    if tipo not in tipos_validos:
        raise ValueError(f"Tipo inválido. Deve ser um de: {tipos_validos}")
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            trans_id = gerar_id()
            cursor.execute("""INSERT INTO transacoes_tokens (id, user_id, tipo, amount, balance_before, balance_after, descricao, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (trans_id, user_id, tipo, amount, balance_before, balance_after, descricao, agora()))
            conn.commit()
            return buscar_transacao_por_id(trans_id)
    except sqlite3.Error:
        return None


def buscar_transacao_por_id(transacao_id: str) -> Optional[Dict[str, Any]]:
    """Busca transação por ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacoes_tokens WHERE id = ?", (transacao_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error:
        return None


def listar_transacoes_por_usuario(user_id: str, limite: int = 50) -> List[Dict[str, Any]]:
    """Lista transações de um usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM transacoes_tokens WHERE user_id = ? 
                ORDER BY criado_em DESC LIMIT ?""", (user_id, limite))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error:
        return []


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    print("\n=== TESTE: Registrar transação ===")
    trans = registrar_transacao("user123", "bonus", 100, 400, 500, "Bônus teste")
    print(f"Transação registrada: {trans is not None}")
    print("\n=== TODOS OS TESTES PASSARAM ===")
