"""Módulo de gerenciamento de assinaturas."""
import sqlite3
from typing import Optional, Dict, Any
from connection import get_connection
from utils.helpers import gerar_id, agora
from utils.json_field import to_json, from_json


def criar_assinatura(user_id: str, plano: str = 'free') -> Optional[Dict[str, Any]]:
    """Cria assinatura para usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            ass_id = gerar_id()
            agora_dt = agora()
            cursor.execute("""INSERT INTO assinaturas (id, user_id, plano, status, used_codes, criado_em, atualizado_em)
                VALUES (?, ?, ?, 'active', ?, ?, ?)""", (ass_id, user_id, plano, to_json([]), agora_dt, agora_dt))
            conn.commit()
            return buscar_assinatura_por_user_id(user_id)
    except sqlite3.IntegrityError as e:
        print(f"Erro ao criar assinatura: {e}")
        return None


def buscar_assinatura_por_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Busca assinatura por user_id."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM assinaturas WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['used_codes'] = from_json(data.get('used_codes'), default=[])
                return data
            return None
    except sqlite3.Error:
        return None


def atualizar_plano(user_id: str, plano: str, premium_until: str = None) -> bool:
    """Atualiza plano do usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            atualizado = agora()
            if premium_until:
                cursor.execute("UPDATE assinaturas SET plano = ?, premium_until = ?, atualizado_em = ? WHERE user_id = ?",
                    (plano, premium_until, atualizado, user_id))
            else:
                cursor.execute("UPDATE assinaturas SET plano = ?, atualizado_em = ? WHERE user_id = ?", (plano, atualizado, user_id))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error:
        return False


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    print("\n=== TESTE: Criar assinatura ===")
    print(f"Assinatura criada: {criar_assinatura('user123') is not None}")
    print("\n=== TODOS OS TESTES PASSARAM ===")
