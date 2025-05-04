# app/api/endpoints/usuarios.py
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.services.auditoria_service import registrar_log

from app.core.auth import obter_usuario_atual, verificar_admin, obter_hash_senha
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioInDB, UsuarioList, UsuarioFilter
)

router = APIRouter()

@router.post("/", response_model=UsuarioInDB, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    usuario: UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: Any = Depends(verificar_admin)  # Apenas administradores podem criar usuários
) -> Any:
    """
    Cria um novo usuário.
    """
    # Verificar se username já existe
    db_usuario = db.query(Usuario).filter(Usuario.username == usuario.username).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já está em uso",
        )
    
    # Verificar se email já existe
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso",
        )
    
    # Criar novo usuário
    db_usuario = Usuario(
        username=usuario.username,
        email=usuario.email,
        nome_completo=usuario.nome_completo,
        senha_hash=obter_hash_senha(usuario.senha),
        ativo=True,
        perfil=usuario.perfil,
        secretaria_id=usuario.secretaria_id
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    # Registrar a ação no log de auditoria
    await registrar_log(
        db=db,
        request=request,
        acao="criar",
        tabela="usuarios",
        registro_id=db_usuario.id,
        detalhes=f"Usuário {db_usuario.username} criado por {usuario_atual.username if hasattr(usuario_atual, 'username') else 'admin'}"
    )
    
    return db_usuario

@router.get("/", response_model=UsuarioList)
async def listar_usuarios(
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: Any = Depends(verificar_admin),  # Apenas administradores podem listar todos os usuários
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    username: str = None,
    email: str = None,
    nome: str = None,
    perfil: str = None,
    secretaria_id: int = None,
    ativo: bool = None
) -> Any:
    """
    Lista todos os usuários com filtros opcionais.
    """
    # Construir query base
    query = db.query(Usuario)
    
    # Aplicar filtros
    if username:
        query = query.filter(Usuario.username.ilike(f"%{username}%"))
    if email:
        query = query.filter(Usuario.email.ilike(f"%{email}%"))
    if nome:
        query = query.filter(Usuario.nome_completo.ilike(f"%{nome}%"))
    if perfil:
        query = query.filter(Usuario.perfil == perfil)
    if secretaria_id:
        query = query.filter(Usuario.secretaria_id == secretaria_id)
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação
    usuarios = query.offset(skip).limit(limit).all()
    
    # Calcular páginas
    pages = (total + limit - 1) // limit if limit > 0 else 1
    
    # Registrar a ação no log de auditoria
    filtros = {
        "username": username,
        "email": email,
        "nome": nome,
        "perfil": perfil,
        "secretaria_id": secretaria_id,
        "ativo": ativo,
        "skip": skip,
        "limit": limit
    }
    
    await registrar_log(
        db=db,
        request=request,
        acao="listar",
        tabela="usuarios",
        registro_id=None,
        detalhes=f"Listagem de usuários por {usuario_atual.username} com filtros: {filtros}"
    )
    
    return {
        "items": usuarios,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": pages
    }

@router.get("/{usuario_id}", response_model=UsuarioInDB)
async def ler_usuario(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioInDB = Depends(obter_usuario_atual)
) -> Any:
    """
    Obtém um usuário pelo ID.
    """
    # Verificar permissão (admin ou o próprio usuário)
    if usuario_atual.perfil != "admin" and usuario_atual.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )
    
    # Buscar usuário
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    # Registrar a ação no log de auditoria
    await registrar_log(
        db=db,
        request=request,
        acao="ler",
        tabela="usuarios",
        registro_id=usuario_id,
        detalhes=f"Usuário {usuario.username} consultado por {usuario_atual.username}"
    )
    
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioInDB)
async def atualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: UsuarioInDB = Depends(obter_usuario_atual)
) -> Any:
    """
    Atualiza um usuário.
    """
    # Verificar permissão (admin ou o próprio usuário)
    if usuario_atual.perfil != "admin" and usuario_atual.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )
    
    # Buscar usuário
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    # Verificar se email já existe (se estiver sendo atualizado)
    if usuario_update.email and usuario_update.email != db_usuario.email:
        email_exists = db.query(Usuario).filter(
            Usuario.email == usuario_update.email,
            Usuario.id != usuario_id
        ).first()
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso",
            )
    
    # Restrições para não-administradores
    if usuario_atual.perfil != "admin":
        # Não-administradores não podem alterar seu próprio perfil ou status
        if usuario_update.perfil is not None or usuario_update.ativo is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para alterar perfil ou status",
            )
    
    # Atualizar campos
    update_data = usuario_update.dict(exclude_unset=True)
    
    # Registrar a ação no log de auditoria com os dados que foram alterados
    await registrar_log(
        db=db,
        request=request,
        acao="atualizar",
        tabela="usuarios",
        registro_id=usuario_id,
        detalhes=f"Usuário {db_usuario.username} atualizado por {usuario_atual.username} - Campos alterados: {list(update_data.keys())}"
    )
    
    for key, value in update_data.items():
        setattr(db_usuario, key, value)
    
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: Any = Depends(verificar_admin)  # Apenas administradores podem deletar usuários
) -> None:
    """
    Deleta um usuário.
    """
    # Buscar usuário
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    # Salvar informações do usuário para o log antes de deletar
    username = usuario.username
    
    # Deletar usuário
    db.delete(usuario)
    db.commit()
    
    # Registrar a ação no log de auditoria
    await registrar_log(
        db=db,
        request=request,
        acao="deletar",
        tabela="usuarios",
        registro_id=usuario_id,
        detalhes=f"Usuário {username} deletado por {usuario_atual.username if hasattr(usuario_atual, 'username') else 'admin'}"
    )
    
    return None