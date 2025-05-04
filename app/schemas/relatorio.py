# app/schemas/relatorio.py
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, date

class RelatorioBase(BaseModel):
    tipo: str
    periodo_inicio: date
    periodo_fim: date
    secretaria_id: Optional[int] = None
    servidor_id: Optional[int] = None
    arquivo_url: str
    gerado_por: Optional[str] = None
    enviado: bool = False
    destinatarios: Optional[Dict[str, Any]] = None

class RelatorioCreate(RelatorioBase):
    pass

class RelatorioResponse(RelatorioBase):
    id: int
    gerado_em: datetime
    enviado_em: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True