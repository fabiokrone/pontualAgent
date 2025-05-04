# app/models/relatorio.py
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base

class Relatorio(Base):
    __tablename__ = "relatorios"
    __table_args__ = ({"schema": "ponto"},)  # Corrigido: adicionada a tupla e vírgula
    
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    secretaria_id = Column(Integer, ForeignKey("ponto.secretarias.id", ondelete="SET NULL"))
    servidor_id = Column(Integer, ForeignKey("ponto.servidores.id", ondelete="SET NULL"))
    arquivo_url = Column(String(255), nullable=False)
    gerado_em = Column(DateTime, default=func.now())
    gerado_por = Column(String(100))
    enviado = Column(Boolean, default=False)
    enviado_em = Column(DateTime)
    destinatarios = Column(JSONB)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    secretaria = relationship("Secretaria")
    servidor = relationship("Servidor")