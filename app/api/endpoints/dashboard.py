from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List

from app.db.session import get_db
from app.models.servidor import Servidor

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Retorna estatísticas para o dashboard
    """
    try:
        # Contagem real de servidores
        total_servidores = db.query(func.count(Servidor.id)).scalar() or 0
        
        # Mantém os outros valores sintéticos
        return {
            "total_servidores": total_servidores,  # Dado real do banco
            "batidas_hoje": 532,                  # Valor fixo 
            "justificativas_pendentes": 18,       # Valor fixo
            "dias_irregulares": 37                # Valor fixo
        }
    except Exception as e:
        print(f"Erro ao obter estatísticas do dashboard: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao obter estatísticas do dashboard."
        )

@router.get("/recent-activities")
async def get_recent_activities():
    """
    Retorna as atividades recentes para o dashboard (dados simulados)
    """
    return [
        {"servidor": "João Silva", "tipo": "Justificativa", "data": "04/05/2025", "status": "Pendente"},
        {"servidor": "Maria Oliveira", "tipo": "Batida", "data": "04/05/2025", "status": "Aprovado"},
        {"servidor": "Carlos Santos", "tipo": "Justificativa", "data": "03/05/2025", "status": "Rejeitado"},
        {"servidor": "Ana Pereira", "tipo": "Batida", "data": "03/05/2025", "status": "Aprovado"},
        {"servidor": "Pedro Souza", "tipo": "Justificativa", "data": "02/05/2025", "status": "Pendente"}
    ]