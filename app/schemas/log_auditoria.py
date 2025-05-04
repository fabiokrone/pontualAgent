from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class LogAuditoriaBase(BaseModel):
    acao: str
    tabela: str
    registro_id: Optional[int] = None
    detalhes: Optional[str] = None
    ip: Optional[str] = None

class LogAuditoriaCreate(LogAuditoriaBase):
    pass

class LogAuditoria(LogAuditoriaBase):
    id: int
    usuario_id: Optional[int] = None
    data_hora: datetime

    class Config:
        orm_mode = True
