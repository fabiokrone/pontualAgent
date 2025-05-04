# app/models/servidor.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table

from app.db.session import Base

class Servidor(Base):
    __tablename__ = "servidores"
    __table_args__ = (
        Index("ix_servidores_matricula", "matricula"),
        Index("ix_servidores_cpf", "cpf"),
        Index("ix_servidores_email", "email"),
        {"schema": "ponto"},  # Note a vírgula adicionada aqui
    )
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    matricula = Column(String(20), unique=True, nullable=False)
    cpf = Column(String(11), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Chave estrangeira
    secretaria_id = Column(Integer, ForeignKey("ponto.secretarias.id"))
    
    # Relacionamentos
    secretaria = relationship("Secretaria", back_populates="servidores")
    batidas_originais = relationship("BatidaOriginal", back_populates="servidor")
    batidas_processadas = relationship("BatidaProcessada", back_populates="servidor")
    justificativas = relationship("Justificativa", back_populates="servidor")