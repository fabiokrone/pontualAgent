# app/api/endpoints/batidas.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.batida import BatidaOriginal, BatidaProcessada
from app.schemas.batida import (
    BatidaOriginalCreate, BatidaOriginalInDB,
    BatidaProcessadaCreate, BatidaProcessadaUpdate, BatidaProcessadaInDB
)

router = APIRouter()

# Rotas para BatidaOriginal
@router.post("/originais/", response_model=BatidaOriginalInDB, status_code=status.HTTP_201_CREATED)
def create_batida_original(batida: BatidaOriginalCreate, db: Session = Depends(get_db)):
    db_batida = BatidaOriginal(**batida.dict())
    db.add(db_batida)
    db.commit()
    db.refresh(db_batida)
    return db_batida

@router.get("/originais/", response_model=List[BatidaOriginalInDB])
def read_batidas_originais(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    batidas = db.query(BatidaOriginal).offset(skip).limit(limit).all()
    return batidas

@router.get("/originais/{batida_id}", response_model=BatidaOriginalInDB)
def read_batida_original(batida_id: int, db: Session = Depends(get_db)):
    batida = db.query(BatidaOriginal).filter(BatidaOriginal.id == batida_id).first()
    if batida is None:
        raise HTTPException(status_code=404, detail="Batida não encontrada")
    return batida

@router.delete("/originais/{batida_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batida_original(batida_id: int, db: Session = Depends(get_db)):
    batida = db.query(BatidaOriginal).filter(BatidaOriginal.id == batida_id).first()
    if batida is None:
        raise HTTPException(status_code=404, detail="Batida não encontrada")
    
    db.delete(batida)
    db.commit()
    return None

# Rotas para BatidaProcessada
@router.post("/processadas/", response_model=BatidaProcessadaInDB, status_code=status.HTTP_201_CREATED)
def create_batida_processada(batida: BatidaProcessadaCreate, db: Session = Depends(get_db)):
    db_batida = BatidaProcessada(**batida.dict())
    db.add(db_batida)
    db.commit()
    db.refresh(db_batida)
    return db_batida

@router.get("/processadas/", response_model=List[BatidaProcessadaInDB])
def read_batidas_processadas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    batidas = db.query(BatidaProcessada).offset(skip).limit(limit).all()
    return batidas

@router.get("/processadas/{batida_id}", response_model=BatidaProcessadaInDB)
def read_batida_processada(batida_id: int, db: Session = Depends(get_db)):
    batida = db.query(BatidaProcessada).filter(BatidaProcessada.id == batida_id).first()
    if batida is None:
        raise HTTPException(status_code=404, detail="Batida processada não encontrada")
    return batida

@router.put("/processadas/{batida_id}", response_model=BatidaProcessadaInDB)
def update_batida_processada(batida_id: int, batida: BatidaProcessadaUpdate, db: Session = Depends(get_db)):
    db_batida = db.query(BatidaProcessada).filter(BatidaProcessada.id == batida_id).first()
    if db_batida is None:
        raise HTTPException(status_code=404, detail="Batida processada não encontrada")
    
    update_data = batida.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_batida, key, value)
    
    db.commit()
    db.refresh(db_batida)
    return db_batida

@router.delete("/processadas/{batida_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batida_processada(batida_id: int, db: Session = Depends(get_db)):
    batida = db.query(BatidaProcessada).filter(BatidaProcessada.id == batida_id).first()
    if batida is None:
        raise HTTPException(status_code=404, detail="Batida processada não encontrada")
    
    db.delete(batida)
    db.commit()
    return None