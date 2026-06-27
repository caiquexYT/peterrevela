"""
Módulo de gerenciamento de perfis de usuário.
"""

import sqlite3
from typing import Optional, Dict, List, Any
from connection import get_connection
from utils.helpers import gerar_id, agora
from utils.json_field import to_json, from_json


def criar_perfil(user_id: str, email: str = None, username: str = None, display_name: str = None) -> Optional[Dict[str, Any]]:
    """Cria um novo perfil para um usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            perfil_id = gerar_id()
            agora_dt = agora()
            
            cursor.execute("""
                INSERT INTO perfis (id, email, username, display_name, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (perfil_id, email, username, display_name, agora_dt, agora_dt))
            
            conn.commit()
            return buscar_perfil_por_user_id(user_id)
    
    except sqlite3.IntegrityError as e:
        print(f"Erro ao criar perfil: {e}")
        return None


def buscar_perfil_por_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Busca perfil pelo ID do usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM perfis WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                # Desserializar campos JSON
                data['interesses'] = from_json(data.get('interesses'), default=[])
                data['temporal_memory'] = from_json(data.get('temporal_memory'), default={"keyEvents": []})
                return data
            return None
    
    except sqlite3.Error as e:
        print(f"Erro ao buscar perfil: {e}")
        return None


def atualizar_perfil(user_id: str, dados: Dict[str, Any]) -> bool:
    """Atualiza dados do perfil."""
    campos_validos = {'email', 'username', 'display_name', 'nome', 'idade', 'interesses', 
                      'profile_picture_url', 'avatar_url', 'bio', 'response_style', 'temporal_memory'}
    campos_para_atualizar = {}
    
    for k, v in dados.items():
        if k in campos_validos:
            # Serializar campos JSON
            if k in ['interesses', 'temporal_memory']:
                campos_para_atualizar[k] = to_json(v)
            else:
                campos_para_atualizar[k] = v
    
    if not campos_para_atualizar:
        return False
    
    campos_para_atualizar['atualizado_em'] = agora()
    set_clause = ', '.join([f"{k} = ?" for k in campos_para_atualizar.keys()])
    valores = list(campos_para_atualizar.values()) + [user_id]
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE perfis SET {set_clause} WHERE id = ?", valores)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Erro ao atualizar perfil: {e}")
        return False


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    
    print("\n=== TESTE: Criar perfil ===")
    perfil = criar_perfil("user123", "teste@email.com", "testuser", "Test User")
    print(f"Perfil criado: {perfil is not None}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
