# app/services/file_import_service.py
from fastapi import UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
import io
from typing import Dict, Any, List

# Corrigido: nome da classe no singular
from app.models.batida import BatidaOriginal
from app.models.servidor import Servidor  # Também ajustado para singular, assumindo que está assim no modelo

class ImportadorArquivoPonto:
    """Serviço para importação de arquivos de batidas de ponto"""
    
    def __init__(self, db: Session):
        self.db = db

    async def importar_arquivo(self, file: UploadFile) -> Dict[str, Any]:
        """
        Importa um arquivo de batidas de ponto e salva os registros no banco de dados.
        
        Args:
            file: Arquivo enviado pelo usuário
            
        Returns:
            Dicionário com estatísticas da importação
        """
        content = await file.read()
        text_content = content.decode('utf-8')
        linhas = text_content.strip().split('\n')
        
        resultado = {
            "total_registros": len(linhas),
            "registros_importados": 0,
            "registros_ignorados": 0,
            "erros": []
        }
        
        batidas = []
        for linha in linhas:
            try:
                batida = self._processar_linha(linha.strip(), file.filename)
                if batida:
                    batidas.append(batida)
                    resultado["registros_importados"] += 1
                else:
                    resultado["registros_ignorados"] += 1
            except Exception as e:
                resultado["registros_ignorados"] += 1
                resultado["erros"].append(f"Erro ao processar linha: {linha} - {str(e)}")
        
        # Adiciona todas as batidas de uma vez (mais eficiente)
        if batidas:
            self.db.add_all(batidas)
            self.db.commit()
            
        return resultado
    
    def _processar_linha(self, linha: str, nome_arquivo: str) -> BatidaOriginal:
        """
        Processa uma linha do arquivo e cria um objeto BatidaOriginal.
        
        Args:
            linha: Linha do arquivo no formato separado por pipe
            nome_arquivo: Nome do arquivo importado
            
        Returns:
            Objeto BatidaOriginal ou None se a linha for inválida
        """
        # Formato esperado: empresa|matricula|unidade|data|hora|tipo_marcacao|tipo_terminal|terminal
        campos = linha.split('|')
        if len(campos) < 8:
            raise ValueError(f"Número insuficiente de campos: {len(campos)}")
            
        empresa = campos[0]
        matricula = campos[1]
        unidade = campos[2]
        data_str = campos[3]
        hora_str = campos[4]
        tipo_marcacao = campos[5]
        tipo_terminal = campos[6]
        terminal = campos[7]
        
        # Busca o servidor pelo número de matrícula
        servidor = self.db.query(Servidor).filter(
            Servidor.matricula == matricula
        ).first()
        
        if not servidor:
            raise ValueError(f"Servidor não encontrado: {matricula}")
            
        # Converte data e hora
        try:
            data = datetime.strptime(data_str, "%d%m%Y").date()
            hora = datetime.strptime(hora_str, "%H%M").time()
            data_hora = datetime.combine(data, hora)
        except ValueError as e:
            raise ValueError(f"Formato de data/hora inválido: {data_str}/{hora_str}")
            
        # Determina se é entrada ou saída com base no número de batidas do dia
        batidas_do_dia = self.db.query(BatidaOriginal).filter(
            BatidaOriginal.servidor_id == servidor.id,
            BatidaOriginal.data_hora >= datetime.combine(data, datetime.min.time()),
            BatidaOriginal.data_hora <= datetime.combine(data, datetime.max.time())
        ).count()
        
        tipo = 'entrada' if batidas_do_dia % 2 == 0 else 'saida'
        
        # Cria o objeto de batida
        batida = BatidaOriginal(
            servidor_id=servidor.id,
            data_hora=data_hora,
            tipo=tipo,
            dispositivo=f"Relógio {tipo_terminal}",
            localizacao=f"Dispositivo {terminal}",
            arquivo_origem=nome_arquivo,
            importado_em=datetime.now()
        )
        
        return batida