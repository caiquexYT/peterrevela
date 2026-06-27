"""
Módulo de codificação/decodificação para o sistema CxIA.
Replica a função decodeActivationCode do frontend TypeScript.
"""

import base64
import hashlib
import hmac
from typing import Optional, Dict, Any


# Chave secreta para codificação (deve ser a mesma do frontend)
# Em produção, isso deve vir de variável de ambiente
SECRET_KEY = "cxia-secret-key-2024"  # Substitua por uma chave segura em produção


def decode_activation_code(code: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica um código de ativação premium.
    
    O código é esperado no formato: BASE64(payload).SIGNATURE
    Onde payload é um JSON com informações do plano e validade.
    
    Args:
        code (str): Código de ativação a ser decodificado.
    
    Returns:
        dict | None: Dicionário com os dados decodificados ou None se inválido.
        
    Exemplo de retorno:
        {
            "plan": "premium",
            "duration_days": 30,
            "valid": True
        }
    """
    if not code or not isinstance(code, str):
        return None
    
    try:
        # Separar payload e assinatura
        parts = code.split('.')
        if len(parts) != 2:
            return None
        
        payload_b64, signature = parts
        
        # Verificar assinatura
        expected_signature = hmac.new(
            SECRET_KEY.encode('utf-8'),
            payload_b64.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        # Decodificar payload
        payload_json = base64.urlsafe_b64decode(payload_b64 + '==').decode('utf-8')
        import json
        payload = json.loads(payload_json)
        
        return payload
    
    except Exception as e:
        print(f"Erro ao decodificar código: {e}")
        return None


def generate_activation_code(plan: str = "premium", duration_days: int = 30) -> str:
    """
    Gera um novo código de ativação premium.
    
    Args:
        plan (str): Tipo de plano ('premium' ou 'premium_max').
        duration_days (int): Duração do plano em dias.
    
    Returns:
        str: Código de ativação no formato BASE64(payload).SIGNATURE
    """
    import json
    import base64
    
    # Criar payload
    payload = {
        "plan": plan,
        "duration_days": duration_days,
        "version": "1.0"
    }
    
    # Codificar payload em Base64
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8').rstrip('=')
    
    # Gerar assinatura
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        payload_b64.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"{payload_b64}.{signature}"


if __name__ == "__main__":
    # Testes manuais
    print("=== TESTE: Gerar código de ativação ===")
    codigo = generate_activation_code("premium", 30)
    print(f"Código gerado: {codigo}")
    
    print("\n=== TESTE: Decodificar código ===")
    resultado = decode_activation_code(codigo)
    print(f"Resultado: {resultado}")
    
    print("\n=== TESTE: Código inválido ===")
    invalido = decode_activation_code("codigo-invalido")
    print(f"Resultado: {invalido}")
