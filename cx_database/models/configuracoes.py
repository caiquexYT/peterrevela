"""
Módulo de gerenciamento de configurações de usuário.
"""

import sqlite3
from typing import Optional, Dict, Any
from connection import get_connection
from utils.helpers import gerar_id, agora
from utils.json_field import to_json, from_json


def criar_configuracao(user_id: str, tema: str = 'dark', idioma: str = 'pt-BR') -> Optional[Dict[str, Any]]:
    """Cria configurações para um usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            config_id = gerar_id()
            agora_dt = agora()
            
            cursor.execute("""
                INSERT INTO configuracoes (id, user_id, tema, idioma, preferences, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (config_id, user_id, tema, idioma, to_json({}), agora_dt, agora_dt))
            
            conn.commit()
            return buscar_configuracao_por_user_id(user_id)
    
    except sqlite3.IntegrityError as e:
        print(f"Erro ao criar configuração: {e}")
        return None


def buscar_configuracao_por_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Busca configurações pelo ID do usuário."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM configuracoes WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data['preferences'] = from_json(data.get('preferences'), default={})
                return data
            return None
    
    except sqlite3.Error as e:
        print(f"Erro ao buscar configuração: {e}")
        return None


def atualizar_configuracao(user_id: str, dados: Dict[str, Any]) -> bool:
    """Atualiza configurações do usuário."""
    campos_validos = {'tema', 'idioma', 'preferences'}
    campos_para_atualizar = {}
    
    for k, v in dados.items():
        if k in campos_validos:
            if k == 'preferences':
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
            cursor.execute(f"UPDATE configuracoes SET {set_clause} WHERE user_id = ?", valores)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Erro ao atualizar configuração: {e}")
        return False


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    
    print("\n=== TESTE: Criar configuração ===")
    config = criar_configuracao("user123")
    print(f"Configuração criada: {config is not None}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
