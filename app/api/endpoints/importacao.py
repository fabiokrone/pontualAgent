# app/api/endpoints/importacao.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.services.file_import_service import ImportadorArquivoPonto

router = APIRouter()

@router.post("/upload/", response_model=Dict[str, Any])
async def importar_arquivo_ponto(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Importa um arquivo de batidas de ponto.
    
    O arquivo deve estar no formato delimitado por pipe (|) com os campos:
    empresa|matricula|unidade|data|hora|tipo_marcacao|tipo_terminal|terminal
    """
    try:
        # Verifica a extensão do arquivo
        if not file.filename.endswith(('.txt', '.csv', '.dat')):
            raise HTTPException(
                status_code=400, 
                detail="Formato de arquivo inválido. Use arquivos .txt, .csv ou .dat"
            )
            
        # Processa o arquivo
        importador = ImportadorArquivoPonto(db)
        resultado = await importador.importar_arquivo(file)
        
        # Comentado temporariamente até implementarmos o processador de batidas
        # if resultado["registros_importados"] > 0:
        #     background_tasks.add_task(
        #         ProcessadorBatidas(db).processar_batidas_nao_processadas
        #     )
        
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )