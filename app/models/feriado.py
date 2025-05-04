# app/models/feriado.py
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, func

from app.db.session import Base

class Feriado(Base):
    __tablename__ = "feriados"
    __table_args__ = ({"schema": "ponto"},)  # Corrigido: adicionada a tupla e vírgula
    
    id = Column(Integer, primary_key=True)
    data = Column(Date, unique=True, nullable=False)
    descricao = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)
    ambito = Column(String(20), nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())