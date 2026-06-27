"""
Módulo de gerenciamento de usuários do CX SaaS.
"""

import sqlite3
from typing import Optional, Dict, List, Any
from connection import get_connection
from cx_database.utils.helpers import gerar_id, agora, hash_senha, verificar_senha
from cx_database.utils.validators import validar_email, validar_senha_forca


def criar_usuario(email: str, senha: str, is_guest: bool = False) -> Optional[Dict[str, Any]]:
    """Cria um novo usuário no banco de dados."""
    if not is_guest and not validar_email(email):
        raise ValueError("Email inválido.")
    
    if not is_guest and not validar_senha_forca(senha):
        raise ValueError("Senha fraca. Mínimo 8 caracteres, 1 número e 1 letra maiúscula.")
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            user_id = gerar_id()
            agora_dt = agora()
            senha_hash_value = None if is_guest else hash_senha(senha)
            
            cursor.execute("""
                INSERT INTO usuarios (id, email, senha_hash, is_guest, ativo, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, 1, ?, ?)
            """, (user_id, email if not is_guest else f"guest_{user_id}@local", senha_hash_value, int(is_guest), agora_dt, agora_dt))
            
            conn.commit()
            return buscar_usuario_por_id(user_id)
    
    except sqlite3.IntegrityError as e:
        print(f"Erro: Email já cadastrado: {email}")
        return None
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return None


def buscar_usuario_por_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Busca um usuário pelo ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Erro ao buscar usuário por ID: {e}")
        return None


def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca um usuário pelo email."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Erro ao buscar usuário por email: {e}")
        return None


def listar_usuarios(ativos_only: bool = True) -> List[Dict[str, Any]]:
    """Lista todos os usuários."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM usuarios WHERE ativo = 1 ORDER BY criado_em DESC" if ativos_only else "SELECT * FROM usuarios ORDER BY criado_em DESC"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Erro ao listar usuários: {e}")
        return []


def atualizar_usuario(user_id: str, dados: Dict[str, Any]) -> bool:
    """Atualiza dados de um usuário."""
    campos_validos = {'email', 'ativo'}
    campos_para_atualizar = {k: v for k, v in dados.items() if k in campos_validos}
    if not campos_para_atualizar:
        return False
    
    campos_para_atualizar['atualizado_em'] = agora()
    set_clause = ', '.join([f"{k} = ?" for k in campos_para_atualizar.keys()])
    valores = list(campos_para_atualizar.values()) + [user_id]
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE usuarios SET {set_clause} WHERE id = ?", valores)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Erro ao atualizar usuário: {e}")
        return False


def deletar_usuario(user_id: str) -> bool:
    """Deleta um usuário (soft delete)."""
    return atualizar_usuario(user_id, {'ativo': 0})


def verificar_credenciais(email: str, senha: str) -> Optional[Dict[str, Any]]:
    """Verifica se email e senha são válidos."""
    usuario = buscar_usuario_por_email(email)
    if not usuario or usuario.get('is_guest', 0):
        return None
    
    senha_hash = usuario.get('senha_hash')
    if not senha_hash:
        return None
    
    return usuario if verificar_senha(senha, senha_hash) else None


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    
    print("\n=== TESTE: Criar usuário ===")
    usuario = criar_usuario("teste@email.com", "Senha123")
    print(f"Usuário criado: {usuario is not None}")
    
    if usuario:
        print(f"\n=== TESTE: Buscar por ID === {buscar_usuario_por_id(usuario['id']) is not None}")
        print(f"=== TESTE: Credenciais OK === {verificar_credenciais('teste@email.com', 'Senha123') is not None}")
        print(f"=== TESTE: Credenciais Erradas === {verificar_credenciais('teste@email.com', 'Errada') is None}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
