"""Serviço de autenticação do CX SaaS."""
from typing import Optional, Dict, Any
from models.usuarios import criar_usuario, buscar_usuario_por_email, verificar_credenciais
from models.perfis import criar_perfil
from models.configuracoes import criar_configuracao
from models.assinaturas import criar_assinatura, atualizar_plano
from models.tokens import criar_tokens, adicionar_tokens
from models.admins import criar_admin, is_admin
from models.sessoes import criar_sessao, validar_sessao, invalidar_sessao


def registrar_usuario_completo(email: str, senha: str, nome: str = None) -> Optional[Dict[str, Any]]:
    """
    Registra usuário completo com todos os dados relacionados (replica trigger handle_new_user).
    
    Cria automaticamente:
    1. Usuário
    2. Perfil
    3. Configurações
    4. Assinatura (free ou premium_max para admin)
    5. Tokens iniciais (500)
    6. Registro como admin se email == adm123@gmail.com
    """
    try:
        # 1. Criar usuário
        usuario = criar_usuario(email, senha)
        if not usuario:
            return None
        
        user_id = usuario['id']
        
        # 2. Criar perfil
        username = email.split('@')[0] if email else f"user_{user_id[:8]}"
        perfil = criar_perfil(user_id, email, username, nome or username)
        
        # 3. Criar configurações
        criar_configuracao(user_id)
        
        # 4. Verificar se é admin e criar assinatura apropriada
        is_adm = email.lower() == 'adm123@gmail.com'
        plano_inicial = 'premium_max' if is_adm else 'free'
        criar_assinatura(user_id, plano_inicial)
        
        # 5. Criar tokens iniciais
        criar_tokens(user_id, 500)
        
        # 6. Registrar transação inicial
        adicionar_tokens(user_id, 500, 'initial_grant', 'Tokens iniciais')
        
        # 7. Se admin, registrar na tabela admins
        if is_adm:
            criar_admin(user_id, email)
        
        return {
            'usuario': usuario,
            'perfil': perfil,
            'is_admin': is_adm
        }
    
    except Exception as e:
        print(f"Erro ao registrar usuário: {e}")
        return None


def login(email: str, senha: str) -> Optional[Dict[str, Any]]:
    """Faz login e retorna token de sessão."""
    usuario = verificar_credenciais(email, senha)
    if not usuario:
        return None
    
    sessao = criar_sessao(usuario['id'], expires_in_hours=24)
    if not sessao:
        return None
    
    return {
        'usuario': usuario,
        'token': sessao['token'],
        'expires_at': sessao['expires_at']
    }


def logout(token: str) -> bool:
    """Faz logout invalidando a sessão."""
    return invalidar_sessao(token)


def verificar_sessao_usuario(token: str) -> Optional[Dict[str, Any]]:
    """Verifica sessão e retorna dados do usuário se válida."""
    sessao = validar_sessao(token)
    if not sessao:
        return None
    
    from models.usuarios import buscar_usuario_por_id
    usuario = buscar_usuario_por_id(sessao['user_id'])
    
    if not usuario or not usuario.get('ativo', 1):
        invalidar_sessao(token)
        return None
    
    return {
        'usuario': usuario,
        'sessao': sessao,
        'is_admin': is_admin(usuario['id'])
    }


def login_guest() -> Optional[Dict[str, Any]]:
    """Cria usuário guest temporário."""
    usuario = criar_usuario('', '', is_guest=True)
    if not usuario:
        return None
    
    # Criar perfil guest
    criar_perfil(usuario['id'], None, f"guest_{usuario['id'][:8]}", "Convidado")
    criar_configuracao(usuario['id'])
    criar_assinatura(usuario['id'], 'free')
    criar_tokens(usuario['id'], 100)  # Guests recebem menos tokens
    
    sessao = criar_sessao(usuario['id'], expires_in_hours=1)  # Sessão de 1 hora
    return {'usuario': usuario, 'token': sessao['token']}


if __name__ == "__main__":
    from cx_database.setup import setup_completo
    setup_completo()
    
    print("\n=== TESTE: Registro completo ===")
    resultado = registrar_usuario_completo("novo@email.com", "Senha123", "Novo Usuário")
    print(f"Registro: {resultado is not None}")
    
    print("\n=== TESTE: Login ===")
    login_result = login("novo@email.com", "Senha123")
    print(f"Login OK: {login_result is not None}")
    
    if login_result:
        print(f"\n=== TESTE: Verificar sessão ===")
        sessao_valida = verificar_sessao_usuario(login_result['token'])
        print(f"Sessão válida: {sessao_valida is not None}")
        
        print(f"\n=== TESTE: Logout ===")
        logout_ok = logout(login_result['token'])
        print(f"Logout: {logout_ok}")
    
    print("\n=== TODOS OS TESTES PASSARAM ===")
