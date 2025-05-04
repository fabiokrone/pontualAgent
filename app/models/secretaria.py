# app/models/secretaria.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Index
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table

from app.db.session import Base

class Secretaria(Base):
    __tablename__ = "secretarias"
    __table_args__ = ({"schema": "ponto"},)
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    servidores = relationship("Servidor", back_populates="secretaria")