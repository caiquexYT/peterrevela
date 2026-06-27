"""
Módulo de modelos do CX Database.

Este módulo exporta todos os modelos para facilitar o uso.
"""

from .usuarios import (
    criar_usuario, buscar_usuario_por_id, buscar_usuario_por_email,
    listar_usuarios, atualizar_usuario, deletar_usuario, verificar_credenciais
)

from .perfis import (
    criar_perfil, buscar_perfil_por_user_id, atualizar_perfil
)

from .configuracoes import (
    criar_configuracao, buscar_configuracao_por_user_id, atualizar_configuracao
)

from .assinaturas import (
    criar_assinatura, buscar_assinatura_por_user_id, atualizar_plano
)

from .tokens import (
    criar_tokens, buscar_tokens_por_user_id, consumir_tokens_atomico,
    adicionar_tokens, get_saldo
)

from .transacoes_tokens import (
    registrar_transacao, buscar_transacao_por_id, listar_transacoes_por_usuario
)

from .conversas import (
    criar_conversa, buscar_conversa_por_id, listar_conversas_por_usuario, arquivar_conversa
)

from .mensagens import (
    criar_mensagem, buscar_mensagem_por_id, listar_mensagens_por_conversa
)

from .projetos_ia import (
    criar_projeto, buscar_projeto_por_id, listar_projetos_por_usuario
)

from .admins import (
    criar_admin, buscar_admin_por_user_id, is_admin
)

from .sessoes import (
    criar_sessao, validar_sessao, invalidar_sessao, limpar_sessoes_expiradas
)

__all__ = [
    # Usuários
    'criar_usuario', 'buscar_usuario_por_id', 'buscar_usuario_por_email',
    'listar_usuarios', 'atualizar_usuario', 'deletar_usuario', 'verificar_credenciais',
    
    # Perfis
    'criar_perfil', 'buscar_perfil_por_user_id', 'atualizar_perfil',
    
    # Configurações
    'criar_configuracao', 'buscar_configuracao_por_user_id', 'atualizar_configuracao',
    
    # Assinaturas
    'criar_assinatura', 'buscar_assinatura_por_user_id', 'atualizar_plano',
    
    # Tokens
    'criar_tokens', 'buscar_tokens_por_user_id', 'consumir_tokens_atomico',
    'adicionar_tokens', 'get_saldo',
    
    # Transações
    'registrar_transacao', 'buscar_transacao_por_id', 'listar_transacoes_por_usuario',
    
    # Conversas
    'criar_conversa', 'buscar_conversa_por_id', 'listar_conversas_por_usuario', 'arquivar_conversa',
    
    # Mensagens
    'criar_mensagem', 'buscar_mensagem_por_id', 'listar_mensagens_por_conversa',
    
    # Projetos IA
    'criar_projeto', 'buscar_projeto_por_id', 'listar_projetos_por_usuario',
    
    # Admins
    'criar_admin', 'buscar_admin_por_user_id', 'is_admin',
    
    # Sessões
    'criar_sessao', 'validar_sessao', 'invalidar_sessao', 'limpar_sessoes_expiradas',
]
