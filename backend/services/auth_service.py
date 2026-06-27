"""
Serviço de autenticação para o CxIA.
Gerencia registro, login, logout e sessões de usuários.
Replica o trigger handle_new_user() do Supabase em Python.
"""

import sqlite3
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from database import get_db
from utils.helpers import gerar_id, agora, hash_senha
from utils.jwt_utils import criar_token, verificar_token


def registrar_usuario(
    nome: str,
    email: str,
    senha: str,
    photo_url: str = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Registra um novo usuário no sistema.
    
    Replica o trigger handle_new_user() do Supabase:
    1. Cria registro em usuarios
    2. Cria perfil em perfis
    3. Cria configurações em configuracoes
    4. Cria assinatura em assinaturas (plano 'free')
    5. Cria tokens em tokens_usuarios (500 tokens iniciais)
    6. Registra transação 'initial_grant' de 500 tokens
    7. Se email == 'adm123@gmail.com': cria admin e seta plano 'premium_max'
    
    Tudo é feito numa única transação atômica.
    
    Args:
        nome (str): Nome do usuário.
        email (str): Email único do usuário.
        senha (str): Senha em texto puro.
        photo_url (str, opcional): URL da foto do usuário.
    
    Returns:
        tuple: (dados_do_usuário, token_jwt) ou (None, None) em caso de erro.
    """
    try:
        with get_db() as conn:
            # Iniciar transação atômica
            conn.execute("BEGIN IMMEDIATE")
            
            try:
                usuario_id = gerar_id()
                data_atual = agora()
                senha_hash = hash_senha(senha)
                
                # 1. Criar usuário
                conn.execute("""
                    INSERT INTO usuarios (id, nome, email, senha_hash, photo_url, provider, is_guest, ativo, criado_em, atualizado_em)
                    VALUES (?, ?, ?, ?, ?, 'email', 0, 1, ?, ?)
                """, (usuario_id, nome, email, senha_hash, photo_url, data_atual, data_atual))
                
                # 2. Criar perfil
                username = email.split('@')[0]
                conn.execute("""
                    INSERT INTO perfis (id, email, username, display_name, nome, interesses, temporal_memory, criado_em, atualizado_em)
                    VALUES (?, ?, ?, ?, ?, '[]', '{"keyEvents": []}', ?, ?)
                """, (usuario_id, email, username, nome, nome, data_atual, data_atual))
                
                # 3. Criar configurações
                config_id = gerar_id()
                conn.execute("""
                    INSERT INTO configuracoes (id, user_id, tema, idioma, preferences, criado_em, atualizado_em)
                    VALUES (?, ?, 'dark', 'pt-BR', '{}', ?, ?)
                """, (config_id, usuario_id, data_atual, data_atual))
                
                # 4. Criar assinatura (plano free por padrão)
                assinatura_id = gerar_id()
                plano_inicial = 'premium_max' if email.lower() == 'adm123@gmail.com' else 'free'
                conn.execute("""
                    INSERT INTO assinaturas (id, user_id, plano, status, used_codes, criado_em, atualizado_em)
                    VALUES (?, ?, ?, 'active', '[]', ?, ?)
                """, (assinatura_id, usuario_id, plano_inicial, data_atual, data_atual))
                
                # 5. Criar tokens (500 iniciais)
                tokens_id = gerar_id()
                limite_inicial = 500000 if plano_inicial == 'premium_max' else 50000
                conn.execute("""
                    INSERT INTO tokens_usuarios (id, user_id, tokens_usados, limite_tokens, janela_inicio, plano, atualizado_em)
                    VALUES (?, ?, 0, ?, ?, ?, ?)
                """, (tokens_id, usuario_id, limite_inicial, data_atual, plano_inicial, data_atual))
                
                # 6. Registrar transação initial_grant
                transacao_id = gerar_id()
                conn.execute("""
                    INSERT INTO transacoes_tokens (id, user_id, tipo, amount, balance_before, balance_after, descricao, criado_em)
                    VALUES (?, ?, 'initial_grant', 500, 0, 500, 'Tokens iniciais concedidos', ?)
                """, (transacao_id, usuario_id, data_atual))
                
                # 7. Se for admin, criar registro em admins
                if email.lower() == 'adm123@gmail.com':
                    admin_id = gerar_id()
                    conn.execute("""
                        INSERT INTO admins (id, user_id, email, criado_em)
                        VALUES (?, ?, ?, ?)
                    """, (admin_id, usuario_id, email, data_atual))
                
                conn.commit()
                
                # Gerar token JWT
                token = criar_token(usuario_id, email, {"plano": plano_inicial})
                
                # Retornar dados do usuário (sem senha_hash)
                usuario_data = {
                    "id": usuario_id,
                    "nome": nome,
                    "email": email,
                    "photo_url": photo_url,
                    "provider": "email",
                    "is_guest": False,
                    "plano": plano_inicial
                }
                
                return usuario_data, token
            
            except Exception as e:
                conn.rollback()
                print(f"Erro na transação de registro: {e}")
                return None, None
    
    except Exception as e:
        print(f"Erro ao registrar usuário: {e}")
        return None, None


def login(email: str, senha: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Realiza login do usuário.
    
    Args:
        email (str): Email do usuário.
        senha (str): Senha em texto puro.
    
    Returns:
        tuple: (dados_do_usuário, token_jwt) ou (None, None) em caso de erro.
    """
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM usuarios WHERE email = ? AND ativo = 1",
                (email,)
            )
            row = cursor.fetchone()
            
            if not row:
                print("Usuário não encontrado")
                return None, None
            
            usuario = dict(row)
            
            # Verificar senha
            if not usuario.get("senha_hash"):
                # Usuário sem senha (ex: Google)
                print("Usuário não possui senha cadastrada")
                return None, None
            
            if hash_senha(senha) != usuario["senha_hash"]:
                print("Senha incorreta")
                return None, None
            
            # Buscar plano do usuário
            cursor = conn.execute(
                "SELECT plano FROM assinaturas WHERE user_id = ?",
                (usuario["id"],)
            )
            plano_row = cursor.fetchone()
            plano = plano_row["plano"] if plano_row else "free"
            
            # Gerar token JWT
            token = criar_token(usuario["id"], email, {"plano": plano})
            
            # Retornar dados (sem senha_hash)
            usuario_data = {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
                "photo_url": usuario.get("photo_url"),
                "provider": usuario.get("provider", "email"),
                "is_guest": bool(usuario.get("is_guest", 0)),
                "plano": plano
            }
            
            return usuario_data, token
    
    except Exception as e:
        print(f"Erro ao fazer login: {e}")
        return None, None


def logout(token: str) -> bool:
    """
    Realiza logout invalidando o token da sessão.
    
    Args:
        token (str): Token JWT a ser invalidado.
    
    Returns:
        bool: True se logout realizado com sucesso.
    """
    try:
        # Verificar token primeiro
        payload = verificar_token(token)
        
        if not payload:
            return False
        
        # Em um sistema com tabela de sessões, removeríamos a sessão aqui
        # Como usamos JWT stateless, o logout é feito apenas no frontend (removendo o token)
        
        return True
    
    except Exception as e:
        print(f"Erro ao fazer logout: {e}")
        return False


def get_usuario_por_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Obtém dados do usuário a partir de um token JWT.
    
    Args:
        token (str): Token JWT.
    
    Returns:
        dict: Dados do usuário ou None se token inválido.
    """
    try:
        # Verificar token
        payload = verificar_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        
        if not user_id:
            return None
        
        # Buscar usuário no banco
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM usuarios WHERE id = ? AND ativo = 1",
                (user_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            usuario = dict(row)
            
            # Buscar plano
            cursor = conn.execute(
                "SELECT plano FROM assinaturas WHERE user_id = ?",
                (user_id,)
            )
            plano_row = cursor.fetchone()
            plano = plano_row["plano"] if plano_row else "free"
            
            # Retornar dados (sem senha_hash)
            return {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
                "photo_url": usuario.get("photo_url"),
                "provider": usuario.get("provider", "email"),
                "is_guest": bool(usuario.get("is_guest", 0)),
                "plano": plano
            }
    
    except Exception as e:
        print(f"Erro ao obter usuário por token: {e}")
        return None


def criar_usuario_guest() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Cria um usuário convidado (guest) temporário.
    
    Returns:
        tuple: (dados_do_usuário, token_jwt) ou (None, None) em caso de erro.
    """
    try:
        with get_db() as conn:
            usuario_id = gerar_id()
            data_atual = agora()
            email_guest = f"guest_{usuario_id[:8]}@temp.local"
            
            # Criar usuário guest (sem senha)
            conn.execute("""
                INSERT INTO usuarios (id, nome, email, senha_hash, provider, is_guest, ativo, criado_em, atualizado_em)
                VALUES (?, 'Convidado', ?, NULL, 'guest', 1, 1, ?, ?)
            """, (usuario_id, email_guest, data_atual, data_atual))
            
            # Criar perfil mínimo
            conn.execute("""
                INSERT INTO perfis (id, email, username, display_name, criado_em, atualizado_em)
                VALUES (?, ?, ?, 'Convidado', ?, ?)
            """, (usuario_id, email_guest, email_guest.split('@')[0], data_atual, data_atual))
            
            # Criar assinatura free
            conn.execute("""
                INSERT INTO assinaturas (id, user_id, plano, status, criado_em, atualizado_em)
                VALUES (?, ?, 'free', 'active', ?, ?)
            """, (gerar_id(), usuario_id, data_atual, data_atual))
            
            # Criar tokens (500 iniciais)
            conn.execute("""
                INSERT INTO tokens_usuarios (id, user_id, tokens_usados, limite_tokens, janela_inicio, plano, atualizado_em)
                VALUES (?, ?, 0, 50000, ?, 'free', ?)
            """, (gerar_id(), usuario_id, data_atual, data_atual))
            
            conn.commit()
            
            # Gerar token JWT
            token = criar_token(usuario_id, email_guest, {"plano": "free"})
            
            usuario_data = {
                "id": usuario_id,
                "nome": "Convidado",
                "email": email_guest,
                "provider": "guest",
                "is_guest": True,
                "plano": "free"
            }
            
            return usuario_data, token
    
    except Exception as e:
        print(f"Erro ao criar usuário guest: {e}")
        return None, None


if __name__ == "__main__":
    from models import criar_todas_as_tabelas
    
    print("=== TESTE: Registro completo de usuário ===")
    usuario, token = registrar_usuario("Teste User", "teste@email.com", "Senha123")
    print(f"Usuário registrado: {usuario}")
    print(f"Token gerado: {token[:50] if token else None}...")
    
    print("\n=== TESTE: Login ===")
    usuario_login, token_login = login("teste@email.com", "Senha123")
    print(f"Login realizado: {usuario_login}")
    
    print("\n=== TESTE: Obter usuário por token ===")
    if token_login:
        usuario_token = get_usuario_por_token(token_login)
        print(f"Usuário do token: {usuario_token}")
    
    print("\n=== TESTE: Criar usuário guest ===")
    guest, guest_token = criar_usuario_guest()
    print(f"Guest criado: {guest}")
    
    print("\n=== TODOS OS TESTES CONCLUÍDOS ===")
