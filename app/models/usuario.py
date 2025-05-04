# app/models/usuario.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = ({"schema": "ponto"},)
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    nome_completo = Column(String(100), nullable=False)
    senha_hash = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True)
    perfil = Column(String(20), nullable=False)  # admin, gestor, usuario
    secretaria_id = Column(Integer, ForeignKey("ponto.secretarias.id"))
    servidor_id = Column(Integer, ForeignKey("ponto.servidores.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Campos para recuperação de senha
    reset_token = Column(String(100), nullable=True, index=True)  # Token para resetar senha
    reset_token_expires_at = Column(DateTime, nullable=True)  # Data de expiração do token
    
    logs_auditoria = relationship("LogAuditoria", back_populates="usuario")
    
    # Relacionamentos
    secretaria = relationship("Secretaria", backref="usuarios")
    servidor = relationship("Servidor", backref="usuarios")