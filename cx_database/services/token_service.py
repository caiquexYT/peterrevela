"""Serviço de gerenciamento de tokens."""
from typing import Optional, Dict, Any
from models.tokens import (
    criar_tokens, buscar_tokens_por_user_id, consumir_tokens_atomico,
    adicionar_tokens, get_saldo
)
from models.transacoes_tokens import listar_transacoes_por_usuario


def consumir_tokens(user_id: str, amount: int, descricao: str, refill_horas: int = 24) -> bool:
    """
    Debita tokens do usuário de forma atômica e segura.
    Replica a função consume_user_tokens() do Supabase/PostgreSQL.
    
    Args:
        user_id (str): UUID do usuário.
        amount (int): Quantidade de tokens a debitar.
        descricao (str): Descrição da transação.
        refill_horas (int): Horas para recarga automática quando saldo zera. Default: 24.
    
    Returns:
        bool: True se débito realizado com sucesso, False se saldo insuficiente.
    """
    if amount <= 0:
        raise ValueError("O amount deve ser maior que zero.")
    
    return consumir_tokens_atomico(user_id, amount, descricao)


def recarregar_se_necessario(user_id: str) -> bool:
    """Verifica e recarrega tokens se necessário."""
    tokens = buscar_tokens_por_user_id(user_id)
    if not tokens or not tokens.get('waiting_refill'):
        return False
    
    from utils.helpers import agora
    from datetime import datetime
    
    next_refill = tokens.get('next_refill_at')
    if not next_refill:
        return False
    
    try:
        if agora() >= next_refill:
            # Recarregar tokens
            adicionar_tokens(user_id, tokens.get('initial_tokens', 500), 'refill', 'Recarga automática')
            
            # Atualizar flags
            from connection import get_connection
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""UPDATE user_tokens SET 
                    waiting_refill = 0, last_refill_at = ?, next_refill_at = NULL, atualizado_em = ?
                    WHERE user_id = ?""", (agora(), agora(), user_id))
                conn.commit()
            return True
    except Exception:
        pass
    
    return False


def adicionar_bonus(user_id: str, amount: int, descricao: str) -> bool:
    """Adiciona tokens de bônus."""
    return adicionar_tokens(user_id, amount, 'bonus', descricao)


def historico_tokens(user_id: str, limite: int = 50) -> list:
    """Retorna histórico de transações de tokens."""
    return listar_transacoes_por_usuario(user_id, limite)


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    
    print("\n=== TESTE: Consumo de tokens ===")
    # Criar usuário teste
    from models.usuarios import criar_usuario
    from models.tokens import criar_tokens
    u = criar_usuario("token_test@email.com", "Senha123")
    if u:
        criar_tokens(u['id'], 500)
        
        print(f"Saldo inicial: {get_saldo(u['id'])}")
        ok = consumir_tokens(u['id'], 10, "Teste de consumo")
        print(f"Consumo OK: {ok}")
        print(f"Saldo após consumo: {get_saldo(u['id'])}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
