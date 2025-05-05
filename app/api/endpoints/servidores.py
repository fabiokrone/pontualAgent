# app/api/endpoints/servidores.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.session import get_db
from app.models.servidor import Servidor
from app.schemas.servidor import ServidorCreate, ServidorUpdate, ServidorInDB

router = APIRouter()

@router.post("/", response_model=ServidorInDB, status_code=status.HTTP_201_CREATED)
def create_servidor(servidor: ServidorCreate, db: Session = Depends(get_db)):
    """Cria um novo servidor no sistema."""
    db_servidor = Servidor(**servidor.dict())
    db.add(db_servidor)
    db.commit()
    db.refresh(db_servidor)
    return db_servidor

@router.get("/", response_model=List[Dict[str, Any]])
def read_servidores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos os servidores com tratamento personalizado para
    evitar erros de validação.
    """
    try:
        servidores = db.query(Servidor).offset(skip).limit(limit).all()
        # Converter para dicionário manualmente para evitar validação do Pydantic
        result = []
        for s in servidores:
            servidor_dict = {
                "id": s.id,
                "nome": s.nome,
                "matricula": s.matricula if len(s.matricula) >= 5 else s.matricula.zfill(5),
                "cpf": s.cpf,
                "email": s.email,
                "ativo": s.ativo,
                "secretaria_id": s.secretaria_id,
                "created_at": s.created_at,
                "updated_at": s.updated_at
            }
            result.append(servidor_dict)
        return result
    except Exception as e:
        # Log detalhado do erro para depuração
        print(f"Erro ao buscar servidores: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar servidores: {str(e)}"
        )

@router.get("/{servidor_id}", response_model=Dict[str, Any])
def read_servidor(servidor_id: int, db: Session = Depends(get_db)):
    """Busca um servidor específico pelo ID com tratamento de validação."""
    try:
        db_servidor = db.query(Servidor).filter(Servidor.id == servidor_id).first()
        if db_servidor is None:
            raise HTTPException(status_code=404, detail="Servidor não encontrado")
        
        return {
            "id": db_servidor.id,
            "nome": db_servidor.nome,
            "matricula": db_servidor.matricula if len(db_servidor.matricula) >= 5 else db_servidor.matricula.zfill(5),
            "cpf": db_servidor.cpf,
            "email": db_servidor.email,
            "ativo": db_servidor.ativo,
            "secretaria_id": db_servidor.secretaria_id,
            "created_at": db_servidor.created_at,
            "updated_at": db_servidor.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao buscar servidor {servidor_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar servidor: {str(e)}"
        )

@router.put("/{servidor_id}", response_model=Dict[str, Any])
def update_servidor(servidor_id: int, servidor: ServidorUpdate, db: Session = Depends(get_db)):
    """Atualiza um servidor existente."""
    try:
        db_servidor = db.query(Servidor).filter(Servidor.id == servidor_id).first()
        if db_servidor is None:
            raise HTTPException(status_code=404, detail="Servidor não encontrado")
        
        update_data = servidor.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_servidor, key, value)
        
        db.commit()
        db.refresh(db_servidor)
        
        return {
            "id": db_servidor.id,
            "nome": db_servidor.nome,
            "matricula": db_servidor.matricula if len(db_servidor.matricula) >= 5 else db_servidor.matricula.zfill(5),
            "cpf": db_servidor.cpf,
            "email": db_servidor.email,
            "ativo": db_servidor.ativo,
            "secretaria_id": db_servidor.secretaria_id,
            "created_at": db_servidor.created_at,
            "updated_at": db_servidor.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao atualizar servidor {servidor_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar servidor: {str(e)}"
        )

@router.delete("/{servidor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_servidor(servidor_id: int, db: Session = Depends(get_db)):
    """Remove um servidor do sistema."""
    db_servidor = db.query(Servidor).filter(Servidor.id == servidor_id).first()
    if db_servidor is None:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    
    db.delete(db_servidor)
    db.commit()
    return None