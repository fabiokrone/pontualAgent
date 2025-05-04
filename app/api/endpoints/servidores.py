# app/api/endpoints/servidores.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.servidor import Servidor
from app.schemas.servidor import ServidorCreate, ServidorUpdate, ServidorInDB

router = APIRouter()

@router.post("/", response_model=ServidorInDB, status_code=status.HTTP_201_CREATED)
def create_servidor(servidor: ServidorCreate, db: Session = Depends(get_db)):
    db_servidor = Servidor(**servidor.dict())
    db.add(db_servidor)
    db.commit()
    db.refresh(db_servidor)
    return db_servidor

@router.get("/", response_model=List[ServidorInDB])
def read_servidores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    servidores = db.query(Servidor).offset(skip).limit(limit).all()
    return servidores

@router.get("/{servidor_id}", response_model=ServidorInDB)
def read_servidor(servidor_id: int, db: Session = Depends(get_db)):
    db_servidor = db.query(Servidor).filter(Servidor.id == servidor_id).first()
    if db_servidor is None:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    return db_servidor

@router.put("/{servidor_id}", response_model=ServidorInDB)
def update_servidor(servidor_id: int, servidor: ServidorUpdate, db: Session = Depends(get_db)):
    db_servidor = db.query(Servidor).filter(Servidor.id == servidor_id).first()
    if db_servidor is None:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    
    update_data = servidor.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_servidor, key, value)
    
    db.commit()
    db.refresh(db_servidor)
    return db_servidor

@router.delete("/{servidor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_servidor(servidor_id: int, db: Session = Depends(get_db)):
    db_servidor = db.query(Servidor).filter(Servidor.id == servidor_id).first()
    if db_servidor is None:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    
    db.delete(db_servidor)
    db.commit()
    return None