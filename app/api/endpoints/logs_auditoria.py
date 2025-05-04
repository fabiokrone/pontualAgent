from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.log_auditoria import LogAuditoria
from app.schemas.log_auditoria import LogAuditoria as LogAuditoriaSchema
from app.core.auth import obter_usuario_atual, UserInDB

router = APIRouter()

@router.get("/", response_model=List[LogAuditoriaSchema])
async def listar_logs(
    skip: int = 0,
    limit: int = 100,
    usuario_id: Optional[int] = None,
    acao: Optional[str] = None,
    tabela: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    usuario_atual: UserInDB = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """
    Lista os logs de auditoria com filtros opcionais.
    Apenas administradores podem ver todos os logs.
    """
    # Verificar se o usuário tem permissão (apenas admin)
    if usuario_atual.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar logs de auditoria"
        )
    
    # Construir a query base
    query = db.query(LogAuditoria)
    
    # Aplicar filtros se fornecidos
    if usuario_id:
        query = query.filter(LogAuditoria.usuario_id == usuario_id)
    if acao:
        query = query.filter(LogAuditoria.acao == acao)
    if tabela:
        query = query.filter(LogAuditoria.tabela == tabela)
    if data_inicio:
        query = query.filter(LogAuditoria.data_hora >= data_inicio)
    if data_fim:
        query = query.filter(LogAuditoria.data_hora <= data_fim)
    
    # Ordenar por data/hora decrescente (mais recentes primeiro)
    query = query.order_by(LogAuditoria.data_hora.desc())
    
    # Aplicar paginação
    logs = query.offset(skip).limit(limit).all()
    
    return logs
