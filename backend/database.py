"""
Database connection module for CxIA Backend.
Gerencia conexão SQLite com WAL mode e foreign keys ativadas.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Generator

# Caminho do banco de dados (configurável via variável de ambiente)
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/cxia.db")


def get_connection() -> sqlite3.Connection:
    """
    Cria e retorna uma nova conexão com o SQLite.
    
    Configurações aplicadas:
    - row_factory = sqlite3.Row (retorna resultados como dicionários)
    - PRAGMA journal_mode=WAL (suporta múltiplas conexões simultâneas)
    - PRAGMA foreign_keys=ON (garante integridade referencial)
    
    Returns:
        sqlite3.Connection: Conexão com o banco de dados.
    """
    # Criar diretório se não existir
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Habilitar WAL mode para suportar múltiplas leituras/escritas simultâneas
    conn.execute("PRAGMA journal_mode=WAL")
    
    # Ativar chaves estrangeiras
    conn.execute("PRAGMA foreign_keys=ON")
    
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager para gerenciar conexões com o banco de dados.
    Garante que a conexão seja sempre fechada corretamente.
    
    Uso:
        with get_db() as conn:
            conn.execute("SELECT * FROM usuarios")
    
    Yields:
        sqlite3.Connection: Conexão com o banco de dados.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas se não existirem.
    Deve ser chamado apenas uma vez na inicialização da aplicação.
    """
    from models import criar_todas_as_tabelas
    
    with get_db() as conn:
        criar_todas_as_tabelas(conn)
        conn.commit()
