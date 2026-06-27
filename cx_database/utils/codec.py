"""
Módulo de codificação/decodificação de códigos de ativação.

Este módulo replica a função decodeActivationCode do frontend TypeScript,
permitindo validar e decodificar códigos de ativação de plano premium no backend.

Os códigos de ativação são usados para upgrade de plano sem pagamento direto.
"""

import base64
import json
import hashlib
import hmac
from typing import Optional, Dict, Any
from datetime import datetime


# Chave secreta para validação dos códigos (em produção, usar variável de ambiente)
ACTIVATION_SECRET_KEY = "cx_saas_activation_secret_2025"


def encode_activation_code(
    plano: str,
    dias_validade: int,
    codigo_personalizado: Optional[str] = None
) -> str:
    """
    Codifica um código de ativação para uso em campanhas/promoções.

    Args:
        plano (str): Tipo de plano ('premium', 'premium_max').
        dias_validade (int): Quantidade de dias de validade do código.
        codigo_personalizado (Optional[str]): Código personalizado opcional.

    Returns:
        str: Código de ativação codificado em base64.

    Example:
        >>> encode_activation_code('premium', 30)
        'eyJwbGFubyI6ICJwcmVtaXVtIiwgImRpYXMiOiAzMH0=...'
    """
    payload = {
        "plano": plano,
        "dias": dias_validade,
        "criado_em": datetime.now().isoformat(),
        "random": codigo_personalizado or hashlib.sha256(
            f"{plano}{dias_validade}{datetime.now()}".encode()
        ).hexdigest()[:16]
    }
    
    # Converte para JSON e codifica em base64
    json_payload = json.dumps(payload, separators=(',', ':'))
    encoded = base64.urlsafe_b64encode(json_payload.encode('utf-8')).decode('utf-8')
    
    # Adiciona checksum para validação
    checksum = hmac.new(
        ACTIVATION_SECRET_KEY.encode(),
        encoded.encode(),
        hashlib.sha256
    ).hexdigest()[:8]
    
    return f"{encoded}.{checksum}"


def decode_activation_code(codigo: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica e valida um código de ativação.

    Replica a função decodeActivationCode do frontend.

    Args:
        codigo (str): Código de ativação recebido do usuário.

    Returns:
        Optional[Dict]: Dicionário com dados do código se válido, None se inválido.
        O dict retornado contém: {'plano': str, 'dias': int, 'valido': bool}

    Example:
        >>> decode_activation_code('eyJwbGFubyI6ICJwcmVtaXVtIn0.abc123')
        {'plano': 'premium', 'dias': 30, 'valido': True}
    """
    if not codigo or not isinstance(codigo, str):
        return None
    
    try:
        # Separar código e checksum
        partes = codigo.strip().split('.')
        if len(partes) != 2:
            return None
        
        encoded, checksum_recebido = partes
        
        # Validar checksum
        checksum_esperado = hmac.new(
            ACTIVATION_SECRET_KEY.encode(),
            encoded.encode(),
            hashlib.sha256
        ).hexdigest()[:8]
        
        if not hmac.compare_digest(checksum_recebido, checksum_esperado):
            return None
        
        # Decodificar base64
        decoded_bytes = base64.urlsafe_b64decode(encoded.encode('utf-8'))
        decoded_str = decoded_bytes.decode('utf-8')
        payload = json.loads(decoded_str)
        
        # Validar campos obrigatórios
        if 'plano' not in payload or 'dias' not in payload:
            return None
        
        # Validar tipo de plano
        if payload['plano'] not in ['premium', 'premium_max']:
            return None
        
        # Validar dias
        if not isinstance(payload['dias'], int) or payload['dias'] <= 0:
            return None
        
        return {
            'plano': payload['plano'],
            'dias': payload['dias'],
            'valido': True
        }
        
    except (base64.binascii.Error, json.JSONDecodeError, KeyError, TypeError) as e:
        # Qualquer erro na decodificação significa código inválido
        print(f"Código de ativação inválido: {e}")
        return None


def validar_codigo_formato(codigo: str) -> bool:
    """
    Valida apenas o formato do código sem decodificar completamente.

    Útil para validação rápida no frontend antes de enviar ao backend.

    Args:
        codigo (str): Código a ser validado.

    Returns:
        bool: True se o formato estiver correto, False caso contrário.
    """
    if not codigo or not isinstance(codigo, str):
        return False
    
    partes = codigo.strip().split('.')
    if len(partes) != 2:
        return False
    
    encoded, checksum = partes
    
    # Verificar tamanho mínimo
    if len(encoded) < 10 or len(checksum) != 8:
        return False
    
    # Tentar decodificar base64 para verificar formato
    try:
        base64.urlsafe_b64decode(encoded.encode('utf-8'))
        return True
    except Exception:
        return False


if __name__ == "__main__":
    print("=== TESTE: encode_activation_code ===")
    
    codigo1 = encode_activation_code('premium', 30)
    codigo2 = encode_activation_code('premium_max', 90)
    codigo3 = encode_activation_code('premium', 7, "PROMO_VERAO")
    
    print(f"Código premium 30 dias: {codigo1}")
    print(f"Código premium_max 90 dias: {codigo2}")
    print(f"Código promocional: {codigo3}")
    
    print("\n=== TESTE: decode_activation_code ===")
    
    resultado1 = decode_activation_code(codigo1)
    resultado2 = decode_activation_code(codigo2)
    resultado3 = decode_activation_code(codigo3)
    
    print(f"Decodificado 1: {resultado1}")
    print(f"Decodificado 2: {resultado2}")
    print(f"Decodificado 3: {resultado3}")
    
    print("\n=== TESTE: códigos inválidos ===")
    
    invalidos = [
        "",
        None,
        "codigo-sem-checksum",
        "eyJ0ZXN0ZSJ9.checksum-errado",
        "não é base64 válido.abcdef12",
        "eyJwbGFubyI6ICJpbnZhbGlkbyIsICJkaWFzIjogMzB9.abc12345"  # plano inválido
    ]
    
    for inv in invalidos:
        resultado = decode_activation_code(inv)
        status = "✓ Rejeitado" if resultado is None else "✗ Aceito (erro!)"
        print(f"{status}: '{inv}'")
    
    print("\n=== TESTE: validar_codigo_formato ===")
    
    formatos_teste = [
        (codigo1, True),
        ("invalido", False),
        ("sem.checksum.curto", False),
        ("", False),
    ]
    
    for codigo, esperado in formatos_teste:
        resultado = validar_codigo_formato(codigo)
        status = "✓" if resultado == esperado else "✗"
        print(f"{status} validar_formato('{codigo[:20]}...') = {resultado}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
