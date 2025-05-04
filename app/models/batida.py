# app/models/batida.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class BatidaOriginal(Base):
    __tablename__ = "batidas_originais"
    __table_args__ = ({"schema": "ponto"},)  # Corrigido: adicionada a tupla e vírgula
    
    id = Column(Integer, primary_key=True)
    servidor_id = Column(Integer, ForeignKey("ponto.servidores.id", ondelete="CASCADE"))
    data_hora = Column(DateTime, nullable=False)
    tipo = Column(String(10), nullable=False)
    dispositivo = Column(String(50))
    localizacao = Column(String(100))
    importado_em = Column(DateTime, default=func.now())
    arquivo_origem = Column(String(200))
    created_at = Column(DateTime, default=func.now())
    
    # Relacionamentos
    servidor = relationship("Servidor", back_populates="batidas_originais")

class BatidaProcessada(Base):
    __tablename__ = "batidas_processadas"
    __table_args__ = ({"schema": "ponto"},)  # Corrigido: adicionada a tupla e vírgula
    
    id = Column(Integer, primary_key=True)
    batida_original_id = Column(Integer, ForeignKey("ponto.batidas_originais.id", ondelete="SET NULL"))
    servidor_id = Column(Integer, ForeignKey("ponto.servidores.id", ondelete="CASCADE"))
    data_hora = Column(DateTime, nullable=False)
    tipo = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False)
    processado_em = Column(DateTime, default=func.now())
    justificativa_id = Column(Integer, ForeignKey("ponto.justificativas.id", ondelete="SET NULL"))
    processado_por = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    servidor = relationship("Servidor", back_populates="batidas_processadas")
    batida_original = relationship("BatidaOriginal", backref="batida_processada")
    justificativa = relationship("Justificativa", back_populates="batidas_processadas")