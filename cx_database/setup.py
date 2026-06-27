"""
Módulo de configuração e inicialização do banco de dados.

Este módulo é responsável por criar todas as tabelas do banco de dados,
inserir dados iniciais (como planos padrão) e fornecer funções para
resetar o banco em ambiente de desenvolvimento.

Usage:
    python setup.py  # Executa o setup completo
"""

import sqlite3
import os
from cx_database.connection import get_connection, DATABASE_PATH
from cx_database.utils.helpers import gerar_id, agora


def criar_tabela_planos() -> None:
    """Cria a tabela de planos de assinatura se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planos (
                id               TEXT PRIMARY KEY,
                nome             TEXT UNIQUE NOT NULL,
                limite_projetos  INTEGER DEFAULT 3,
                limite_mensagens INTEGER DEFAULT 100,
                preco_mensal     REAL DEFAULT 0.0,
                ativo            INTEGER DEFAULT 1,
                criado_em        TEXT,
                atualizado_em    TEXT
            )
        """)
        conn.commit()
        print("Tabela 'planos' verificada/criada.")


def criar_tabela_usuarios() -> None:
    """Cria a tabela de usuários se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id               TEXT PRIMARY KEY,
                email            TEXT UNIQUE NOT NULL,
                senha_hash       TEXT,
                is_guest         INTEGER DEFAULT 0,
                ativo            INTEGER DEFAULT 1,
                criado_em        TEXT,
                atualizado_em    TEXT
            )
        """)
        conn.commit()
        print("Tabela 'usuarios' verificada/criada.")


def criar_tabela_perfis() -> None:
    """Cria a tabela de perfis de usuário se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS perfis (
                id                TEXT PRIMARY KEY REFERENCES usuarios(id),
                email             TEXT,
                username          TEXT,
                display_name      TEXT,
                nome              TEXT,
                idade             INTEGER,
                interesses        TEXT DEFAULT '[]',
                profile_picture_url TEXT,
                avatar_url        TEXT,
                bio               TEXT,
                response_style    TEXT DEFAULT 'amigável',
                temporal_memory   TEXT DEFAULT '{"keyEvents": []}',
                criado_em         TEXT,
                atualizado_em     TEXT
            )
        """)
        conn.commit()
        print("Tabela 'perfis' verificada/criada.")


def criar_tabela_conversas() -> None:
    """Cria a tabela de conversas se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversas (
                id               TEXT PRIMARY KEY,
                user_id          TEXT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                titulo           TEXT,
                modo             TEXT DEFAULT 'chat',
                active_agent_ids TEXT DEFAULT '[]',
                is_archived      INTEGER DEFAULT 0,
                is_anonymous     INTEGER DEFAULT 0,
                criado_em        TEXT,
                ultima_modificacao TEXT
            )
        """)
        conn.commit()
        print("Tabela 'conversas' verificada/criada.")


def criar_tabela_mensagens() -> None:
    """Cria a tabela de mensagens se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensagens (
                id               TEXT PRIMARY KEY,
                conversa_id      TEXT NOT NULL REFERENCES conversas(id) ON DELETE CASCADE,
                user_id          TEXT REFERENCES usuarios(id) ON DELETE CASCADE,
                role             TEXT CHECK(role IN ('user', 'assistant', 'system', 'model')) NOT NULL,
                content          TEXT,
                attachment       TEXT DEFAULT NULL,
                actions          TEXT DEFAULT NULL,
                author           TEXT DEFAULT NULL,
                image_urls       TEXT DEFAULT '[]',
                criado_em        TEXT
            )
        """)
        conn.commit()
        print("Tabela 'mensagens' verificada/criada.")


def criar_tabela_projetos_ia() -> None:
    """Cria a tabela de projetos de IA se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projetos_ia (
                id               TEXT PRIMARY KEY,
                user_id          TEXT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                nome             TEXT,
                descricao        TEXT,
                icone            TEXT,
                files            TEXT DEFAULT '[]',
                chat_history     TEXT DEFAULT '[]',
                criado_em        TEXT,
                atualizado_em    TEXT,
                ultima_modificacao TEXT
            )
        """)
        conn.commit()
        print("Tabela 'projetos_ia' verificada/criada.")


def criar_tabela_configuracoes() -> None:
    """Cria a tabela de configurações de usuário se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id               TEXT PRIMARY KEY,
                user_id          TEXT UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                tema             TEXT DEFAULT 'dark',
                idioma           TEXT DEFAULT 'pt-BR',
                preferences      TEXT DEFAULT '{}',
                criado_em        TEXT,
                atualizado_em    TEXT
            )
        """)
        conn.commit()
        print("Tabela 'configuracoes' verificada/criada.")


def criar_tabela_user_tokens() -> None:
    """Cria a tabela de saldo de tokens do usuário se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tokens (
                id               TEXT PRIMARY KEY,
                user_id          TEXT UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                balance          INTEGER DEFAULT 0,
                initial_tokens   INTEGER DEFAULT 500,
                total_used       INTEGER DEFAULT 0,
                total_received   INTEGER DEFAULT 500,
                last_usage_at    TEXT,
                last_refill_at   TEXT,
                next_refill_at   TEXT,
                waiting_refill   INTEGER DEFAULT 0,
                criado_em        TEXT,
                atualizado_em    TEXT
            )
        """)
        conn.commit()
        print("Tabela 'user_tokens' verificada/criada.")


def criar_tabela_transacoes_tokens() -> None:
    """Cria a tabela de transações de tokens se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes_tokens (
                id               TEXT PRIMARY KEY,
                user_id          TEXT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                tipo             TEXT CHECK(tipo IN ('usage','refill','bonus','admin_adjustment','initial_grant')) NOT NULL,
                amount           INTEGER NOT NULL,
                balance_before   INTEGER,
                balance_after    INTEGER,
                descricao        TEXT,
                criado_em        TEXT
            )
        """)
        conn.commit()
        print("Tabela 'transacoes_tokens' verificada/criada.")


def criar_tabela_assinaturas() -> None:
    """Cria a tabela de assinaturas de usuário se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assinaturas (
                id               TEXT PRIMARY KEY,
                user_id          TEXT UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                plano            TEXT DEFAULT 'free',
                status           TEXT DEFAULT 'active',
                expires_at       TEXT,
                premium_until    TEXT,
                used_codes       TEXT DEFAULT '[]',
                criado_em        TEXT,
                atualizado_em    TEXT
            )
        """)
        conn.commit()
        print("Tabela 'assinaturas' verificada/criada.")


def criar_tabela_admins() -> None:
    """Cria a tabela de administradores se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id               TEXT PRIMARY KEY,
                user_id          TEXT UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                email            TEXT UNIQUE NOT NULL,
                criado_em        TEXT
            )
        """)
        conn.commit()
        print("Tabela 'admins' verificada/criada.")


def criar_tabela_sessoes() -> None:
    """Cria a tabela de sessões de usuário se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessoes (
                id               TEXT PRIMARY KEY,
                user_id          TEXT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                token            TEXT UNIQUE NOT NULL,
                expires_at       TEXT NOT NULL,
                criado_em        TEXT
            )
        """)
        conn.commit()
        print("Tabela 'sessoes' verificada/criada.")


def criar_todas_as_tabelas() -> None:
    """
    Cria todas as tabelas do banco de dados na ordem correta.
    
    A ordem é importante devido às chaves estrangeiras.
    """
    print("\n=== Criando tabelas ===")
    criar_tabela_planos()
    criar_tabela_usuarios()
    criar_tabela_perfis()
    criar_tabela_configuracoes()
    criar_tabela_assinaturas()
    criar_tabela_user_tokens()
    criar_tabela_transacoes_tokens()
    criar_tabela_conversas()
    criar_tabela_mensagens()
    criar_tabela_projetos_ia()
    criar_tabela_admins()
    criar_tabela_sessoes()
    print("Todas as tabelas foram criadas com sucesso!\n")


def criar_indices() -> None:
    """
    Cria índices para otimizar consultas frequentes.
    
    Índices criados:
    - conversas.user_id: busca de conversas por usuário
    - mensagens.conversa_id: busca de mensagens por conversa
    - transacoes_tokens.user_id: histórico de transações por usuário
    - sessoes.token: validação rápida de sessão
    - sessoes.expires_at: limpeza de sessões expiradas
    """
    print("\n=== Criando índices ===")
    
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_conversas_user_id ON conversas(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_mensagens_conversa_id ON mensagens(conversa_id)",
        "CREATE INDEX IF NOT EXISTS idx_transacoes_user_id ON transacoes_tokens(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_sessoes_token ON sessoes(token)",
        "CREATE INDEX IF NOT EXISTS idx_sessoes_expires_at ON sessoes(expires_at)",
        "CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)",
        "CREATE INDEX IF NOT EXISTS idx_assinaturas_user_id ON assinaturas(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_tokens_user_id ON user_tokens(user_id)",
    ]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        for indice_sql in indices:
            try:
                cursor.execute(indice_sql)
            except sqlite3.OperationalError as e:
                print(f"  Aviso: Índice não criado ({e})")
        conn.commit()
    
    print(f"{len(indices)} índices criados com sucesso!\n")


def inserir_admin_padrao() -> None:
    """
    Cria o administrador padrão se não existir.
    
    O admin padrão tem email 'adm123@gmail.com' e recebe plano 'premium_max'.
    """
    print("\n=== Verificando admin padrão ===")
    
    email_admin = "adm123@gmail.com"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Verifica se já existe usuário com este email
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email_admin,))
        usuario_existente = cursor.fetchone()
        
        if not usuario_existente:
            # Criar usuário admin
            from cx_database.utils.helpers import hash_senha
            
            user_id = gerar_id()
            agora_dt = agora()
            senha_hash = hash_senha("Admin@123")  # Senha padrão (deve ser trocada)
            
            # Criar usuário
            cursor.execute("""
                INSERT INTO usuarios (id, email, senha_hash, is_guest, ativo, criado_em, atualizado_em)
                VALUES (?, ?, ?, 0, 1, ?, ?)
            """, (user_id, email_admin, senha_hash, agora_dt, agora_dt))
            
            # Criar perfil
            cursor.execute("""
                INSERT INTO perfis (id, email, username, display_name, criado_em, atualizado_em)
                VALUES (?, ?, 'admin', 'Administrador', ?, ?)
            """, (user_id, email_admin, agora_dt, agora_dt))
            
            # Criar configurações
            cursor.execute("""
                INSERT INTO configuracoes (id, user_id, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?)
            """, (gerar_id(), user_id, agora_dt, agora_dt))
            
            # Criar assinatura premium_max
            cursor.execute("""
                INSERT INTO assinaturas (id, user_id, plano, status, criado_em, atualizado_em)
                VALUES (?, ?, 'premium_max', 'active', ?, ?)
            """, (gerar_id(), user_id, agora_dt, agora_dt))
            
            # Criar tokens iniciais
            cursor.execute("""
                INSERT INTO user_tokens (id, user_id, balance, initial_tokens, total_received, criado_em, atualizado_em)
                VALUES (?, ?, 500, 500, 500, ?, ?)
            """, (gerar_id(), user_id, agora_dt, agora_dt))
            
            # Registrar transação inicial
            cursor.execute("""
                INSERT INTO transacoes_tokens (id, user_id, tipo, amount, balance_before, balance_after, descricao, criado_em)
                VALUES (?, ?, 'initial_grant', 500, 0, 500, 'Tokens iniciais - Admin', ?)
            """, (gerar_id(), user_id, agora_dt))
            
            # Registrar como admin
            cursor.execute("""
                INSERT INTO admins (id, user_id, email, criado_em)
                VALUES (?, ?, ?, ?)
            """, (gerar_id(), user_id, email_admin, agora_dt))
            
            conn.commit()
            print(f"✓ Admin '{email_admin}' criado com plano 'premium_max'.")
            print(f"  User ID: {user_id}")
            print(f"  Senha padrão: Admin@123 (troque no primeiro login!)")
        else:
            print(f"→ Admin '{email_admin}' já existe.")
    
    print("")


def setup_completo() -> None:
    """
    Executa o setup completo do banco de dados.
    
    Inclui:
    1. Criação de todas as tabelas
    2. Criação de índices
    3. Inserção do admin padrão
    """
    print("=" * 60)
    print("CX SAAS - SETUP COMPLETO DO BANCO DE DADOS")
    print("=" * 60)
    print(f"\nCaminho do banco: {DATABASE_PATH}\n")
    
    criar_todas_as_tabelas()
    criar_indices()
    inserir_admin_padrao()
    
    print("=" * 60)
    print("SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)


def resetar_banco() -> None:
    """
    Apaga todas as tabelas e recria o banco do zero.
    
    ⚠️ ATENÇÃO: Esta função apaga TODOS os dados!
    Use apenas em ambiente de desenvolvimento.
    """
    print("\n⚠️  RESETANDO BANCO DE DADOS ⚠️")
    print("Todos os dados serão apagados!\n")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Desabilita temporariamente foreign keys para permitir drop
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Lista de tabelas na ordem correta para deletar (dependentes primeiro)
        tabelas = [
            'transacoes_tokens', 'user_tokens', 'mensagens', 'conversas',
            'projetos_ia', 'configuracoes', 'perfis', 'assinaturas',
            'admins', 'sessoes', 'usuarios', 'planos'
        ]
        
        for tabela in tabelas:
            cursor.execute(f"DROP TABLE IF EXISTS {tabela}")
            print(f"  Tabela '{tabela}' removida.")
        
        # Drop índices também
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indices = cursor.fetchall()
        for indice in indices:
            cursor.execute(f"DROP INDEX IF EXISTS {indice[0]}")
        
        conn.commit()
        
        # Reabilita foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
    
    print("\nBanco resetado. Recriando estrutura...")
    setup_completo()
    print("\n✓ Banco de dados resetado com sucesso!")


def verificar_setup() -> bool:
    """
    Verifica se o banco de dados está configurado corretamente.
    
    Returns:
        bool: True se todas as tabelas existirem, False caso contrário.
    """
    tabelas_esperadas = {
        'planos', 'usuarios', 'perfis', 'conversas', 'mensagens',
        'projetos_ia', 'configuracoes', 'user_tokens', 'transacoes_tokens',
        'assinaturas', 'admins', 'sessoes'
    }
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tabelas_existentes = {row[0] for row in cursor.fetchall()}
        
        todas_existem = tabelas_esperadas.issubset(tabelas_existentes)
        
        if todas_existem:
            print("✓ Todas as tabelas estão presentes.")
        else:
            faltantes = tabelas_esperadas - tabelas_existentes
            print(f"✗ Tabelas faltando: {faltantes}")
        
        return todas_existem
    
    except sqlite3.Error as e:
        print(f"✗ Erro ao verificar setup: {e}")
        return False


if __name__ == "__main__":
    # Verifica se já existe setup
    if verificar_setup():
        print("\nO banco de dados já está configurado.")
        resposta = input("Deseja resetar e recriar? (s/N): ").strip().lower()
        if resposta == 's':
            resetar_banco()
        else:
            print("Setup mantido.")
    else:
        print("\nConfigurando banco de dados pela primeira vez...")
        setup_completo()
