"""
Roteador de tokens para a API CxIA.
Endpoints: GET /tokens/saldo, POST /tokens/consumir, POST /tokens/upgrade
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from schemas import ConsumoTokensInput, TokenSaldoResponse, ConsumoResult, UpgradePlanoInput
from services.auth_service import get_usuario_por_token
from services.token_service import get_saldo, consumir_tokens, adicionar_tokens, atualizar_plano

router = APIRouter(prefix="/tokens", tags=["Tokens"])


def get_current_user(authorization: Optional[str]) -> dict:
    """Extrai usuário do token JWT."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = authorization.replace("Bearer ", "")
    usuario = get_usuario_por_token(token)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    return usuario


@router.get("/saldo", response_model=TokenSaldoResponse)
async def get_saldo_endpoint(authorization: Optional[str] = Header(None)):
    """
    Obtém o saldo atual de tokens do usuário.
    
    Retorna:
    - **tokens_usados**: Quantidade de tokens usados na janela atual
    - **limite_tokens**: Limite máximo de tokens do plano
    - **tokens_restantes**: Tokens disponíveis para uso
    - **janela_inicio**: Data/hora de início da janela atual
    - **plano**: Plano atual do usuário (free/premium/premium_max)
    """
    usuario = get_current_user(authorization)
    saldo = get_saldo(usuario["id"])
    
    return saldo


@router.post("/consumir", response_model=ConsumoResult)
async def consumir_endpoint(
    dados: ConsumoTokensInput,
    authorization: Optional[str] = Header(None)
):
    """
    Consome tokens do usuário.
    
    - **amount**: Quantidade de tokens a consumir (obrigatório, > 0)
    - **descricao**: Descrição do consumo (ex: "Mensagem enviada no chat")
    
    Retorna:
    - **allowed**: True se consumo realizado com sucesso, False se saldo insuficiente
    - **tokens_restantes**: Saldo após consumo
    - **reset_in_ms**: Tempo em ms até a próxima recarga (se aplicável)
    """
    usuario = get_current_user(authorization)
    
    try:
        sucesso, restante = consumir_tokens(
            user_id=usuario["id"],
            amount=dados.amount,
            descricao=dados.descricao
        )
        
        # Calcular tempo até reset se necessário
        reset_in_ms = None
        if not sucesso and restante == 0:
            # Janela de 8 horas = 28800000 ms
            reset_in_ms = 28800000
        
        return {
            "allowed": sucesso,
            "tokens_restantes": restante,
            "reset_in_ms": reset_in_ms
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro ao consumir tokens: {e}")
        raise HTTPException(status_code=500, detail="Erro ao consumir tokens")


@router.post("/upgrade")
async def upgrade_plano(
    dados: UpgradePlanoInput,
    authorization: Optional[str] = Header(None)
):
    """
    Atualiza o plano do usuário.
    
    - **novo_plano**: 'free', 'premium' ou 'premium_max'
    
    Limites de tokens por plano:
    - free: 50.000 tokens
    - premium: 250.000 tokens
    - premium_max: 500.000 tokens
    """
    usuario = get_current_user(authorization)
    
    # Definir limites por plano
    limites = {
        "free": 50000,
        "premium": 250000,
        "premium_max": 500000
    }
    
    novo_limite = limites.get(dados.novo_plano)
    
    if not novo_limite:
        raise HTTPException(status_code=400, detail="Plano inválido")
    
    sucesso = atualizar_plano(usuario["id"], dados.novo_plano, novo_limite)
    
    if not sucesso:
        raise HTTPException(status_code=500, detail="Erro ao atualizar plano")
    
    return {
        "message": f"Plano atualizado para {dados.novo_plano}",
        "novo_limite": novo_limite
    }


@router.post("/bonus")
async def adicionar_bonus(
    amount: int,
    descricao: str,
    authorization: Optional[str] = Header(None)
):
    """
    Adiciona tokens de bônus ao usuário.
    
    Endpoint administrativo para conceder tokens extras.
    """
    usuario = get_current_user(authorization)
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount deve ser positivo")
    
    sucesso = adicionar_tokens(
        user_id=usuario["id"],
        amount=amount,
        tipo="bonus",
        descricao=descricao
    )
    
    if not sucesso:
        raise HTTPException(status_code=500, detail="Erro ao adicionar bônus")
    
    return {
        "message": f"{amount} tokens de bônus adicionados",
        "novo_saldo": get_saldo(usuario["id"])
    }
