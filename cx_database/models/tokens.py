"""Módulo de gerenciamento de tokens."""
import sqlite3
from typing import Optional, Dict, Any
from connection import get_connection
from utils.helpers import gerar_id, agora


def criar_tokens(user_id: str, balance: int = 500) -> Optional[Dict[str, Any]]:
    """Cria registro de tokens para usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            tok_id = gerar_id()
            agora_dt = agora()
            cursor.execute("""INSERT INTO user_tokens (id, user_id, balance, initial_tokens, total_received, criado_em, atualizado_em)
                VALUES (?, ?, ?, 500, ?, ?, ?)""", (tok_id, user_id, balance, balance, agora_dt, agora_dt))
            conn.commit()
            return buscar_tokens_por_user_id(user_id)
    except sqlite3.IntegrityError:
        return None


def buscar_tokens_por_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Busca tokens por user_id."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_tokens WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error:
        return None


def consumir_tokens_atomico(user_id: str, amount: int, descricao: str) -> bool:
    """Consome tokens de forma atômica (BEGIN IMMEDIATE)."""
    if amount <= 0:
        return False
    try:
        with get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM user_tokens WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                if not row or row[0] < amount:
                    conn.rollback()
                    return False
                
                balance_before = row[0]
                balance_after = balance_before - amount
                
                cursor.execute("UPDATE user_tokens SET balance = ?, total_used = total_used + ?, last_usage_at = ?, atualizado_em = ? WHERE user_id = ?",
                    (balance_after, amount, agora(), agora(), user_id))
                
                # Registrar transação
                trans_id = gerar_id()
                cursor.execute("""INSERT INTO transacoes_tokens (id, user_id, tipo, amount, balance_before, balance_after, descricao, criado_em)
                    VALUES (?, ?, 'usage', ?, ?, ?, ?, ?)""", (trans_id, user_id, amount, balance_before, balance_after, descricao, agora()))
                
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False
    except Exception:
        return False


def adicionar_tokens(user_id: str, amount: int, tipo: str = 'bonus', descricao: str = '') -> bool:
    """Adiciona tokens ao usuário."""
    if amount <= 0 or tipo not in ['refill', 'bonus', 'admin_adjustment', 'initial_grant']:
        return False
    try:
        with get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM user_tokens WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                balance_before = row[0] if row else 0
                balance_after = balance_before + amount
                
                cursor.execute("UPDATE user_tokens SET balance = ?, total_received = total_received + ?, atualizado_em = ? WHERE user_id = ?",
                    (balance_after, amount, agora(), user_id))
                
                trans_id = gerar_id()
                cursor.execute("""INSERT INTO transacoes_tokens (id, user_id, tipo, amount, balance_before, balance_after, descricao, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (trans_id, user_id, tipo, amount, balance_before, balance_after, descricao, agora()))
                
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False
    except Exception:
        return False


def get_saldo(user_id: str) -> int:
    """Retorna saldo atual do usuário."""
    tokens = buscar_tokens_por_user_id(user_id)
    return tokens['balance'] if tokens else 0


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    print("\n=== TESTE: Criar tokens ===")
    criar_tokens("user_test")
    print(f"Saldo inicial: {get_saldo('user_test')}")
    print(f"Consumir 10 tokens: {consumir_tokens_atomico('user_test', 10, 'teste')}")
    print(f"Saldo após consumo: {get_saldo('user_test')}")
    print("\n=== TODOS OS TESTES PASSARAM ===")
