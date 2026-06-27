"""
Módulo de gerenciamento de conexão com o banco de dados SQLite.

Este módulo fornece uma interface segura e reutilizável para conectar
ao banco de dados SQLite, usando context managers para garantir que
as conexões sejam sempre fechadas corretamente.
"""

import sqlite3
import os
from typing import Optional


# Camho do banco de dados, configurável via variável de ambiente
DATABASE_PATH = os.getenv(
    'DATABASE_PATH',
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cx_saas.db')
)


def garantir_diretorio_data() -> None:
    """
    Garante que o diretório 'data' existe para armazenar o arquivo do banco.
    
    Cria o diretório automaticamente se ele não existir.
    """
    diretorio = os.path.dirname(DATABASE_PATH)
    if not os.path.exists(diretorio):
        os.makedirs(diretorio, exist_ok=True)
        print(f"Diretório criado: {diretorio}")


def get_connection() -> sqlite3.Connection:
    """
    Cria e retorna uma nova conexão com o banco de dados SQLite.
    
    Configurações aplicadas:
    - check_same_thread=False: permite múltiplas requisições simultâneas (FastAPI)
    - row_factory=sqlite3.Row: permite acessar resultados como dicionários
    - PRAGMA journal_mode=WAL: habilita Write-Ahead Logging para concorrência
    - PRAGMA foreign_keys=ON: ativa integridade referencial
    
    Returns:
        sqlite3.Connection: Conexão ativa com o banco de dados.
    
    Raises:
        sqlite3.Error: Se houver erro ao conectar ao banco.
    """
    garantir_diretorio_data()
    
    conn = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False,  # Necessário para FastAPI/múltiplos threads
        timeout=30.0  # Timeout de 30 segundos para operações bloqueadas
    )
    conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
    conn.execute("PRAGMA journal_mode = WAL")  # WAL para melhor concorrência
    conn.execute("PRAGMA foreign_keys = ON")  # Habilita chaves estrangeiras
    
    return conn


class DatabaseConnection:
    """
    Context manager para gerenciar conexões com o banco de dados.
    
    Garante que a conexão seja sempre fechada, mesmo em caso de exceções.
    
    Usage:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios")
            resultados = cursor.fetchall()
    
    Yields:
        sqlite3.Connection: Conexão ativa com o banco.
    """
    
    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None
    
    def __enter__(self) -> sqlite3.Connection:
        """Abre a conexão com o banco."""
        self.conn = get_connection()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Fecha a conexão, independentemente de haver exceção ou não."""
        if self.conn:
            self.conn.close()


# Alias para uso mais simples
conexao_db = DatabaseConnection


def testar_conexao() -> bool:
    """
    Testa se a conexão com o banco de dados está funcionando.
    
    Returns:
        bool: True se a conexão for bem-sucedida, False caso contrário.
    """
    try:
        with conexao_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            resultado = cursor.fetchone()
            return resultado is not None and resultado[0] == 1
    except sqlite3.Error as e:
        print(f"Erro ao testar conexão: {e}")
        return False


if __name__ == "__main__":
    print("=== TESTE: Conexão com o banco de dados ===")
    
    print("\n1. Testando função testar_conexao():")
    sucesso = testar_conexao()
    print(f"Conexão teste: {'SUCESSO' if sucesso else 'FALHOU'}")
    
    print("\n2. Testando context manager:")
    try:
        with conexao_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            versao = cursor.fetchone()[0]
            print(f"Versão do SQLite: {versao}")
            print(f"Caminho do banco: {DATABASE_PATH}")
            print("Context manager: SUCESSO")
    except Exception as e:
        print(f"Erro no context manager: {e}")
    
    print("\n3. Testando get_connection() direto:")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        print(f"Tabelas existentes: {[t[0] for t in tabelas]}")
        conn.close()
        print("get_connection(): SUCESSO")
    except Exception as e:
        print(f"Erro no get_connection: {e}")
