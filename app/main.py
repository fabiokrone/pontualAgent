from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.config import settings
from app.api.api import api_router  # Importe o roteador API
from app.db.session import init_db, get_db  # Importando a função init_db e get_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para gestão automatizada de ponto",
    version="0.1.0",
)

# Configuração CORS aprimorada
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, isso deve ser mais restritivo
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],  # Isso pode ajudar em alguns casos
)

# Importe a função de seeds
from app.db.seeds import criar_ou_atualizar_usuarios

# Adicionar evento de inicialização
@app.on_event("startup")
async def startup_db_event():
    # Inicializa o banco de dados (cria as tabelas)
    init_db()
    
    # Obter uma sessão do banco de dados
    db = next(get_db())
    try:
        # Criar ou atualizar usuários com senhas consistentes
        criar_ou_atualizar_usuarios(db)
    finally:
        # Fechar a sessão
        db.close()

# Incluir o roteador de API com prefixo /api
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Bem-vindo ao Sistema Automatizado de Gestão de Ponto"}

@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}