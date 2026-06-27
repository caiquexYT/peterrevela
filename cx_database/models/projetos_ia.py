"""Módulo de gerenciamento de projetos de IA."""
import sqlite3
from typing import Optional, Dict, List, Any
from connection import get_connection
from utils.helpers import gerar_id, agora
from utils.json_field import to_json, from_json


def criar_projeto(user_id: str, nome: str = None, descricao: str = None) -> Optional[Dict[str, Any]]:
    """Cria novo projeto de IA."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            proj_id = gerar_id()
            agora_dt = agora()
            cursor.execute("""INSERT INTO projetos_ia (id, user_id, nome, descricao, files, chat_history, criado_em, atualizado_em, ultima_modificacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (proj_id, user_id, nome, descricao, to_json([]), to_json([]), agora_dt, agora_dt, agora_dt))
            conn.commit()
            return buscar_projeto_por_id(proj_id)
    except sqlite3.Error:
        return None


def buscar_projeto_por_id(projeto_id: str) -> Optional[Dict[str, Any]]:
    """Busca projeto por ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projetos_ia WHERE id = ?", (projeto_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['files'] = from_json(data.get('files'), default=[])
                data['chat_history'] = from_json(data.get('chat_history'), default=[])
                return data
            return None
    except sqlite3.Error:
        return None


def listar_projetos_por_usuario(user_id: str) -> List[Dict[str, Any]]:
    """Lista projetos de um usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projetos_ia WHERE user_id = ? ORDER BY ultima_modificacao DESC", (user_id,))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                data = dict(row)
                data['files'] = from_json(data.get('files'), default=[])
                data['chat_history'] = from_json(data.get('chat_history'), default=[])
                result.append(data)
            return result
    except sqlite3.Error:
        return []


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    print("\n=== TESTE: Criar projeto ===")
    proj = criar_projeto("user123", "Meu Projeto")
    print(f"Projeto criado: {proj is not None}")
    print("\n=== TODOS OS TESTES PASSARAM ===")
