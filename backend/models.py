"""
Modelos de dados (tabelas) para o banco SQLite do CxIA.
Cria todas as tabelas necessárias para o funcionamento do sistema.
"""

import sqlite3


def criar_tabela_usuarios(conn: sqlite3.Connection) -> None:
    """Cria a tabela de usuários."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT,
            photo_url TEXT,
            provider TEXT DEFAULT 'email',
            is_guest INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            criado_em TEXT NOT NULL,
            atualizado_em TEXT NOT NULL
        )
    """)


def criar_tabela_perfis(conn: sqlite3.Connection) -> None:
    """Cria a tabela de perfis de usuário."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS perfis (
            id TEXT PRIMARY KEY REFERENCES usuarios(id),
            email TEXT,
            username TEXT,
            display_name TEXT,
            nome TEXT,
            idade INTEGER,
            interesses TEXT DEFAULT '[]',
            profile_picture_url TEXT,
            avatar_url TEXT,
            bio TEXT,
            response_style TEXT DEFAULT 'amigável',
            temporal_memory TEXT DEFAULT '{"keyEvents": []}',
            criado_em TEXT,
            atualizado_em TEXT
        )
    """)


def criar_tabela_conversas(conn: sqlite3.Connection) -> None:
    """Cria a tabela de conversas."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversas (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            titulo TEXT NOT NULL DEFAULT 'Nova conversa',
            modo TEXT DEFAULT 'chat',
            active_agent_ids TEXT DEFAULT '[]',
            is_private INTEGER DEFAULT 0,
            is_archived INTEGER DEFAULT 0,
            is_anonymous INTEGER DEFAULT 0,
            criado_em TEXT NOT NULL,
            atualizado_em TEXT NOT NULL
        )
    """)


def criar_tabela_mensagens(conn: sqlite3.Connection) -> None:
    """Cria a tabela de mensagens."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id TEXT PRIMARY KEY,
            conversa_id TEXT NOT NULL REFERENCES conversas(id) ON DELETE CASCADE,
            user_id TEXT REFERENCES usuarios(id) ON DELETE CASCADE,
            role TEXT CHECK(role IN ('user', 'assistant', 'system', 'model')) NOT NULL,
            content TEXT NOT NULL,
            thinking_time REAL DEFAULT NULL,
            attachment TEXT DEFAULT NULL,
            actions TEXT DEFAULT NULL,
            author TEXT DEFAULT NULL,
            image_urls TEXT DEFAULT '[]',
            criado_em TEXT NOT NULL
        )
    """)


def criar_tabela_projetos_ia(conn: sqlite3.Connection) -> None:
    """Cria a tabela de projetos de IA."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projetos_ia (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            nome TEXT,
            descricao TEXT,
            icone TEXT,
            files TEXT DEFAULT '[]',
            chat_history TEXT DEFAULT '[]',
            criado_em TEXT,
            atualizado_em TEXT,
            ultima_modificacao TEXT
        )
    """)


def criar_tabela_configuracoes(conn: sqlite3.Connection) -> None:
    """Cria a tabela de configurações por usuário."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            tema TEXT DEFAULT 'dark',
            idioma TEXT DEFAULT 'pt-BR',
            preferences TEXT DEFAULT '{}',
            criado_em TEXT,
            atualizado_em TEXT
        )
    """)


def criar_tabela_tokens_usuarios(conn: sqlite3.Connection) -> None:
    """Cria a tabela de saldo de tokens dos usuários."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tokens_usuarios (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            tokens_usados INTEGER DEFAULT 0,
            limite_tokens INTEGER DEFAULT 50000,
            janela_inicio TEXT NOT NULL,
            plano TEXT DEFAULT 'free',
            atualizado_em TEXT NOT NULL
        )
    """)


def criar_tabela_transacoes_tokens(conn: sqlite3.Connection) -> None:
    """Cria a tabela de histórico de transações de tokens."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transacoes_tokens (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            tipo TEXT CHECK(tipo IN ('usage','refill','bonus','admin_adjustment','initial_grant')) NOT NULL,
            amount INTEGER NOT NULL,
            balance_before INTEGER,
            balance_after INTEGER,
            descricao TEXT,
            criado_em TEXT NOT NULL
        )
    """)


def criar_tabela_assinaturas(conn: sqlite3.Connection) -> None:
    """Cria a tabela de assinaturas/planos dos usuários."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assinaturas (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            plano TEXT DEFAULT 'free',
            status TEXT DEFAULT 'active',
            expires_at TEXT,
            premium_until TEXT,
            used_codes TEXT DEFAULT '[]',
            criado_em TEXT,
            atualizado_em TEXT
        )
    """)


def criar_tabela_admins(conn: sqlite3.Connection) -> None:
    """Cria a tabela de administradores."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            email TEXT UNIQUE NOT NULL,
            criado_em TEXT NOT NULL
        )
    """)


def criar_tabela_sessoes(conn: sqlite3.Connection) -> None:
    """Cria a tabela de sessões ativas."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessoes (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            criado_em TEXT NOT NULL
        )
    """)


def criar_indices(conn: sqlite3.Connection) -> None:
    """Cria índices para otimizar consultas frequentes."""
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_conversas_user_id ON conversas(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_conversas_atualizado_em ON conversas(atualizado_em DESC)",
        "CREATE INDEX IF NOT EXISTS idx_mensagens_conversa_id ON mensagens(conversa_id)",
        "CREATE INDEX IF NOT EXISTS idx_mensagens_criado_em ON mensagens(criado_em ASC)",
        "CREATE INDEX IF NOT EXISTS idx_transacoes_user_id ON transacoes_tokens(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_sessoes_token ON sessoes(token)",
        "CREATE INDEX IF NOT EXISTS idx_sessoes_expires_at ON sessoes(expires_at)",
        "CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)",
    ]
    
    for indice in indices:
        conn.execute(indice)


def criar_todas_as_tabelas(conn: sqlite3.Connection) -> None:
    """
    Cria todas as tabelas do banco de dados.
    
    Args:
        conn: Conexão ativa com o banco SQLite.
    """
    criar_tabela_usuarios(conn)
    criar_tabela_perfis(conn)
    criar_tabela_conversas(conn)
    criar_tabela_mensagens(conn)
    criar_tabela_projetos_ia(conn)
    criar_tabela_configuracoes(conn)
    criar_tabela_tokens_usuarios(conn)
    criar_tabela_transacoes_tokens(conn)
    criar_tabela_assinaturas(conn)
    criar_tabela_admins(conn)
    criar_tabela_sessoes(conn)
    criar_indices(conn)


if __name__ == "__main__":
    # Teste manual de criação de tabelas
    import os
    import sys
    
    # Adicionar o diretório pai ao path para imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from database import get_connection
    
    print("=== TESTE: Criar todas as tabelas ===")
    
    with get_connection() as conn:
        criar_todas_as_tabelas(conn)
        conn.commit()
        
        # Verificar se as tabelas foram criadas
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tabelas = [row[0] for row in cursor.fetchall()]
        print(f"Tabelas criadas: {tabelas}")
        
        print("\n=== TODAS AS TABELAS CRIADAS COM SUCESSO ===")
