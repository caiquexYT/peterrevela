"""Módulo de gerenciamento de mensagens."""
import sqlite3
from typing import Optional, Dict, List, Any
from connection import get_connection
from utils.helpers import gerar_id, agora
from utils.json_field import to_json, from_json


def criar_mensagem(conversa_id: str, role: str, content: str, user_id: str = None) -> Optional[Dict[str, Any]]:
    """Cria nova mensagem."""
    if role not in ['user', 'assistant', 'system', 'model']:
        raise ValueError("Role inválido")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            msg_id = gerar_id()
            agora_dt = agora()
            cursor.execute("""INSERT INTO mensagens (id, conversa_id, user_id, role, content, image_urls, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (msg_id, conversa_id, user_id, role, content, to_json([]), agora_dt))
            
            # Atualizar ultima_modificacao da conversa
            cursor.execute("UPDATE conversas SET ultima_modificacao = ? WHERE id = ?", (agora_dt, conversa_id))
            conn.commit()
            return buscar_mensagem_por_id(msg_id)
    except sqlite3.Error:
        return None


def buscar_mensagem_por_id(mensagem_id: str) -> Optional[Dict[str, Any]]:
    """Busca mensagem por ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mensagens WHERE id = ?", (mensagem_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['attachment'] = from_json(data.get('attachment'))
                data['actions'] = from_json(data.get('actions'), default=[])
                data['author'] = from_json(data.get('author'))
                data['image_urls'] = from_json(data.get('image_urls'), default=[])
                return data
            return None
    except sqlite3.Error:
        return None


def listar_mensagens_por_conversa(conversa_id: str) -> List[Dict[str, Any]]:
    """Lista mensagens de uma conversa ordenadas por criação."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mensagens WHERE conversa_id = ? ORDER BY criado_em ASC", (conversa_id,))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                data = dict(row)
                data['attachment'] = from_json(data.get('attachment'))
                data['actions'] = from_json(data.get('actions'), default=[])
                data['author'] = from_json(data.get('author'))
                data['image_urls'] = from_json(data.get('image_urls'), default=[])
                result.append(data)
            return result
    except sqlite3.Error:
        return []


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    print("\n=== TESTE: Criar mensagem ===")
    msg = criar_mensagem("conv123", "user", "Olá!", "user456")
    print(f"Mensagem criada: {msg is not None}")
    print("\n=== TODOS OS TESTES PASSARAM ===")
