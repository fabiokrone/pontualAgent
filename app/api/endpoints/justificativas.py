# app/api/endpoints/justificativas.py
from typing import Any, List
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.auth import obter_usuario_atual, verificar_gestor, verificar_permissao_justificativa
from app.db.session import get_db
from app.models.justificativa import Justificativa
from app.models.servidor import Servidor
from app.schemas.justificativa import (
    JustificativaCreate, JustificativaUpdate, JustificativaInDB, 
    JustificativaList, JustificativaFilter, JustificativaAprovacao
)
from app.schemas.usuario import UsuarioInDB  # Corrigido: UserInDB -> UsuarioInDB

router = APIRouter()

@router.post("/", response_model=JustificativaInDB, status_code=status.HTTP_201_CREATED)
def criar_justificativa(
    justificativa: JustificativaCreate,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioInDB = Depends(obter_usuario_atual)  # Corrigido: UserInDB -> UsuarioInDB
) -> Any:
    """
    Cria uma nova justificativa.
    """
    # Verificar se o servidor existe
    servidor = db.query(Servidor).filter(Servidor.id == justificativa.servidor_id).first()
    if not servidor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servidor não encontrado",
        )
    
    # Verificar permissão (admin, gestor da secretaria ou o próprio servidor)
    if usuario_atual.perfil not in ["admin", "gestor"] and usuario_atual.id != servidor.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )
    
    # Se for gestor, verificar se é da mesma secretaria
    if usuario_atual.perfil == "gestor" and usuario_atual.secretaria_id != servidor.secretaria_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente para esta secretaria",
        )
    
    # Criar justificativa
    db_justificativa = Justificativa(**justificativa.dict())
    db.add(db_justificativa)
    db.commit()
    db.refresh(db_justificativa)
    
    return db_justificativa

@router.get("/", response_model=JustificativaList)
def listar_justificativas(
    db: Session = Depends(get_db),
    usuario_atual: UsuarioInDB = Depends(obter_usuario_atual),  # Corrigido: UserInDB -> UsuarioInDB
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    servidor_id: int = None,
    data_inicio: date = None,
    data_fim: date = None,
    tipo: str = None,
    status: str = None,
    canal_origem: str = None
) -> Any:
    """
    Lista justificativas com filtros opcionais.
    """
    # Construir query base
    query = db.query(Justificativa)
    
    # Aplicar filtros de permissão
    if usuario_atual.perfil == "admin":
        # Administradores podem ver todas as justificativas
        pass
    elif usuario_atual.perfil == "gestor":
        # Gestores só podem ver justificativas de servidores da sua secretaria
        query = query.join(Servidor).filter(Servidor.secretaria_id == usuario_atual.secretaria_id)
    else:
        # Usuários comuns só podem ver suas próprias justificativas
        query = query.filter(Justificativa.servidor_id == usuario_atual.id)
    
    # Aplicar filtros adicionais
    if servidor_id:
        query = query.filter(Justificativa.servidor_id == servidor_id)
    if data_inicio:
        query = query.filter(Justificativa.data >= data_inicio)
    if data_fim:
        query = query.filter(Justificativa.data <= data_fim)
    if tipo:
        query = query.filter(Justificativa.tipo == tipo)
    if status:
        query = query.filter(Justificativa.status == status)
    if canal_origem:
        query = query.filter(Justificativa.canal_origem == canal_origem)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação
    justificativas = query.order_by(Justificativa.data.desc()).offset(skip).limit(limit).all()
    
    # Calcular páginas
    pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return {
        "items": justificativas,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": pages
    }

@router.get("/{justificativa_id}", response_model=JustificativaInDB)
def ler_justificativa(
    justificativa_id: int,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioInDB = Depends(obter_usuario_atual)  # Corrigido: UserInDB -> UsuarioInDB
) -> Any:
    """
    Obtém uma justificativa pelo ID.
    """
    # Buscar justificativa
    justificativa = db.query(Justificativa).filter(Justificativa.id == justificativa_id).first()
    if not justificativa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Justificativa não encontrada",
        )
    
    # Verificar permissão
    servidor = db.query(Servidor).filter(Servidor.id == justificativa.servidor_id).first()
    if not servidor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servidor não encontrado",
        )
    
    # Verificar permissão (admin, gestor da secretaria ou o próprio servidor)
    if usuario_atual.perfil == "admin":
        # Administradores podem ver todas as justificativas
        pass
    elif usuario_atual.perfil == "gestor" and usuario_atual.secretaria_id == servidor.secretaria_id:
        # Gestores podem ver justificativas de servidores da sua secretaria
        pass
    elif usuario_atual.id == servidor.usuario_id:
        # Usuários podem ver suas próprias justificativas
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )
    
    return justificativa

@router.put("/{justificativa_id}", response_model=JustificativaInDB)
def atualizar_justificativa(
    justificativa_id: int,
    justificativa_update: JustificativaUpdate,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioInDB = Depends(obter_usuario_atual)  # Corrigido: UserInDB -> UsuarioInDB
) -> Any:
    """
    Atualiza uma justificativa.
    """
    # Buscar justificativa
    db_justificativa = db.query(Justificativa).filter(Justificativa.id == justificativa_id).first()
    if not db_justificativa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Justificativa não encontrada",
        )
    
    # Verificar permissão
    servidor = db.query(Servidor).filter(Servidor.id == db_justificativa.servidor_id).first()
    if not servidor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servidor não encontrado",
        )
    
    # Verificar permissão (admin, gestor da secretaria ou o próprio servidor)
    if usuario_atual.perfil == "admin":
        # Administradores podem atualizar todas as justificativas
        pass
    elif usuario_atual.perfil == "gestor" and usuario_atual.secretaria_id == servidor.secretaria_id:
        # Gestores podem atualizar justificativas de servidores da sua secretaria
        pass
    elif usuario_atual.id == servidor.usuario_id:
        # Usuários podem atualizar suas próprias justificativas, mas apenas se estiverem pendentes
        if db_justificativa.status != "pendente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não é possível atualizar uma justificativa que já foi aprovada ou rejeitada",
            )
        
        # Usuários não podem alterar o status
        if justificativa_update.status is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuários não podem alterar o status da justificativa",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )
    
    # Atualizar campos
    update_data = justificativa_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_justificativa, key, value)
    
    # Se estiver aprovando a justificativa, adicionar timestamp
    if update_data.get("status") == "aprovada" and db_justificativa.status != "aprovada":
        db_justificativa.aprovado_em = datetime.now()
        if not db_justificativa.aprovado_por and usuario_atual.nome_completo:
            db_justificativa.aprovado_por = usuario_atual.nome_completo
    
    db.commit()
    db.refresh(db_justificativa)
    
    return db_justificativa

@router.post("/{justificativa_id}/aprovar", response_model=JustificativaInDB)
def aprovar_justificativa(
    justificativa_id: int,
    dados: JustificativaAprovacao,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioInDB = Depends(verificar_gestor)  # Corrigido: UserInDB -> UsuarioInDB
) -> Any:
    """
    Aprova ou rejeita uma justificativa.
    """
    # Verificar permissão para esta justificativa
    verificar_permissao_justificativa(justificativa_id, db, usuario_atual)
    
    # Buscar justificativa
    db_justificativa = db.query(Justificativa).filter(Justificativa.id == justificativa_id).first()
    if not db_justificativa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Justificativa não encontrada",
        )
    
    # Verificar se já foi aprovada/rejeitada
    if db_justificativa.status != "pendente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Justificativa já foi {db_justificativa.status}",
        )
    
    # Atualizar status
    db_justificativa.status = dados.status
    db_justificativa.aprovado_por = dados.aprovado_por
    db_justificativa.aprovado_em = datetime.now()
    
    # Adicionar observação se fornecida
    if dados.observacao:
        db_justificativa.descricao += f"\n\nObservação do gestor: {dados.observacao}"
    
    db.commit()
    db.refresh(db_justificativa)
    
    return db_justificativa

@router.delete("/{justificativa_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_justificativa(
    justificativa_id: int,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioInDB = Depends(obter_usuario_atual)  # Corrigido: UserInDB -> UsuarioInDB
) -> None:
    """
    Deleta uma justificativa.
    """
    # Buscar justificativa
    justificativa = db.query(Justificativa).filter(Justificativa.id == justificativa_id).first()
    if not justificativa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Justificativa não encontrada",
        )
    
    # Verificar permissão
    servidor = db.query(Servidor).filter(Servidor.id == justificativa.servidor_id).first()
    if not servidor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servidor não encontrado",
        )
    
    # Verificar permissão (admin, gestor da secretaria ou o próprio servidor)
    if usuario_atual.perfil == "admin":
        # Administradores podem deletar todas as justificativas
        pass
    elif usuario_atual.perfil == "gestor" and usuario_atual.secretaria_id == servidor.secretaria_id:
        # Gestores podem deletar justificativas de servidores da sua secretaria
        pass
    elif usuario_atual.id == servidor.usuario_id:
        # Usuários podem deletar suas próprias justificativas, mas apenas se estiverem pendentes
        if justificativa.status != "pendente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não é possível deletar uma justificativa que já foi aprovada ou rejeitada",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )
    
    # Deletar justificativa
    db.delete(justificativa)
    db.commit()
    
    return None