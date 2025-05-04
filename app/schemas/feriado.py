# app/schemas/feriado.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class FeriadoBase(BaseModel):
    data: date
    descricao: str
    tipo: str
    ambito: str
    ativo: bool = True

class FeriadoCreate(FeriadoBase):
    pass

class FeriadoUpdate(BaseModel):
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    ambito: Optional[str] = None
    ativo: Optional[bool] = None

class FeriadoInDB(FeriadoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True