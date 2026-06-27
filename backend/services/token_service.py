"""
Serviço de gerenciamento de tokens para o CxIA.
Implementa consumo atômico de tokens com prevenção de race conditions.
"""

import sqlite3
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from database import get_db
from utils.helpers import gerar_id, agora


def get_or_create_tokens(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtém ou cria registros de tokens para um usuário.
    Replica a função get_or_create_user_tokens() do Supabase.
    
    Args:
        user_id (str): ID do usuário.
    
    Returns:
        dict: Dados de tokens do usuário ou None em caso de erro.
    """
    try:
        with get_db() as conn:
            # Tentar buscar tokens existentes
            cursor = conn.execute(
                "SELECT * FROM tokens_usuarios WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            
            # Criar tokens se não existirem (500 iniciais)
            tokens_id = gerar_id()
            data_atual = agora()
            
            conn.execute("""
                INSERT INTO tokens_usuarios (id, user_id, tokens_usados, limite_tokens, janela_inicio, plano, atualizado_em)
                VALUES (?, ?, 0, 50000, ?, 'free', ?)
            """, (tokens_id, user_id, data_atual, data_atual))
            
            conn.commit()
            
            return get_or_create_tokens(user_id)
    
    except Exception as e:
        print(f"Erro ao obter/criar tokens: {e}")
        return None


def consumir_tokens(
    user_id: str,
    amount: int,
    descricao: str,
    refill_horas: int = 8
) -> Tuple[bool, int]:
    """
    Debita tokens do usuário de forma atômica e segura.
    Replica a função consume_user_tokens() do Supabase/PostgreSQL.
    
    Usa BEGIN IMMEDIATE para lock exclusivo, evitando race conditions
    quando múltiplas requisições tentam consumir tokens simultaneamente.
    
    Args:
        user_id (str): ID do usuário.
        amount (int): Quantidade de tokens a debitar.
        descricao (str): Descrição da transação.
        refill_horas (int): Horas para recarga automática quando saldo zera. Default: 8.
    
    Returns:
        tuple: (sucesso: bool, tokens_restantes: int)
    """
    if amount <= 0:
        raise ValueError("O amount deve ser maior que zero.")
    
    try:
        with get_db() as conn:
            # BEGIN IMMEDIATE para lock exclusivo (equivalente ao FOR UPDATE do PostgreSQL)
            conn.execute("BEGIN IMMEDIATE")
            
            try:
                # Buscar tokens atuais
                cursor = conn.execute(
                    "SELECT * FROM tokens_usuarios WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    conn.rollback()
                    return False, 0
                
                tokens_data = dict(row)
                tokens_usados = tokens_data["tokens_usados"]
                limite_tokens = tokens_data["limite_tokens"]
                janela_inicio_str = tokens_data["janela_inicio"]
                
                # Calcular tokens disponíveis
                tokens_disponiveis = limite_tokens - tokens_usados
                
                if tokens_disponiveis < amount:
                    conn.rollback()
                    return False, tokens_disponiveis
                
                # Verificar se precisa resetar janela (8 horas)
                janela_inicio = datetime.fromisoformat(janela_inicio_str)
                agora_dt = datetime.now()
                
                if (agora_dt - janela_inicio).total_seconds() >= refill_horas * 3600:
                    # Resetar janela
                    nova_janela = agora()
                    conn.execute("""
                        UPDATE tokens_usuarios 
                        SET tokens_usados = 0, janela_inicio = ?, atualizado_em = ?
                        WHERE user_id = ?
                    """, (nova_janela, agora(), user_id))
                    
                    tokens_usados = 0
                    tokens_disponiveis = limite_tokens
                
                # Debitar tokens
                novos_tokens_usados = tokens_usados + amount
                tokens_restantes = limite_tokens - novos_tokens_usados
                
                conn.execute("""
                    UPDATE tokens_usuarios 
                    SET tokens_usados = ?, atualizado_em = ?
                    WHERE user_id = ?
                """, (novos_tokens_usados, agora(), user_id))
                
                # Registrar transação
                transacao_id = gerar_id()
                conn.execute("""
                    INSERT INTO transacoes_tokens (id, user_id, tipo, amount, balance_before, balance_after, descricao, criado_em)
                    VALUES (?, ?, 'usage', ?, ?, ?, ?, ?)
                """, (transacao_id, user_id, amount, tokens_disponiveis, tokens_restantes, descricao, agora()))
                
                conn.commit()
                
                return True, tokens_restantes
            
            except Exception as e:
                conn.rollback()
                print(f"Erro na transação de consumo de tokens: {e}")
                return False, 0
    
    except Exception as e:
        print(f"Erro de conexão ao consumir tokens: {e}")
        return False, 0


def get_saldo(user_id: str) -> Dict[str, Any]:
    """
    Obtém o saldo atual de tokens do usuário.
    
    Args:
        user_id (str): ID do usuário.
    
    Returns:
        dict: Dados de saldo ou dados zerados se não existir.
    """
    tokens = get_or_create_tokens(user_id)
    
    if not tokens:
        return {
            "tokens_usados": 0,
            "limite_tokens": 50000,
            "tokens_restantes": 50000,
            "janela_inicio": agora(),
            "plano": "free"
        }
    
    tokens_restantes = tokens["limite_tokens"] - tokens["tokens_usados"]
    
    return {
        "tokens_usados": tokens["tokens_usados"],
        "limite_tokens": tokens["limite_tokens"],
        "tokens_restantes": max(0, tokens_restantes),
        "janela_inicio": tokens["janela_inicio"],
        "plano": tokens.get("plano", "free")
    }


def adicionar_tokens(
    user_id: str,
    amount: int,
    tipo: str,
    descricao: str
) -> bool:
    """
    Adiciona tokens ao usuário (para bônus, ajustes admin, etc.).
    
    Args:
        user_id (str): ID do usuário.
        amount (int): Quantidade de tokens a adicionar.
        tipo (str): Tipo da transação ('bonus', 'refill', 'admin_adjustment').
        descricao (str): Descrição da transação.
    
    Returns:
        bool: True se adicionado com sucesso.
    """
    try:
        with get_db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            
            try:
                # Buscar tokens atuais
                cursor = conn.execute(
                    "SELECT * FROM tokens_usuarios WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    conn.rollback()
                    return False
                
                tokens_data = dict(row)
                tokens_usados = tokens_data["tokens_usados"]
                limite_tokens = tokens_data["limite_tokens"]
                
                # Adicionar tokens (reduzir tokens_usados)
                novos_tokens_usados = max(0, tokens_usados - amount)
                tokens_restantes = limite_tokens - novos_tokens_usados
                
                conn.execute("""
                    UPDATE tokens_usuarios 
                    SET tokens_usados = ?, atualizado_em = ?
                    WHERE user_id = ?
                """, (novos_tokens_usados, agora(), user_id))
                
                # Registrar transação
                transacao_id = gerar_id()
                conn.execute("""
                    INSERT INTO transacoes_tokens (id, user_id, tipo, amount, balance_before, balance_after, descricao, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (transacao_id, user_id, tipo, amount, tokens_usados, tokens_restantes, descricao, agora()))
                
                conn.commit()
                return True
            
            except Exception as e:
                conn.rollback()
                print(f"Erro na transação de adição de tokens: {e}")
                return False
    
    except Exception as e:
        print(f"Erro ao adicionar tokens: {e}")
        return False


def atualizar_plano(user_id: str, novo_plano: str, novo_limite: int) -> bool:
    """
    Atualiza o plano e limite de tokens do usuário.
    
    Args:
        user_id (str): ID do usuário.
        novo_plano (str): Novo plano ('free', 'premium', 'premium_max').
        novo_limite (int): Novo limite de tokens.
    
    Returns:
        bool: True se atualizado com sucesso.
    """
    try:
        with get_db() as conn:
            # Atualizar tokens_usuarios
            conn.execute("""
                UPDATE tokens_usuarios 
                SET plano = ?, limite_tokens = ?, atualizado_em = ?
                WHERE user_id = ?
            """, (novo_plano, novo_limite, agora(), user_id))
            
            # Atualizar assinaturas
            conn.execute("""
                UPDATE assinaturas 
                SET plano = ?, atualizado_em = ?
                WHERE user_id = ?
            """, (novo_plano, agora(), user_id))
            
            conn.commit()
            return True
    
    except Exception as e:
        print(f"Erro ao atualizar plano: {e}")
        return False


if __name__ == "__main__":
    from models import criar_todas_as_tabelas
    from services.auth_service import registrar_usuario
    
    print("=== TESTE: Registro de usuário ===")
    usuario, token = registrar_usuario("Token Test", "token@email.com", "Senha123")
    print(f"Usuário: {usuario['id'] if usuario else None}")
    
    if usuario:
        user_id = usuario["id"]
        
        print("\n=== TESTE: Obter saldo inicial ===")
        saldo = get_saldo(user_id)
        print(f"Saldo inicial: {saldo}")
        
        print("\n=== TESTE: Consumir tokens ===")
        sucesso, restante = consumir_tokens(user_id, 1000, "Teste de consumo")
        print(f"Consumo: {sucesso}, Restante: {restante}")
        
        print("\n=== TESTE: Saldo após consumo ===")
        saldo = get_saldo(user_id)
        print(f"Saldo: {saldo}")
        
        print("\n=== TESTE: Adicionar tokens (bônus) ===")
        ok = adicionar_tokens(user_id, 5000, "bonus", "Bônus de teste")
        print(f"Bônus adicionado: {ok}")
        
        print("\n=== TESTE: Saldo após bônus ===")
        saldo = get_saldo(user_id)
        print(f"Saldo: {saldo}")
    
    print("\n=== TODOS OS TESTES CONCLUÍDOS ===")
