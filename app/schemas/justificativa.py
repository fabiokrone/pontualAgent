# app/schemas/justificativa.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime, date

class JustificativaBase(BaseModel):
    servidor_id: int = Field(..., description="ID do servidor que solicitou a justificativa")
    data: date = Field(..., description="Data da ocorrência a ser justificada")
    tipo: Literal["atestado", "abono", "falta_justificada", "compensacao", "outro"] = Field(
        ..., description="Tipo da justificativa: atestado, abono, falta_justificada, compensacao ou outro"
    )
    descricao: str = Field(..., min_length=10, max_length=500, description="Descrição detalhada da justificativa")
    anexo_url: Optional[str] = Field(None, description="URL do anexo da justificativa (documento comprobatório)")
    canal_origem: Literal["whatsapp", "email", "sistema", "manual"] = Field(
        ..., description="Canal de origem da justificativa: whatsapp, email, sistema ou manual"
    )

    @validator('data')
    def validate_data(cls, v):
        # Verifica se a data não é futura (permitindo apenas até 7 dias no futuro para casos específicos)
        hoje = date.today()
        max_data_futura = hoje.replace(day=hoje.day + 7)
        if v > max_data_futura:
            raise ValueError("A data da justificativa não pode ser mais de 7 dias no futuro")
        
        # Verifica se a data não é muito antiga (limite de 90 dias)
        min_data = hoje.replace(day=hoje.day - 90)
        if v < min_data:
            raise ValueError("A data da justificativa não pode ser mais de 90 dias no passado")
        
        return v

class JustificativaCreate(JustificativaBase):
    """Schema para criação de uma nova justificativa."""
    status: Literal["pendente", "aprovada", "rejeitada"] = Field(
        "pendente", description="Status da justificativa: pendente, aprovada ou rejeitada"
    )

class JustificativaUpdate(BaseModel):
    """Schema para atualização parcial de uma justificativa."""
    tipo: Optional[Literal["atestado", "abono", "falta_justificada", "compensacao", "outro"]] = Field(
        None, description="Tipo da justificativa: atestado, abono, falta_justificada, compensacao ou outro"
    )
    descricao: Optional[str] = Field(None, min_length=10, max_length=500, description="Descrição detalhada da justificativa")
    anexo_url: Optional[str] = Field(None, description="URL do anexo da justificativa (documento comprobatório)")
    status: Optional[Literal["pendente", "aprovada", "rejeitada"]] = Field(
        None, description="Status da justificativa: pendente, aprovada ou rejeitada"
    )
    aprovado_por: Optional[str] = Field(None, description="Identificação de quem aprovou a justificativa")
    aprovado_em: Optional[datetime] = Field(None, description="Data e hora da aprovação da justificativa")

    @validator('status')
    def validate_status_aprovacao(cls, v, values):
        # Se o status for 'aprovada', deve haver informações de aprovação
        if v == 'aprovada' and not values.get('aprovado_por'):
            raise ValueError("Uma justificativa aprovada deve ter o campo 'aprovado_por' preenchido")
        return v

class JustificativaInDB(JustificativaBase):
    """Schema para representação de uma justificativa armazenada no banco de dados."""
    id: int
    status: Literal["pendente", "aprovada", "rejeitada"]
    criado_em: datetime
    aprovado_por: Optional[str] = None
    aprovado_em: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "servidor_id": 1,
                "data": "2025-04-27",
                "tipo": "atestado",
                "descricao": "Atestado médico por motivo de saúde",
                "anexo_url": "https://storage.exemplo.com/justificativas/atestado_123.pdf",
                "canal_origem": "whatsapp",
                "status": "aprovada",
                "criado_em": "2025-04-27T10:30:00",
                "aprovado_por": "Gestor Silva",
                "aprovado_em": "2025-04-27T14:15:00",
                "created_at": "2025-04-27T10:30:00",
                "updated_at": "2025-04-27T14:15:00"
            }
        }

class JustificativaWithRelationships(JustificativaInDB):
    """Schema para representação de uma justificativa com seus relacionamentos."""
    servidor_nome: Optional[str] = None
    batidas_relacionadas: Optional[List[dict]] = None

class JustificativaList(BaseModel):
    """Schema para representação de uma lista paginada de justificativas."""
    items: List[JustificativaInDB]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        orm_mode = True

class JustificativaFilter(BaseModel):
    """Schema para filtros de busca de justificativas."""
    servidor_id: Optional[int] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    canal_origem: Optional[str] = None

class JustificativaAprovacao(BaseModel):
    """Schema para aprovação ou rejeição de uma justificativa."""
    status: Literal["aprovada", "rejeitada"] = Field(..., description="Novo status da justificativa: aprovada ou rejeitada")
    aprovado_por: str = Field(..., min_length=3, max_length=100, description="Nome ou identificação de quem está aprovando/rejeitando")
    observacao: Optional[str] = Field(None, max_length=500, description="Observação opcional sobre a aprovação/rejeição")
