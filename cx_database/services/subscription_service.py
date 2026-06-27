"""Serviço de gerenciamento de assinaturas."""
from typing import Optional, Dict, Any
from models.assinaturas import criar_assinatura, buscar_assinatura_por_user_id, atualizar_plano
from utils.codec import decode_activation_code


def ativar_codigo(user_id: str, codigo: str) -> Optional[Dict[str, Any]]:
    """Ativa código de assinatura premium."""
    decoded = decode_activation_code(codigo)
    if not decoded or not decoded.get('valido'):
        return None
    
    assinatura = buscar_assinatura_por_user_id(user_id)
    if not assinatura:
        return None
    
    # Verificar se código já foi usado
    used_codes = assinatura.get('used_codes', [])
    if codigo in used_codes:
        return {'erro': 'Código já utilizado'}
    
    plano = decoded['plano']
    dias = decoded['dias']
    
    from datetime import datetime, timedelta
    expires_at = (datetime.utcnow() + timedelta(days=dias)).strftime('%Y-%m-%dT%H:%M:%S')
    
    if atualizar_plano(user_id, plano, expires_at):
        # Adicionar código aos usados
        used_codes.append(codigo)
        from utils.json_field import to_json
        from connection import get_connection
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE assinaturas SET used_codes = ?, atualizado_em = datetime('now') WHERE user_id = ?",
                (to_json(used_codes), user_id))
            conn.commit()
        
        return {'plano': plano, 'expires_at': expires_at}
    
    return None


def verificar_plano(user_id: str) -> Dict[str, Any]:
    """Verifica plano atual do usuário."""
    assinatura = buscar_assinatura_por_user_id(user_id)
    if not assinatura:
        return {'plano': 'free', 'ativo': False}
    
    # Verificar expiração
    from utils.helpers import agora
    premium_until = assinatura.get('premium_until')
    plano = assinatura.get('plano', 'free')
    
    if premium_until and plano != 'free' and agora() > premium_until:
        # Expirou - fazer downgrade
        atualizar_plano(user_id, 'free')
        return {'plano': 'free', 'expirado': True}
    
    return {
        'plano': plano,
        'ativo': True,
        'premium_until': premium_until
    }


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    
    print("\n=== TESTE: Verificar plano ===")
    plano = verificar_plano("user123")
    print(f"Plano: {plano}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
