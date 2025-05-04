# app/core/config.py
"""
Módulo de configuração da aplicação.
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Configurações da aplicação
    PROJECT_NAME: str = Field(default="Sistema Automatizado de Gestão de Ponto")
    API_PREFIX: str = Field(default="/api")
    CORS_ORIGINS: str = Field(default="http://localhost,http://localhost:8000,http://localhost:3000")
    DEBUG: bool = Field(default=False)
    
    # Configurações do banco de dados
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="gestao_ponto")
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    
    # Configurações avançadas do banco de dados
    DB_POOL_SIZE: int = Field(default=5)
    DB_MAX_OVERFLOW: int = Field(default=10)
    DB_POOL_TIMEOUT: int = Field(default=30)
    DB_POOL_RECYCLE: int = Field(default=1800)
    DB_ECHO_LOG: bool = Field(default=False)
    
    # Configurações de autenticação
    SECRET_KEY: str = Field(default="sua_chave_secreta_padrao_deve_ser_alterada_em_producao")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = Field(default=1)  # Validade do token de reset em horas
    
    # Configurações de integração WhatsApp
    WHATSAPP_API_TYPE: str = Field(default="official")
    WHATSAPP_API_URL: Optional[str] = Field(default=None)
    WHATSAPP_API_TOKEN: Optional[str] = Field(default=None)
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = Field(default=None)
    
    
    # Configurações de envio de e-mail (Postmark)
    POSTMARK_SERVER_TOKEN: Optional[str] = Field(default=None) 
    EMAILS_FROM_EMAIL: Optional[str] = Field(default=None) 
    EMAILS_FROM_NAME: Optional[str] = Field(default="PontoAgent") 
    FRONTEND_URL: str = Field(default="http://localhost:3000") 
    
    # Adicione essas configurações na classe Settings
    # Configurações de SMTP para Postmark
    SMTP_HOST: str = Field(default="smtp.postmarkapp.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default=None)  # Seu token do Postmark
    SMTP_PASSWORD: str = Field(default=None)  # Mesmo token do Postmark
    SMTP_MESSAGE_STREAM: str = Field(default="pontoagent")  # Sua message stream
            
    
    # Configurações adicionais que estão sendo passadas como variáveis de ambiente
    DATABASE_URL: Optional[str] = Field(default=None)
    PGADMIN_EMAIL: Optional[str] = Field(default=None)
    PGADMIN_PASSWORD: Optional[str] = Field(default=None)
    ALLOWED_HOSTS: Optional[str] = Field(default=None)
    CORS_ALLOWED_ORIGINS: Optional[str] = Field(default=None)
    NEXT_PUBLIC_API_URL: Optional[str] = Field(default=None)
    NEXT_PUBLIC_API_DOCKER_URL: Optional[str] = Field(default=None)

    # Propriedade calculada para URI do banco
    @property
    def DATABASE_URI(self) -> str:
        # Usar DATABASE_URL se estiver definido, caso contrário usar os campos individuais
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Processar CORS_ORIGINS para lista
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        # Usar CORS_ALLOWED_ORIGINS se estiver definido, caso contrário usar CORS_ORIGINS
        cors_string = self.CORS_ALLOWED_ORIGINS if self.CORS_ALLOWED_ORIGINS else self.CORS_ORIGINS
        return [origin.strip() for origin in cors_string.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "allow"  # Permite campos extras não declarados

# Instância única de configurações
settings = Settings()