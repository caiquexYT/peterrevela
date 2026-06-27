"""
Roteador de mensagens para a API CxIA.
Endpoints: GET /mensagens/{conversa_id}, POST /mensagens, DELETE /mensagens/{id}
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List, Dict, Any

from schemas import CriarMensagemInput, MensagemResponse, ListarMensagensResponse
from database import get_db
from utils.helpers import gerar_id, agora
from utils.json_field import to_json
from services.auth_service import get_usuario_por_token

router = APIRouter(prefix="/mensagens", tags=["Mensagens"])


def get_current_user(authorization: Optional[str]) -> dict:
    """Extrai usuário do token JWT."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = authorization.replace("Bearer ", "")
    usuario = get_usuario_por_token(token)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    return usuario


@router.get("/{conversa_id}", response_model=ListarMensagensResponse)
async def listar_mensagens(conversa_id: str, authorization: Optional[str] = Header(None)):
    """
    Lista todas as mensagens de uma conversa.
    
    Retorna mensagens ordenadas por criado_em ASC (mais antigas primeiro).
    """
    usuario = get_current_user(authorization)
    
    try:
        with get_db() as conn:
            # Verificar se a conversa pertence ao usuário
            cursor = conn.execute(
                "SELECT * FROM conversas WHERE id = ? AND user_id = ?",
                (conversa_id, usuario["id"])
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Conversa não encontrada")
            
            # Buscar mensagens
            cursor = conn.execute(
                """
                SELECT * FROM mensagens 
                WHERE conversa_id = ? 
                ORDER BY criado_em ASC
                """,
                (conversa_id,)
            )
            
            mensagens = []
            for row in cursor.fetchall():
                msg = dict(row)
                # Desserializar campos JSON
                if msg.get("attachment"):
                    msg["attachment"] = msg["attachment"]  # Já vem como string JSON
                if msg.get("actions"):
                    msg["actions"] = msg["actions"]
                if msg.get("image_urls"):
                    msg["image_urls"] = msg["image_urls"]
                mensagens.append(msg)
            
            return {"mensagens": mensagens}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao listar mensagens: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar mensagens")


@router.post("", response_model=MensagemResponse)
async def criar_mensagem(dados: CriarMensagemInput, authorization: Optional[str] = Header(None)):
    """
    Cria uma nova mensagem em uma conversa.
    
    - **conversa_id**: ID da conversa (obrigatório)
    - **role**: 'user', 'assistant', 'system' ou 'model' (obrigatório)
    - **content**: Conteúdo da mensagem (obrigatório)
    - **thinking_time**: Tempo de pensamento em segundos (opcional)
    - **attachment**: Dados anexos em JSON (opcional)
    - **actions**: Ações em JSON (opcional)
    """
    usuario = get_current_user(authorization)
    
    try:
        with get_db() as conn:
            # Verificar se a conversa existe e pertence ao usuário
            cursor = conn.execute(
                "SELECT * FROM conversas WHERE id = ? AND user_id = ?",
                (dados.conversa_id, usuario["id"])
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Conversa não encontrada")
            
            mensagem_id = gerar_id()
            data_atual = agora()
            
            # Serializar campos JSON
            attachment_json = to_json(dados.attachment) if dados.attachment else None
            actions_json = to_json(dados.actions) if dados.actions else None
            
            conn.execute("""
                INSERT INTO mensagens (id, conversa_id, user_id, role, content, thinking_time, attachment, actions, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mensagem_id,
                dados.conversa_id,
                usuario["id"],
                dados.role,
                dados.content,
                dados.thinking_time,
                attachment_json,
                actions_json,
                data_atual
            ))
            
            # Atualizar ultima_modificacao da conversa
            conn.execute("""
                UPDATE conversas SET atualizado_em = ? WHERE id = ?
            """, (data_atual, dados.conversa_id))
            
            conn.commit()
            
            # Buscar mensagem criada
            cursor = conn.execute(
                "SELECT * FROM mensagens WHERE id = ?",
                (mensagem_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            
            raise HTTPException(status_code=500, detail="Erro ao criar mensagem")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao criar mensagem: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar mensagem")


@router.delete("/{mensagem_id}")
async def deletar_mensagem(mensagem_id: str, authorization: Optional[str] = Header(None)):
    """
    Deleta uma mensagem específica.
    """
    usuario = get_current_user(authorization)
    
    try:
        with get_db() as conn:
            # Verificar se a mensagem existe e pertence ao usuário
            cursor = conn.execute(
                """
                SELECT m.* FROM mensagens m
                JOIN conversas c ON m.conversa_id = c.id
                WHERE m.id = ? AND c.user_id = ?
                """,
                (mensagem_id, usuario["id"])
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Mensagem não encontrada")
            
            # Deletar mensagem
            conn.execute("DELETE FROM mensagens WHERE id = ?", (mensagem_id,))
            conn.commit()
            
            return {"message": "Mensagem deletada com sucesso"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao deletar mensagem: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar mensagem")
