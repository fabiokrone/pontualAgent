# app/api/endpoints/feriados.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.feriado import Feriado
from app.schemas.feriado import FeriadoCreate, FeriadoUpdate, FeriadoInDB

router = APIRouter()

@router.post("/", response_model=FeriadoInDB, status_code=status.HTTP_201_CREATED)
def create_feriado(feriado: FeriadoCreate, db: Session = Depends(get_db)):
    # Verificar se já existe um feriado nessa data
    existing_feriado = db.query(Feriado).filter(Feriado.data == feriado.data).first()
    if existing_feriado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um feriado cadastrado para a data {feriado.data}"
        )
    
    db_feriado = Feriado(**feriado.dict())
    db.add(db_feriado)
    db.commit()
    db.refresh(db_feriado)
    return db_feriado

@router.get("/", response_model=List[FeriadoInDB])
def read_feriados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feriados = db.query(Feriado).order_by(Feriado.data).offset(skip).limit(limit).all()
    return feriados

@router.get("/{feriado_id}", response_model=FeriadoInDB)
def read_feriado(feriado_id: int, db: Session = Depends(get_db)):
    feriado = db.query(Feriado).filter(Feriado.id == feriado_id).first()
    if feriado is None:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")
    return feriado

@router.put("/{feriado_id}", response_model=FeriadoInDB)
def update_feriado(feriado_id: int, feriado: FeriadoUpdate, db: Session = Depends(get_db)):
    db_feriado = db.query(Feriado).filter(Feriado.id == feriado_id).first()
    if db_feriado is None:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")
    
    update_data = feriado.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_feriado, key, value)
    
    db.commit()
    db.refresh(db_feriado)
    return db_feriado

@router.delete("/{feriado_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feriado(feriado_id: int, db: Session = Depends(get_db)):
    feriado = db.query(Feriado).filter(Feriado.id == feriado_id).first()
    if feriado is None:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")
    
    db.delete(feriado)
    db.commit()
    return None