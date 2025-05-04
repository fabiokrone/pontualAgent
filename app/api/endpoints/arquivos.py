# app/api/endpoints/arquivos.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.services.file_processor import ArquivoPontoProcessor
from app.services.ponto_processor import ProcessaPonto

router = APIRouter()

@router.post("/upload/", response_model=Dict[str, Any])
async def upload_arquivo_ponto(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Faz upload de um arquivo de batidas de ponto e processa os registros
    """
    try:
        # Processa o arquivo e salva as batidas no banco
        processor = ArquivoPontoProcessor(db)
        result = await processor.process_file(file)
        
        # Agenda o processamento das batidas em segundo plano
        # para calcular horas extras, faltas, etc.
        background_tasks.add_task(
            ProcessaPonto(db).processar_batidas_importadas
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")