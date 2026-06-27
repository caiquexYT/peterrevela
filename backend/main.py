"""
Aplicação principal FastAPI para o backend CxIA.
Expõe API REST completa para o frontend React.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar routers
from routers import auth, conversas, mensagens, tokens
from schemas import HealthResponse

# Configurações
DATABASE_URL = os.getenv("DATABASE_URL", "http://localhost:8000")
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:8080"
).split(",")

# Criar aplicação FastAPI
app = FastAPI(
    title="CxIA API",
    description="Backend para o SaaS CxIA - Assistente de IA para projetos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(conversas.router)
app.include_router(mensagens.router)
app.include_router(tokens.router)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Verifica se a API está online e saudável.
    
    Use este endpoint para monitorar a saúde do backend.
    """
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    """
    Endpoint raiz com informações da API.
    """
    return {
        "name": "CxIA API",
        "version": "1.0.0",
        "description": "Backend para o SaaS CxIA",
        "docs": "/docs",
        "health": "/health"
    }


# Inicializar banco de dados ao iniciar a aplicação
@app.on_event("startup")
async def startup_event():
    """Inicializa o banco de dados na inicialização."""
    from database import init_db
    from models import criar_todas_as_tabelas
    
    try:
        from database import get_connection
        
        with get_connection() as conn:
            criar_todas_as_tabelas(conn)
            conn.commit()
        
        print("✅ Banco de dados inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        raise


if __name__ == "__main__":
    import uvicorn
    
    # Obter porta das variáveis de ambiente (padrão: 8000)
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 Iniciando CxIA Backend na porta {port}")
    print(f"📚 Documentação: http://localhost:{port}/docs")
    print(f"❤️ Health check: http://localhost:{port}/health")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
