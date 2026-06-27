"""
Modelo de dados para usuários do CxIA.
CRUD completo para a tabela usuarios.
"""

import sqlite3
from typing import Optional, Dict, List, Any
from datetime import datetime

from database import get_db
from utils.helpers import gerar_id, agora, hash_senha


def criar_usuario(
    nome: str,
    email: str,
    senha: str = None,
    photo_url: str = None,
    provider: str = "email",
    is_guest: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Cria um novo usuário no banco de dados.
    
    Args:
        nome (str): Nome do usuário.
        email (str): Email único do usuário.
        senha (str, opcional): Senha em texto puro (será convertida para hash).
        photo_url (str, opcional): URL da foto do usuário.
        provider (str): Provedor de autenticação ('email', 'google', 'guest').
        is_guest (bool): Se é um usuário convidado.
    
    Returns:
        dict: Dados do usuário criado, ou None em caso de erro.
    """
    try:
        with get_db() as conn:
            usuario_id = gerar_id()
            data_atual = agora()
            
            # Hash da senha (se fornecida)
            senha_hash = hash_senha(senha) if senha else None
            
            conn.execute("""
                INSERT INTO usuarios (id, nome, email, senha_hash, photo_url, provider, is_guest, ativo, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (usuario_id, nome, email, senha_hash, photo_url, provider, 1 if not is_guest else 0, data_atual, data_atual))
            
            conn.commit()
            
            return buscar_usuario_por_id(usuario_id)
    
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade ao criar usuário (email duplicado?): {e}")
        return None
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return None


def buscar_usuario_por_id(usuario_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca um usuário pelo ID.
    
    Args:
        usuario_id (str): ID do usuário.
    
    Returns:
        dict: Dados do usuário, ou None se não encontrado.
    """
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM usuarios WHERE id = ? AND ativo = 1",
                (usuario_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    except Exception as e:
        print(f"Erro ao buscar usuário por ID: {e}")
        return None


def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca um usuário pelo email.
    
    Args:
        email (str): Email do usuário.
    
    Returns:
        dict: Dados do usuário, ou None se não encontrado.
    """
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM usuarios WHERE email = ? AND ativo = 1",
                (email,)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    except Exception as e:
        print(f"Erro ao buscar usuário por email: {e}")
        return None


def listar_usuarios(ativos: bool = True) -> List[Dict[str, Any]]:
    """
    Lista todos os usuários.
    
    Args:
        ativos (bool): Se True, retorna apenas usuários ativos.
    
    Returns:
        list: Lista de dicionários com dados dos usuários.
    """
    try:
        with get_db() as conn:
            if ativos:
                cursor = conn.execute("SELECT * FROM usuarios WHERE ativo = 1 ORDER BY criado_em DESC")
            else:
                cursor = conn.execute("SELECT * FROM usuarios ORDER BY criado_em DESC")
            
            return [dict(row) for row in cursor.fetchall()]
    
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        return []


def atualizar_usuario(
    usuario_id: str,
    nome: str = None,
    email: str = None,
    photo_url: str = None,
    ativo: int = None
) -> Optional[Dict[str, Any]]:
    """
    Atualiza dados de um usuário.
    
    Args:
        usuario_id (str): ID do usuário a ser atualizado.
        nome (str, opcional): Novo nome.
        email (str, opcional): Novo email.
        photo_url (str, opcional): Nova URL da foto.
        ativo (int, opcional): Status de atividade (0 ou 1).
    
    Returns:
        dict: Dados atualizados do usuário, ou None se não encontrado.
    """
    try:
        with get_db() as conn:
            updates = []
            values = []
            
            if nome is not None:
                updates.append("nome = ?")
                values.append(nome)
            
            if email is not None:
                updates.append("email = ?")
                values.append(email)
            
            if photo_url is not None:
                updates.append("photo_url = ?")
                values.append(photo_url)
            
            if ativo is not None:
                updates.append("ativo = ?")
                values.append(ativo)
            
            if not updates:
                return buscar_usuario_por_id(usuario_id)
            
            updates.append("atualizado_em = ?")
            values.append(agora())
            values.append(usuario_id)
            
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, values)
            conn.commit()
            
            return buscar_usuario_por_id(usuario_id)
    
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade ao atualizar usuário (email duplicado?): {e}")
        return None
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        return None


def deletar_usuario(usuario_id: str) -> bool:
    """
    Deleta (desativa) um usuário.
    
    Args:
        usuario_id (str): ID do usuário a ser deletado.
    
    Returns:
        bool: True se deletado com sucesso, False caso contrário.
    """
    try:
        with get_db() as conn:
            # Soft delete - apenas marca como inativo
            conn.execute("""
                UPDATE usuarios SET ativo = 0, atualizado_em = ? WHERE id = ?
            """, (agora(), usuario_id))
            
            conn.commit()
            return True
    
    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        return False


def verificar_senha_usuario(email: str, senha: str) -> Optional[Dict[str, Any]]:
    """
    Verifica se a senha fornecida corresponde ao usuário com o email dado.
    
    Args:
        email (str): Email do usuário.
        senha (str): Senha em texto puro para verificação.
    
    Returns:
        dict: Dados do usuário se a senha estiver correta, None caso contrário.
    """
    usuario = buscar_usuario_por_email(email)
    
    if not usuario:
        return None
    
    senha_hash = usuario.get("senha_hash")
    
    if not senha_hash:
        # Usuário sem senha (ex: login via Google)
        return None
    
    if hash_senha(senha) == senha_hash:
        return usuario
    
    return None


if __name__ == "__main__":
    from models import criar_todas_as_tabelas
    
    print("=== TESTE: Criar usuário ===")
    usuario = criar_usuario("João Silva", "joao@email.com", "Senha123")
    print(f"Usuário criado: {usuario}")
    
    print("\n=== TESTE: Buscar por ID ===")
    if usuario:
        encontrado = buscar_usuario_por_id(usuario["id"])
        print(f"Buscado por ID: {encontrado}")
    
    print("\n=== TESTE: Buscar por email ===")
    por_email = buscar_usuario_por_email("joao@email.com")
    print(f"Buscado por email: {por_email}")
    
    print("\n=== TESTE: Verificar senha ===")
    verificado = verificar_senha_usuario("joao@email.com", "Senha123")
    print(f"Senha verificada: {verificado is not None}")
    
    print("\n=== TESTE: Atualizar usuário ===")
    if usuario:
        atualizado = atualizar_usuario(usuario["id"], nome="João Silva Atualizado")
        print(f"Atualizado: {atualizado}")
    
    print("\n=== TESTE: Listar usuários ===")
    lista = listar_usuarios()
    print(f"Total de usuários: {len(lista)}")
    
    print("\n=== TODOS OS TESTES CONCLUÍDOS ===")
