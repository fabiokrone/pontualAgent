# app/schemas/usuario.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário único")
    email: EmailStr = Field(..., description="Email válido do usuário")
    nome_completo: str = Field(..., min_length=3, max_length=100, description="Nome completo do usuário")
    perfil: str = Field(..., description="Perfil do usuário: admin, gestor ou usuario")
    secretaria_id: Optional[int] = Field(None, description="ID da secretaria à qual o usuário está vinculado")
    
    @validator('perfil')
    def validate_perfil(cls, v):
        perfis_validos = ["admin", "gestor", "usuario"]
        if v not in perfis_validos:
            raise ValueError(f"Perfil deve ser um dos seguintes: {', '.join(perfis_validos)}")
        return v
    
    @validator('secretaria_id')
    def validate_secretaria_id(cls, v, values):
        perfil = values.get('perfil')
        if perfil == "gestor" and v is None:
            raise ValueError("Usuários com perfil 'gestor' devem estar vinculados a uma secretaria")
        return v

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=8, description="Senha do usuário (mínimo 8 caracteres)")

class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email válido do usuário")
    nome_completo: Optional[str] = Field(None, min_length=3, max_length=100, description="Nome completo do usuário")
    perfil: Optional[str] = Field(None, description="Perfil do usuário: admin, gestor ou usuario")
    secretaria_id: Optional[int] = Field(None, description="ID da secretaria à qual o usuário está vinculado")
    ativo: Optional[bool] = Field(None, description="Status do usuário (ativo/inativo)")
    
    @validator('perfil')
    def validate_perfil(cls, v):
        if v is None:
            return v
        perfis_validos = ["admin", "gestor", "usuario"]
        if v not in perfis_validos:
            raise ValueError(f"Perfil deve ser um dos seguintes: {', '.join(perfis_validos)}")
        return v

class UsuarioInDB(UsuarioBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "joao.silva",
                "email": "joao.silva@exemplo.com",
                "nome_completo": "João da Silva",
                "perfil": "gestor",
                "secretaria_id": 1,
                "ativo": True,
                "created_at": "2025-04-27T15:00:00",
                "updated_at": "2025-04-27T15:00:00"
            }
        }


class UsuarioList(BaseModel):
    items: List[UsuarioInDB]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True  # Corrigido: orm_mode = True -> from_attributes = True


class UsuarioFilter(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    nome_completo: Optional[str] = None
    perfil: Optional[str] = None
    secretaria_id: Optional[int] = None
    ativo: Optional[bool] = None

class CredenciaisLogin(BaseModel):
    email: EmailStr # Alterado de username para email
    password: str

class AlterarSenha(BaseModel):
    senha_atual: str
    nova_senha: str = Field(..., min_length=8, description="Nova senha (mínimo 8 caracteres)")
    
    @validator('nova_senha')
    def validate_nova_senha(cls, v, values):
        if 'senha_atual' in values and v == values['senha_atual']:
            raise ValueError("A nova senha deve ser diferente da senha atual")
        return v

# Schemas para Recuperação de Senha
class PasswordRecoveryRequest(BaseModel):
    email: EmailStr = Field(..., description="E-mail do usuário para recuperação de senha")

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Token de redefinição recebido por e-mail")
    nova_senha: str = Field(..., min_length=8, description="Nova senha (mínimo 8 caracteres)")
    confirmacao_nova_senha: str = Field(..., description="Confirmação da nova senha")

    @validator('confirmacao_nova_senha')
    def passwords_match(cls, v, values):
        if 'nova_senha' in values and v != values['nova_senha']:
            raise ValueError('As senhas não coincidem')
        return v