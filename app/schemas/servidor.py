# app/schemas/servidor.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, validator, Field

import re

def validate_cpf(cpf: str) -> str:
    """
    Valida um CPF brasileiro.
    
    Args:
        cpf: String contendo o CPF a ser validado
        
    Returns:
        CPF formatado apenas com dígitos
        
    Raises:
        ValueError: Se o CPF for inválido
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11:
        raise ValueError('CPF deve conter 11 dígitos')
    
    # Verifica se todos os dígitos são iguais
    if len(set(cpf)) == 1:
        raise ValueError('CPF inválido')
    
    # Validação dos dígitos verificadores
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != int(cpf[i]):
            raise ValueError('CPF inválido')
    
    return cpf

def validate_matricula(matricula: str) -> str:
    """
    Valida uma matrícula de servidor.
    
    Args:
        matricula: String contendo a matrícula a ser validada
        
    Returns:
        Matrícula formatada
        
    Raises:
        ValueError: Se a matrícula for inválida
    """
    # Remove espaços em branco
    matricula = matricula.strip()
    
    # Verifica se a matrícula contém apenas caracteres válidos
    if not re.match(r'^[A-Za-z0-9\-\.]+$', matricula):
        raise ValueError('Matrícula contém caracteres inválidos')
    
    return matricula

class ServidorBase(BaseModel):
    nome: constr(min_length=3, max_length=100) = Field(..., description="Nome completo do servidor")
    matricula: constr(min_length=5, max_length=20) = Field(..., description="Matrícula funcional do servidor")
    cpf: str = Field(..., description="CPF do servidor (apenas números ou com formatação)")
    email: EmailStr = Field(..., description="Email válido do servidor")
    ativo: bool = Field(True, description="Status do servidor (ativo/inativo)")
    secretaria_id: int = Field(..., description="ID da secretaria à qual o servidor está vinculado")

    @validator('cpf')
    def validate_cpf_format(cls, v):
        return validate_cpf(v)
    
    @validator('matricula')
    def validate_matricula_format(cls, v):
        return validate_matricula(v)
    
    @validator('nome')
    def validate_nome(cls, v):
        # Capitaliza o nome corretamente
        return ' '.join(word.capitalize() for word in v.split())

class ServidorCreate(ServidorBase):
    """Schema para criação de um novo servidor."""
    pass

class ServidorUpdate(BaseModel):
    """Schema para atualização parcial de um servidor."""
    nome: Optional[constr(min_length=3, max_length=100)] = Field(None, description="Nome completo do servidor")
    matricula: Optional[constr(min_length=5, max_length=20)] = Field(None, description="Matrícula funcional do servidor")
    cpf: Optional[str] = Field(None, description="CPF do servidor (apenas números ou com formatação)")
    email: Optional[EmailStr] = Field(None, description="Email válido do servidor")
    ativo: Optional[bool] = Field(None, description="Status do servidor (ativo/inativo)")
    secretaria_id: Optional[int] = Field(None, description="ID da secretaria à qual o servidor está vinculado")
    
    @validator('cpf')
    def validate_cpf_format(cls, v):
        if v is None:
            return v
        return validate_cpf(v)
    
    @validator('matricula')
    def validate_matricula_format(cls, v):
        if v is None:
            return v
        return validate_matricula(v)
    
    @validator('nome')
    def validate_nome(cls, v):
        if v is None:
            return v
        # Capitaliza o nome corretamente
        return ' '.join(word.capitalize() for word in v.split())

class ServidorInDB(ServidorBase):
    """Schema para representação de um servidor armazenado no banco de dados."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "nome": "João da Silva",
                "matricula": "12345-6",
                "cpf": "12345678901",
                "email": "joao.silva@exemplo.com",
                "ativo": True,
                "secretaria_id": 1,
                "created_at": "2025-04-27T15:00:00",
                "updated_at": "2025-04-27T15:00:00"
            }
        }

class ServidorWithRelationships(ServidorInDB):
    """Schema para representação de um servidor com seus relacionamentos."""
    secretaria_nome: Optional[str] = None
    total_batidas: Optional[int] = None
    total_justificativas: Optional[int] = None

class ServidorList(BaseModel):
    """Schema para representação de uma lista paginada de servidores."""
    items: List[ServidorInDB]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        orm_mode = True

class ServidorFilter(BaseModel):
    """Schema para filtros de busca de servidores."""
    nome: Optional[str] = None
    matricula: Optional[str] = None
    cpf: Optional[str] = None
    email: Optional[str] = None
    ativo: Optional[bool] = None
    secretaria_id: Optional[int] = None
