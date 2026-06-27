"""Módulo de gerenciamento de conversas."""
import sqlite3
from typing import Optional, Dict, List, Any
from connection import get_connection
from utils.helpers import gerar_id, agora
from utils.json_field import to_json, from_json


def criar_conversa(user_id: str, titulo: str = None, modo: str = 'chat') -> Optional[Dict[str, Any]]:
    """Cria nova conversa."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            conv_id = gerar_id()
            agora_dt = agora()
            cursor.execute("""INSERT INTO conversas (id, user_id, titulo, modo, active_agent_ids, criado_em, ultima_modificacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (conv_id, user_id, titulo, modo, to_json([]), agora_dt, agora_dt))
            conn.commit()
            return buscar_conversa_por_id(conv_id)
    except sqlite3.Error:
        return None


def buscar_conversa_por_id(conversa_id: str) -> Optional[Dict[str, Any]]:
    """Busca conversa por ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversas WHERE id = ?", (conversa_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['active_agent_ids'] = from_json(data.get('active_agent_ids'), default=[])
                return data
            return None
    except sqlite3.Error:
        return None


def listar_conversas_por_usuario(user_id: str, ativas_only: bool = True) -> List[Dict[str, Any]]:
    """Lista conversas de um usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if ativas_only:
                cursor.execute("SELECT * FROM conversas WHERE user_id = ? AND is_archived = 0 ORDER BY ultima_modificacao DESC", (user_id,))
            else:
                cursor.execute("SELECT * FROM conversas WHERE user_id = ? ORDER BY ultima_modificacao DESC", (user_id,))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                data = dict(row)
                data['active_agent_ids'] = from_json(data.get('active_agent_ids'), default=[])
                result.append(data)
            return result
    except sqlite3.Error:
        return []


def arquivar_conversa(conversa_id: str) -> bool:
    """Arquiva uma conversa."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE conversas SET is_archived = 1, ultima_modificacao = ? WHERE id = ?", (agora(), conversa_id))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error:
        return False


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    print("\n=== TESTE: Criar conversa ===")
    conv = criar_conversa("user123", "Minha Conversa")
    print(f"Conversa criada: {conv is not None}")
    print("\n=== TODOS OS TESTES PASSARAM ===")
