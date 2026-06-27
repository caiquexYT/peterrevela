"""
Roteador de conversas para a API CxIA.
Endpoints: GET/POST /conversas, PUT/DELETE /conversas/{id}
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List

from schemas import CriarConversaInput, AtualizarConversaInput, ConversaResponse, ListarConversasResponse
from database import get_db
from utils.helpers import gerar_id, agora
from services.auth_service import get_usuario_por_token

router = APIRouter(prefix="/conversas", tags=["Conversas"])


def get_current_user(authorization: Optional[str]) -> dict:
    """Extrai usuário do token JWT."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = authorization.replace("Bearer ", "")
    usuario = get_usuario_por_token(token)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    return usuario


@router.get("", response_model=ListarConversasResponse)
async def listar_conversas(authorization: Optional[str] = Header(None)):
    """
    Lista todas as conversas do usuário logado.
    
    Retorna conversas ordenadas por mais recente primeiro.
    """
    usuario = get_current_user(authorization)
    
    try:
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM conversas 
                WHERE user_id = ? 
                ORDER BY atualizado_em DESC
                """,
                (usuario["id"],)
            )
            
            conversas = [dict(row) for row in cursor.fetchall()]
            
            return {"conversas": conversas}
    
    except Exception as e:
        print(f"Erro ao listar conversas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar conversas")


@router.post("", response_model=ConversaResponse)
async def criar_conversa(dados: CriarConversaInput, authorization: Optional[str] = Header(None)):
    """
    Cria uma nova conversa para o usuário logado.
    
    - **titulo**: Título da conversa (obrigatório)
    """
    usuario = get_current_user(authorization)
    
    try:
        with get_db() as conn:
            conversa_id = gerar_id()
            data_atual = agora()
            
            conn.execute("""
                INSERT INTO conversas (id, user_id, titulo, modo, is_private, criado_em, atualizado_em)
                VALUES (?, ?, ?, 'chat', 0, ?, ?)
            """, (conversa_id, usuario["id"], dados.titulo, data_atual, data_atual))
            
            conn.commit()
            
            # Buscar conversa criada
            cursor = conn.execute(
                "SELECT * FROM conversas WHERE id = ?",
                (conversa_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            
            raise HTTPException(status_code=500, detail="Erro ao criar conversa")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao criar conversa: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar conversa")


@router.get("/{conversa_id}", response_model=ConversaResponse)
async def obter_conversa(conversa_id: str, authorization: Optional[str] = Header(None)):
    """
    Obtém detalhes de uma conversa específica.
    """
    usuario = get_current_user(authorization)
    
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM conversas WHERE id = ? AND user_id = ?",
                (conversa_id, usuario["id"])
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Conversa não encontrada")
            
            return dict(row)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao obter conversa: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter conversa")


@router.put("/{conversa_id}", response_model=ConversaResponse)
async def atualizar_conversa(
    conversa_id: str,
    dados: AtualizarConversaInput,
    authorization: Optional[str] = Header(None)
):
    """
    Atualiza uma conversa existente.
    
    - **titulo**: Novo título (opcional)
    - **is_private**: Definir como privada (opcional)
    """
    usuario = get_current_user(authorization)
    
    try:
        with get_db() as conn:
            # Verificar se a conversa existe e pertence ao usuário
            cursor = conn.execute(
                "SELECT * FROM conversas WHERE id = ? AND user_id = ?",
                (conversa_id, usuario["id"])
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Conversa não encontrada")
            
            # Atualizar campos
            updates = []
            values = []
            
            if dados.titulo is not None:
                updates.append("titulo = ?")
                values.append(dados.titulo)
            
            if dados.is_private is not None:
                updates.append("is_private = ?")
                values.append(1 if dados.is_private else 0)
            
            if updates:
                updates.append("atualizado_em = ?")
                values.append(agora())
                values.append(conversa_id)
                
                query = f"UPDATE conversas SET {', '.join(updates)} WHERE id = ?"
                conn.execute(query, values)
                conn.commit()
            
            # Buscar conversa atualizada
            cursor = conn.execute(
                "SELECT * FROM conversas WHERE id = ?",
                (conversa_id,)
            )
            row = cursor.fetchone()
            
            return dict(row)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao atualizar conversa: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar conversa")


@router.delete("/{conversa_id}")
async def deletar_conversa(conversa_id: str, authorization: Optional[str] = Header(None)):
    """
    Deleta uma conversa e todas as suas mensagens.
    
    O CASCADE do SQLite remove automaticamente as mensagens relacionadas.
    """
    usuario = get_current_user(authorization)
    
    try:
        with get_db() as conn:
            # Verificar se a conversa existe e pertence ao usuário
            cursor = conn.execute(
                "SELECT * FROM conversas WHERE id = ? AND user_id = ?",
                (conversa_id, usuario["id"])
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Conversa não encontrada")
            
            # Deletar conversa (CASCADE remove mensagens automaticamente)
            conn.execute("DELETE FROM conversas WHERE id = ?", (conversa_id,))
            conn.commit()
            
            return {"message": "Conversa deletada com sucesso"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao deletar conversa: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar conversa")
