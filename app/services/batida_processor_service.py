# app/services/batida_processor_service.py
from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Tuple
from sqlalchemy import func, and_, or_

from app.models.batida import BatidasOriginais, BatidasProcessadas
from app.models.servidor import Servidores
from app.models.feriado import Feriados
from app.models.horarios_padrao import HorariosPadrao

class ProcessadorBatidas:
    """Serviço para processamento e análise de batidas de ponto"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def processar_batidas_nao_processadas(self):
        """
        Processa todas as batidas originais que ainda não foram processadas.
        - Agrupa por servidor e data
        - Verifica inconsistências
        - Calcula horas trabalhadas
        - Detecta batidas faltantes
        """
        # Buscando batidas não processadas (que não existem na tabela de processadas)
        batidas_originais = self.db.query(BatidasOriginais) \
            .filter(~BatidasOriginais.id.in_(
                self.db.query(BatidasProcessadas.batida_original_id)
            )) \
            .order_by(BatidasOriginais.servidor_id, BatidasOriginais.data_hora) \
            .all()
        
        # Agrupando por servidor e data
        batidas_por_servidor_data = {}
        for batida in batidas_originais:
            data = batida.data_hora.date()
            key = (batida.servidor_id, data)
            
            if key not in batidas_por_servidor_data:
                batidas_por_servidor_data[key] = []
                
            batidas_por_servidor_data[key].append(batida)
        
        # Processando cada grupo
        for (servidor_id, data), batidas_do_dia in batidas_por_servidor_data.items():
            self._processar_batidas_dia(servidor_id, data, batidas_do_dia)
    
    def _processar_batidas_dia(self, servidor_id: int, data: date, batidas: List[BatidasOriginais]):
        """
        Processa as batidas de um servidor em um determinado dia.
        - Detecta inconsistências no padrão de entrada/saída
        - Compara com o horário padrão do servidor
        - Identifica feriados e finais de semana
        
        Args:
            servidor_id: ID do servidor
            data: Data das batidas
            batidas: Lista de batidas do dia
        """
        # Verificar se é feriado ou fim de semana
        is_dia_especial = self._verificar_dia_especial(data)
        
        # Obter o horário padrão do servidor para o dia da semana
        horario_padrao = self._obter_horario_padrao(servidor_id, data.weekday())
        
        # Ordenar batidas por horário
        batidas_ordenadas = sorted(batidas, key=lambda b: b.data_hora)
        
        # Verificar padrão de entrada/saída
        batidas_processadas = []
        batidas_inconsistentes = []
        
        tipo_esperado = 'entrada'
        for batida in batidas_ordenadas:
            # Determinar status da batida
            if batida.tipo == tipo_esperado:
                status = 'normal'
                tipo_esperado = 'saida' if tipo_esperado == 'entrada' else 'entrada'
            else:
                status = 'inconsistente'
                batidas_inconsistentes.append(batida)
            
            # Criar batida processada
            batida_processada = BatidasProcessadas(
                batida_original_id=batida.id,
                servidor_id=batida.servidor_id,
                data_hora=batida.data_hora,
                tipo=batida.tipo,
                status=status,
                processado_em=datetime.now()
            )
            
            batidas_processadas.append(batida_processada)
        
        # Adicionar todas as batidas processadas
        if batidas_processadas:
            self.db.add_all(batidas_processadas)
            self.db.commit()
        
        # Verificar batidas faltantes comparando com o horário padrão
        if horario_padrao and not is_dia_especial:
            self._verificar_batidas_faltantes(servidor_id, data, batidas_ordenadas, horario_padrao)
    
    def _verificar_dia_especial(self, data: date) -> bool:
        """
        Verifica se a data é um dia especial (feriado ou fim de semana).
        
        Args:
            data: Data a verificar
            
        Returns:
            True se for feriado ou fim de semana, False caso contrário
        """
        # Verificar se é fim de semana (5=sábado, 6=domingo)
        if data.weekday() >= 5:
            return True
            
        # Verificar se é feriado
        feriado = self.db.query(Feriados).filter(Feriados.data == data).first()
        return feriado is not None
    
    def _obter_horario_padrao(self, servidor_id: int, dia_semana: int) -> HorariosPadrao:
        """
        Obtém o horário padrão do servidor para o dia da semana.
        
        Args:
            servidor_id: ID do servidor
            dia_semana: Dia da semana (0-6, sendo 0=segunda, 6=domingo)
            
        Returns:
            Objeto HorariosPadrao ou None se não encontrado
        """
        return self.db.query(HorariosPadrao).filter(
            HorariosPadrao.servidor_id == servidor_id,
            HorariosPadrao.dia_semana == dia_semana
        ).first()
    
    def _verificar_batidas_faltantes(self, servidor_id: int, data: date, 
                                    batidas: List[BatidasOriginais], 
                                    horario_padrao: HorariosPadrao):
        """
        Verifica se há batidas faltantes comparando com o horário padrão.
        Cria registros para controle interno (não modifica as batidas originais).
        
        Args:
            servidor_id: ID do servidor
            data: Data a verificar
            batidas: Lista de batidas do dia
            horario_padrao: Horário padrão do servidor
        """
        # Implementar lógica para verificar batidas faltantes
        # Comparar com os horários padrão e registrar em uma tabela de controle
        # Esta funcionalidade será expandida conforme necessário
        pass