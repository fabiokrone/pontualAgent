# app/models/justificativa.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class Justificativa(Base):
    __tablename__ = "justificativas"
    __table_args__ = ({"schema": "ponto"},)  # Corrigido: adicionada a tupla e vírgula
    
    id = Column(Integer, primary_key=True)
    servidor_id = Column(Integer, ForeignKey("ponto.servidores.id", ondelete="CASCADE"))
    data = Column(Date, nullable=False)
    tipo = Column(String(50), nullable=False)
    descricao = Column(Text, nullable=False)
    anexo_url = Column(String(255))
    status = Column(String(20), nullable=False, default="pendente")
    criado_em = Column(DateTime, default=func.now())
    aprovado_por = Column(String(100))
    aprovado_em = Column(DateTime)
    canal_origem = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    servidor = relationship("Servidor", back_populates="justificativas")
    batidas_processadas = relationship("BatidaProcessada", back_populates="justificativa")