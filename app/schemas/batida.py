# app/schemas/batida.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime, date, time

class BatidaOriginalBase(BaseModel):
    servidor_id: int = Field(..., description="ID do servidor que realizou a batida")
    data_hora: datetime = Field(..., description="Data e hora da batida")
    tipo: Literal["entrada", "saida", "intervalo_inicio", "intervalo_fim"] = Field(
        ..., description="Tipo da batida: entrada, saida, intervalo_inicio ou intervalo_fim"
    )
    dispositivo: Optional[str] = Field(None, description="Dispositivo utilizado para registro da batida")
    localizacao: Optional[str] = Field(None, description="Localização onde a batida foi registrada")
    arquivo_origem: Optional[str] = Field(None, description="Nome do arquivo de origem da importação")

    @validator('data_hora')
    def validate_data_hora(cls, v):
        # Verifica se a data não é futura
        if v > datetime.now():
            raise ValueError("A data e hora da batida não pode ser futura")
        return v

class BatidaOriginalCreate(BatidaOriginalBase):
    """Schema para criação de uma nova batida original."""
    pass

class BatidaOriginalInDB(BatidaOriginalBase):
    """Schema para representação de uma batida original armazenada no banco de dados."""
    id: int
    importado_em: datetime
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "servidor_id": 1,
                "data_hora": "2025-04-27T08:00:00",
                "tipo": "entrada",
                "dispositivo": "Relógio Biométrico",
                "localizacao": "Entrada Principal",
                "arquivo_origem": "batidas_abril_2025.csv",
                "importado_em": "2025-04-27T15:00:00",
                "created_at": "2025-04-27T15:00:00"
            }
        }

class BatidaProcessadaBase(BaseModel):
    servidor_id: int = Field(..., description="ID do servidor que realizou a batida")
    data_hora: datetime = Field(..., description="Data e hora da batida")
    tipo: Literal["entrada", "saida", "intervalo_inicio", "intervalo_fim"] = Field(
        ..., description="Tipo da batida: entrada, saida, intervalo_inicio ou intervalo_fim"
    )
    status: Literal["regular", "irregular", "justificada", "pendente"] = Field(
        ..., description="Status da batida: regular, irregular, justificada ou pendente"
    )
    batida_original_id: Optional[int] = Field(None, description="ID da batida original relacionada")
    justificativa_id: Optional[int] = Field(None, description="ID da justificativa relacionada")
    processado_por: Optional[str] = Field(None, description="Identificação de quem processou a batida")

    @validator('status')
    def validate_status_justificativa(cls, v, values):
        # Se o status for 'justificada', deve haver uma justificativa associada
        if v == 'justificada' and not values.get('justificativa_id'):
            raise ValueError("Uma batida com status 'justificada' deve ter uma justificativa associada")
        return v

class BatidaProcessadaCreate(BatidaProcessadaBase):
    """Schema para criação de uma nova batida processada."""
    pass

class BatidaProcessadaUpdate(BaseModel):
    """Schema para atualização parcial de uma batida processada."""
    status: Optional[Literal["regular", "irregular", "justificada", "pendente"]] = Field(
        None, description="Status da batida: regular, irregular, justificada ou pendente"
    )
    justificativa_id: Optional[int] = Field(None, description="ID da justificativa relacionada")
    processado_por: Optional[str] = Field(None, description="Identificação de quem processou a batida")

    @validator('status')
    def validate_status_justificativa(cls, v, values):
        # Se o status for 'justificada', deve haver uma justificativa associada
        if v == 'justificada' and not values.get('justificativa_id'):
            raise ValueError("Uma batida com status 'justificada' deve ter uma justificativa associada")
        return v

class BatidaProcessadaInDB(BatidaProcessadaBase):
    """Schema para representação de uma batida processada armazenada no banco de dados."""
    id: int
    processado_em: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "servidor_id": 1,
                "data_hora": "2025-04-27T08:00:00",
                "tipo": "entrada",
                "status": "regular",
                "batida_original_id": 1,
                "justificativa_id": None,
                "processado_por": "sistema",
                "processado_em": "2025-04-27T15:00:00",
                "created_at": "2025-04-27T15:00:00",
                "updated_at": "2025-04-27T15:00:00"
            }
        }

class BatidaProcessadaWithRelationships(BatidaProcessadaInDB):
    """Schema para representação de uma batida processada com seus relacionamentos."""
    servidor_nome: Optional[str] = None
    justificativa_tipo: Optional[str] = None

class BatidaList(BaseModel):
    """Schema para representação de uma lista paginada de batidas."""
    items: List[BatidaProcessadaInDB]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        orm_mode = True

class BatidaFilter(BaseModel):
    """Schema para filtros de busca de batidas."""
    servidor_id: Optional[int] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    tipo: Optional[str] = None
    status: Optional[str] = None

class BatidaImportItem(BaseModel):
    """Schema para um item de importação de batida."""
    empresa: str
    matricula: str
    local: str
    data: str  # Formato: DDMMYYYY
    hora: str  # Formato: HHMM
    tipo: str
    sentido: str
    terminal: str
    
    @validator('data')
    def validate_data_format(cls, v):
        if not re.match(r'^\d{8}$', v):
            raise ValueError("Data deve estar no formato DDMMYYYY")
        return v
    
    @validator('hora')
    def validate_hora_format(cls, v):
        if not re.match(r'^\d{4}$', v):
            raise ValueError("Hora deve estar no formato HHMM")
        return v

class BatidaImportResult(BaseModel):
    """Schema para resultado de importação de batidas."""
    total_processado: int
    total_sucesso: int
    total_erro: int
    erros: List[str] = []

import re

class BatidaProcessamentoResult(BaseModel):
    """Schema para resultado do processamento de batidas."""
    total_processado: int
    total_regular: int
    total_irregular: int
    total_justificada: int
    servidor_id: int
    periodo_inicio: date
    periodo_fim: date
    detalhes: List[dict] = []
