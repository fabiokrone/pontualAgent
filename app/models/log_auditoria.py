from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"
    __table_args__ = ({"schema": "ponto"},)

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("ponto.usuarios.id"), nullable=True)
    acao = Column(String(50), nullable=False)
    tabela = Column(String(50), nullable=False)
    registro_id = Column(Integer, nullable=True)
    detalhes = Column(Text, nullable=True)
    ip = Column(String(50), nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamento com o usuário (opcional)
    usuario = relationship("Usuario", back_populates="logs_auditoria")
