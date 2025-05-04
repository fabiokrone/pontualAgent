# app/schemas/secretaria.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr, validator
import re

def validate_codigo(codigo: str) -> str:
    # Remove espaços e converte para maiúsculo
    codigo = codigo.strip().upper()
    
    # Verifica se o código tem o formato correto (letras e números, sem caracteres especiais)
    if not re.match(r'^[A-Z0-9]+$', codigo):
        raise ValueError('Código deve conter apenas letras e números')
    
    if len(codigo) < 2 or len(codigo) > 20:
        raise ValueError('Código deve ter entre 2 e 20 caracteres')
    
    return codigo

class SecretariaBase(BaseModel):
    nome: constr(min_length=3, max_length=100)
    codigo: str
    ativo: bool = True

    @validator('codigo')
    def validate_codigo_format(cls, v):
        return validate_codigo(v)

class SecretariaCreate(SecretariaBase):
    pass

class SecretariaUpdate(BaseModel):
    nome: Optional[constr(min_length=3, max_length=100)] = None
    codigo: Optional[str] = None
    ativo: Optional[bool] = None

    @validator('codigo')
    def validate_codigo_format(cls, v):
        if v is not None:
            return validate_codigo(v)
        return v

class SecretariaInDB(SecretariaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True