"""
Utilitário para serialização e desserialização de campos JSON.
Simula o comportamento JSONB do PostgreSQL no SQLite.
"""

import json
from typing import Any, Optional, List, Dict


def to_json(value: Any) -> Optional[str]:
    """
    Converte um valor Python (dict, list, etc.) para string JSON.
    
    Args:
        value (Any): Valor a ser convertido. Pode ser dict, list, ou None.
    
    Returns:
        str | None: String JSON se o valor for válido, None se o valor for None.
    """
    if value is None:
        return None
    
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        print(f"Erro ao converter para JSON: {e}")
        return None


def from_json(value: Optional[str], default: Any = None) -> Any:
    """
    Converte uma string JSON de volta para um objeto Python.
    
    Args:
        value (str | None): String JSON para converter.
        default (Any): Valor padrão a ser retornado em caso de erro ou None.
    
    Returns:
        Any: Objeto Python (dict, list, etc.) ou o valor default.
    """
    if value is None or value == '':
        return default
    
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Erro ao converter de JSON: {e}")
        return default


# Aliases para compatibilidade com diferentes nomes
serialize_json = to_json
deserialize_json = from_json
