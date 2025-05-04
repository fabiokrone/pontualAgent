# app/services/file_processor.py
import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Tuple
import io
from datetime import datetime, date

from app.models.batida import Batida
from app.models.servidor import Servidor

class ArquivoPontoProcessor:
    def __init__(self, db: Session):
        self.db = db

    async def process_file(self, file: UploadFile) -> Dict[str, Any]:
        """Processa o arquivo de batida de ponto enviado e salva no banco de dados"""
        content = await file.read()
        
        # Processa o arquivo como texto para lidar com o formato pipe-delimited
        text_content = content.decode('utf-8')
        lines = text_content.strip().split('\n')
        
        result = {
            "total_registros": len(lines),
            "registros_validos": 0,
            "registros_invalidos": 0,
            "erros": []
        }
        
        for line in lines:
            try:
                fields = line.strip().split('|')
                if len(fields) < 8:
                    result["registros_invalidos"] += 1
                    result["erros"].append(f"Linha com formato inválido: {line}")
                    continue
                
                # Extrai os campos conforme o formato apresentado
                # Formato: 000001|00004439|000001|01082024|0728|1|1|000001
                empresa_id = fields[0]
                matricula = fields[1]
                unidade_id = fields[2]
                data_str = fields[3]
                hora_str = fields[4]
                tipo_marcacao = fields[5]
                tipo_terminal = fields[6]
                terminal_id = fields[7]
                
                # Converte data e hora
                data = datetime.strptime(data_str, "%d%m%Y").date()
                hora = datetime.strptime(hora_str, "%H%M").time()
                
                # Busca o servidor pelo número de matrícula
                servidor = self.db.query(Servidor).filter(
                    Servidor.matricula == matricula
                ).first()
                
                if not servidor:
                    result["registros_invalidos"] += 1
                    result["erros"].append(f"Servidor com matrícula {matricula} não encontrado")
                    continue
                
                # Cria o registro de batida
                batida = Batida(
                    servidor_id=servidor.id,
                    data_original=data,
                    hora_original=hora,
                    data_autorizada=data,  # Inicialmente igual à original
                    hora_autorizada=hora,  # Inicialmente igual à original
                    importado_em=datetime.now(),
                    fonte="arquivo_importado",
                    empresa_id=empresa_id,
                    unidade_id=unidade_id,
                    tipo_marcacao=tipo_marcacao,
                    tipo_terminal=tipo_terminal,
                    terminal_id=terminal_id
                )
                
                self.db.add(batida)
                result["registros_validos"] += 1
                
            except Exception as e:
                result["registros_invalidos"] += 1
                result["erros"].append(str(e))
        
        # Commit dos dados
        self.db.commit()
        
        return result