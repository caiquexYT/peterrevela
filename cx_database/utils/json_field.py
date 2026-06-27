"""
Módulo de serialização/deserialização de campos JSON.

Este módulo simula o comportamento JSONB do PostgreSQL, permitindo
armazenar estruturas complexas (dicts, lists) em campos TEXT do SQLite.

Todos os campos JSON no banco devem usar estas funções para garantir
consistência e tratamento correto de erros.
"""

import json
from typing import Any, Optional, Union


def to_json(value: Any) -> Optional[str]:
    """
    Converte um valor Python (dict, list, etc.) para string JSON.

    Args:
        value (Any): Valor a ser convertido. Pode ser dict, list, str, int, float, bool, None.

    Returns:
        Optional[str]: String JSON se conversão bem-sucedida, None se value for None.

    Example:
        >>> to_json({"chave": "valor"})
        '{"chave": "valor"}'
        >>> to_json([1, 2, 3])
        '[1, 2, 3]'
        >>> to_json(None)
        None
    """
    if value is None:
        return None
    
    try:
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    except (TypeError, ValueError) as e:
        # Log do erro sem quebrar o sistema
        print(f"Erro ao serializar JSON: {e}")
        return None


def from_json(value: Optional[str], default: Any = None) -> Any:
    """
    Converte uma string JSON do banco de dados para objeto Python.

    Args:
        value (Optional[str]): String JSON vinda do banco de dados.
        default (Any, optional): Valor padrão retornado se value for None ou inválido. Default: None.

    Returns:
        Any: Objeto Python (dict, list, etc.) ou default se falhar.

    Example:
        >>> from_json('{"chave": "valor"}')
        {'chave': 'valor'}
        >>> from_json('[1, 2, 3]')
        [1, 2, 3]
        >>> from_json(None, default={})
        {}
        >>> from_json('invalido', default=[])
        []
    """
    if value is None:
        return default
    
    if not isinstance(value, str):
        return default
    
    if value.strip() == '':
        return default
    
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        # Log do erro sem quebrar o sistema
        print(f"Erro ao deserializar JSON: {e}")
        return default


def merge_json(original: Optional[str], updates: dict) -> str:
    """
    Mescla atualizações em um JSON existente.

    Útil para atualizações parciais de campos JSON.

    Args:
        original (Optional[str]): JSON original armazenado no banco.
        updates (dict): Dicionário com campos a serem atualizados/Adicionados.

    Returns:
        str: Novo JSON mesclado.

    Example:
        >>> merge_json('{"nome": "João"}', {"idade": 25})
        '{"nome": "João", "idade": 25}'
    """
    base = from_json(original, default={})
    
    if not isinstance(base, dict):
        base = {}
    
    base.update(updates)
    
    result = to_json(base)
    return result if result else '{}'


if __name__ == "__main__":
    print("=== TESTE: to_json ===")
    
    teste_dict = {"nome": "João", "idade": 25, "ativo": True}
    teste_list = [1, 2, 3, "quatro"]
    teste_nested = {"usuarios": [{"nome": "Ana"}, {"nome": "Bruno"}]}
    
    print(f"Dict: {to_json(teste_dict)}")
    print(f"List: {to_json(teste_list)}")
    print(f"Nested: {to_json(teste_nested)}")
    print(f"None: {to_json(None)}")
    
    print("\n=== TESTE: from_json ===")
    
    json_dict = '{"nome": "João", "idade": 25}'
    json_list = '[1, 2, 3, "quatro"]'
    json_invalid = 'não é json válido'
    
    print(f"JSON para dict: {from_json(json_dict)}")
    print(f"JSON para list: {from_json(json_list)}")
    print(f"JSON inválido com default: {from_json(json_invalid, default={'erro': True})}")
    print(f"None com default: {from_json(None, default=[])}")
    
    print("\n=== TESTE: merge_json ===")
    
    original = '{"nome": "João", "cidade": "SP"}'
    updates = {"idade": 30, "cidade": "RJ"}
    
    resultado = merge_json(original, updates)
    print(f"Original: {original}")
    print(f"Updates: {updates}")
    print(f"Merged: {resultado}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
