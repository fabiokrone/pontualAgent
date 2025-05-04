# app/api/endpoints/secretarias.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.secretaria import Secretaria
from app.schemas.secretaria import SecretariaCreate, SecretariaUpdate, SecretariaInDB

router = APIRouter()

@router.post("/", response_model=SecretariaInDB, status_code=status.HTTP_201_CREATED)
def create_secretaria(secretaria: SecretariaCreate, db: Session = Depends(get_db)):
    db_secretaria = Secretaria(**secretaria.dict())
    db.add(db_secretaria)
    db.commit()
    db.refresh(db_secretaria)
    return db_secretaria

@router.get("/", response_model=List[SecretariaInDB])
def read_secretarias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    secretarias = db.query(Secretaria).offset(skip).limit(limit).all()
    return secretarias

@router.get("/{secretaria_id}", response_model=SecretariaInDB)
def read_secretaria(secretaria_id: int, db: Session = Depends(get_db)):
    db_secretaria = db.query(Secretaria).filter(Secretaria.id == secretaria_id).first()
    if db_secretaria is None:
        raise HTTPException(status_code=404, detail="Secretaria não encontrada")
    return db_secretaria

@router.put("/{secretaria_id}", response_model=SecretariaInDB)
def update_secretaria(secretaria_id: int, secretaria: SecretariaUpdate, db: Session = Depends(get_db)):
    db_secretaria = db.query(Secretaria).filter(Secretaria.id == secretaria_id).first()
    if db_secretaria is None:
        raise HTTPException(status_code=404, detail="Secretaria não encontrada")
    
    update_data = secretaria.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_secretaria, key, value)
    
    db.commit()
    db.refresh(db_secretaria)
    return db_secretaria

@router.delete("/{secretaria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_secretaria(secretaria_id: int, db: Session = Depends(get_db)):
    db_secretaria = db.query(Secretaria).filter(Secretaria.id == secretaria_id).first()
    if db_secretaria is None:
        raise HTTPException(status_code=404, detail="Secretaria não encontrada")
    
    db.delete(db_secretaria)
    db.commit()
    return None