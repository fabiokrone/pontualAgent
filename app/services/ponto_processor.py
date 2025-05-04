# app/services/ponto_processor.py
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Tuple, Optional
import logging

from sqlalchemy.orm import Session
from app.models.batida import BatidaOriginal, BatidaProcessada
from app.models.servidor import Servidor
from app.models.justificativa import Justificativa
from app.schemas.batida import BatidaProcessamentoResult

# Configurar logging
logger = logging.getLogger(__name__)

class HorarioTrabalho:
    """Representa o horário de trabalho de um funcionário."""

    def __init__(self, periodos: List[Tuple[time, time]]):
        """
        Inicializa HorarioTrabalho com uma lista de períodos de trabalho.

        Args:
            periodos (List[Tuple[time, time]]): Lista de tuplas de períodos de trabalho (início, fim).
        """
        self.periodos = periodos

    def calcular_horas_regulares(self) -> timedelta:
        """
        Calcula o total de horas regulares de trabalho.

        Retorna:
            timedelta: Soma total das horas trabalhadas em todos os períodos.
        """
        # Usa uma compreensão de lista para calcular a duração de cada período
        # e soma todos os resultados usando a função sum()
        return sum((self._time_to_timedelta(fim) - self._time_to_timedelta(inicio) 
                    for inicio, fim in self.periodos), 
                   start=timedelta())

    def _time_to_timedelta(self, t: time) -> timedelta:
        """
        Converte um objeto time para timedelta.

        Args:
            t (time): Objeto time para converter.

        Retorna:
            timedelta: Objeto timedelta equivalente.
        """
        return timedelta(hours=t.hour, minutes=t.minute)

class RegistroPonto:
    """Representa um registro de ponto."""

    def __init__(self, data: date, horarios: List[datetime]):
        """
        Inicializa RegistroPonto com uma data e lista de horários de entrada/saída.

        Args:
            data (date): Data do registro.
            horarios (List[datetime]): Lista de horários de entrada/saída.
        """
        self.data = data
        # Ordena os horários para garantir que estejam em ordem cronológica
        self.horarios = sorted(horarios)

class CalculadoraHorasExtras:
    """Calcula as horas extras para um funcionário."""

    def __init__(self, jornada_diaria: timedelta = timedelta(hours=8), intervalo_minimo: int = 0, feriados: List[date] = None):
        """
        Inicializa CalculadoraHorasExtras.

        Args:
            jornada_diaria (timedelta): Jornada diária padrão (default: 8 horas)
            intervalo_minimo (int): Tempo mínimo de intervalo em minutos.
            feriados (List[date]): Lista de datas de feriados.
        """
        self.intervalo_minimo = intervalo_minimo
        self.feriados = feriados or []
        self.jornada_diaria = jornada_diaria

    def calcular_horas_trabalhadas_e_extras(self, registro: RegistroPonto) -> Tuple[timedelta, timedelta, timedelta, bool]:
        """
        Calcula as horas trabalhadas e extras para um registro de ponto.
        
        Args:
            registro (RegistroPonto): Registro de ponto do dia.
            
        Returns:
            Tuple[timedelta, timedelta, timedelta, bool]: 
                - Horas trabalhadas
                - Horas extras
                - Horas faltantes
                - Indicador se é dia especial (feriado/fim de semana)
        """
        horas_trabalhadas = self._calcular_horas_trabalhadas(registro)
        is_dia_especial = self._is_dia_especial(registro.data)
    
        if is_dia_especial:
            return horas_trabalhadas, horas_trabalhadas, timedelta(), True
        
        diferenca = horas_trabalhadas - self.jornada_diaria
        horas_extras = max(diferenca, timedelta())
        horas_faltantes = max(-diferenca, timedelta())
        
        return horas_trabalhadas, horas_extras, horas_faltantes, False

    def _is_dia_especial(self, data: date) -> bool:
        """
        Verifica se a data fornecida é um dia especial (fim de semana ou feriado).

        Args:
            data (date): Data a ser verificada.

        Retorna:
            bool: True se for fim de semana ou feriado, False caso contrário.
        """
        # Considera sábado (5) e domingo (6) como dias especiais
        return data.weekday() >= 5 or data in self.feriados

    def _calcular_horas_trabalhadas(self, registro: RegistroPonto) -> timedelta:
        """
        Calcula o total de horas trabalhadas para um dado registro de ponto.

        Args:
            registro (RegistroPonto): Registro de ponto do dia.

        Retorna:
            timedelta: Total de horas trabalhadas.
        """
        horas_trabalhadas = timedelta()
        
        # Verifica se há um número par de batidas (entrada/saída)
        if len(registro.horarios) % 2 != 0:
            logger.warning(f"Número ímpar de batidas para a data {registro.data}. Ignorando a última batida.")
            horarios = registro.horarios[:-1]  # Remove a última batida
        else:
            horarios = registro.horarios
        
        # Itera sobre os pares de entrada/saída
        for i in range(0, len(horarios), 2):
            if i + 1 < len(horarios):  # Garante que há um par completo
                entrada, saida = horarios[i], horarios[i + 1]
                periodo_trabalhado = saida - entrada
                horas_trabalhadas += periodo_trabalhado

        # Ajusta as horas trabalhadas considerando o intervalo mínimo
        ajuste = self._ajustar_intervalos(registro)
        horas_trabalhadas -= ajuste

        return horas_trabalhadas

    def _ajustar_intervalos(self, registro: RegistroPonto) -> timedelta:
        """
        Ajusta as horas trabalhadas com base no requisito de intervalo mínimo.

        Args:
            registro (RegistroPonto): Registro de ponto do dia.

        Retorna:
            timedelta: Tempo total a ser deduzido das horas trabalhadas.
        """
        if self.intervalo_minimo == 0:
            return timedelta()
    
        ajuste_total = timedelta()
        
        # Verifica se há um número par de batidas
        if len(registro.horarios) % 2 != 0:
            horarios = registro.horarios[:-1]  # Remove a última batida
        else:
            horarios = registro.horarios
            
        # Verifica cada intervalo entre períodos de trabalho
        for i in range(1, len(horarios) // 2):
            intervalo = horarios[i*2] - horarios[i*2 - 1]
            
            # Se o intervalo for menor que o mínimo, calcula a diferença
            if intervalo < timedelta(minutes=self.intervalo_minimo):
                diferenca_intervalo = timedelta(minutes=self.intervalo_minimo) - intervalo
                ajuste_total += diferenca_intervalo

        return ajuste_total

class PontoProcessor:
    """Processa as batidas de ponto e calcula horas trabalhadas, extras e faltantes."""
    
    def __init__(self, db: Session):
        """
        Inicializa o processador de ponto.
        
        Args:
            db (Session): Sessão do banco de dados.
        """
        self.db = db
        self.calculadora = CalculadoraHorasExtras(
            jornada_diaria=timedelta(hours=8),
            intervalo_minimo=60  # 1 hora de intervalo mínimo
        )
        
    def processar_batidas_por_servidor(self, servidor_id: int, periodo_inicio: date, periodo_fim: date) -> BatidaProcessamentoResult:
        """
        Processa todas as batidas de um servidor em um período específico.
        
        Args:
            servidor_id (int): ID do servidor.
            periodo_inicio (date): Data de início do período.
            periodo_fim (date): Data de fim do período.
            
        Returns:
            BatidaProcessamentoResult: Resultado do processamento.
        """
        # Verificar se o servidor existe
        servidor = self.db.query(Servidor).filter(Servidor.id == servidor_id).first()
        if not servidor:
            raise ValueError(f"Servidor com ID {servidor_id} não encontrado")
            
        # Buscar batidas originais do período
        batidas_originais = self.db.query(BatidaOriginal).filter(
            BatidaOriginal.servidor_id == servidor_id,
            BatidaOriginal.data_hora >= datetime.combine(periodo_inicio, time.min),
            BatidaOriginal.data_hora <= datetime.combine(periodo_fim, time.max)
        ).order_by(BatidaOriginal.data_hora).all()
        
        # Buscar feriados do período
        feriados = self._buscar_feriados(periodo_inicio, periodo_fim)
        self.calculadora.feriados = feriados
        
        # Agrupar batidas por data
        batidas_por_data = self._agrupar_batidas_por_data(batidas_originais)
        
        # Processar cada dia
        total_processado = 0
        total_regular = 0
        total_irregular = 0
        total_justificada = 0
        detalhes = []
        
        # Iterar por todas as datas do período
        data_atual = periodo_inicio
        while data_atual <= periodo_fim:
            # Processar o dia
            resultado_dia = self._processar_dia(servidor_id, data_atual, batidas_por_data.get(data_atual, []))
            
            # Atualizar contadores
            total_processado += 1
            if resultado_dia["status"] == "regular":
                total_regular += 1
            elif resultado_dia["status"] == "justificada":
                total_justificada += 1
            else:
                total_irregular += 1
                
            # Adicionar aos detalhes
            detalhes.append(resultado_dia)
            
            # Avançar para o próximo dia
            data_atual += timedelta(days=1)
            
        # Retornar resultado
        return BatidaProcessamentoResult(
            total_processado=total_processado,
            total_regular=total_regular,
            total_irregular=total_irregular,
            total_justificada=total_justificada,
            servidor_id=servidor_id,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            detalhes=detalhes
        )
    
    def _buscar_feriados(self, data_inicio: date, data_fim: date) -> List[date]:
        """
        Busca os feriados no período especificado.
        
        Args:
            data_inicio (date): Data de início do período.
            data_fim (date): Data de fim do período.
            
        Returns:
            List[date]: Lista de datas de feriados.
        """
        # Implementar busca de feriados no banco de dados
        # Por enquanto, retorna uma lista vazia
        return []
    
    def _agrupar_batidas_por_data(self, batidas: List[BatidaOriginal]) -> Dict[date, List[datetime]]:
        """
        Agrupa as batidas por data.
        
        Args:
            batidas (List[BatidaOriginal]): Lista de batidas originais.
            
        Returns:
            Dict[date, List[datetime]]: Dicionário com datas e listas de horários.
        """
        resultado = {}
        for batida in batidas:
            data = batida.data_hora.date()
            if data not in resultado:
                resultado[data] = []
            resultado[data].append(batida.data_hora)
            
        # Ordenar os horários em cada data
        for data in resultado:
            resultado[data] = sorted(resultado[data])
            
        return resultado
    
    def _processar_dia(self, servidor_id: int, data: date, horarios: List[datetime]) -> dict:
        """
        Processa as batidas de um dia específico.
        
        Args:
            servidor_id (int): ID do servidor.
            data (date): Data a ser processada.
            horarios (List[datetime]): Lista de horários de batidas.
            
        Returns:
            dict: Resultado do processamento do dia.
        """
        # Verificar se é fim de semana ou feriado
        is_dia_especial = self.calculadora._is_dia_especial(data)
        
        # Verificar se há justificativa para o dia
        justificativa = self._buscar_justificativa(servidor_id, data)
        
        # Se não há batidas
        if not horarios:
            if is_dia_especial:
                # Fim de semana ou feriado sem batidas é considerado regular
                return {
                    "data": data,
                    "status": "regular",
                    "batidas": [],
                    "horas_trabalhadas": "00:00",
                    "horas_extras": "00:00",
                    "horas_faltantes": "00:00",
                    "justificativa_id": None,
                    "observacao": "Fim de semana ou feriado"
                }
            elif justificativa:
                # Dia com justificativa é considerado justificado
                return {
                    "data": data,
                    "status": "justificada",
                    "batidas": [],
                    "horas_trabalhadas": "00:00",
                    "horas_extras": "00:00",
                    "horas_faltantes": "08:00",
                    "justificativa_id": justificativa.id,
                    "observacao": f"Justificativa: {justificativa.tipo} - {justificativa.descricao}"
                }
            else:
                # Dia útil sem batidas e sem justificativa é considerado irregular
                return {
                    "data": data,
                    "status": "irregular",
                    "batidas": [],
                    "horas_trabalhadas": "00:00",
                    "horas_extras": "00:00",
                    "horas_faltantes": "08:00",
                    "justificativa_id": None,
                    "observacao": "Falta não justificada"
                }
        
        # Criar registro de ponto
        registro = RegistroPonto(data, horarios)
        
        # Calcular horas trabalhadas e extras
        horas_trabalhadas, horas_extras, horas_faltantes, _ = self.calculadora.calcular_horas_trabalhadas_e_extras(registro)
        
        # Determinar status
        if is_dia_especial:
            status = "regular"
            observacao = "Trabalho em fim de semana ou feriado"
        elif justificativa and horas_faltantes > timedelta():
            status = "justificada"
            observacao = f"Justificativa: {justificativa.tipo} - {justificativa.descricao}"
        elif horas_faltantes > timedelta():
            status = "irregular"
            observacao = "Horas faltantes sem justificativa"
        else:
            status = "regular"
            observacao = "Jornada regular"
            
        # Formatar horas
        horas_trabalhadas_str = self._formatar_horas(horas_trabalhadas)
        horas_extras_str = self._formatar_horas(horas_extras)
        horas_faltantes_str = self._formatar_horas(horas_faltantes)
        
        # Formatar batidas
        batidas_str = [h.strftime("%H:%M") for h in horarios]
        
        # Criar e salvar batidas processadas
        self._salvar_batidas_processadas(servidor_id, data, horarios, status, justificativa.id if justificativa else None)
        
        # Retornar resultado
        return {
            "data": data,
            "status": status,
            "batidas": batidas_str,
            "horas_trabalhadas": horas_trabalhadas_str,
            "horas_extras": horas_extras_str,
            "horas_faltantes": horas_faltantes_str,
            "justificativa_id": justificativa.id if justificativa else None,
            "observacao": observacao
        }
    
    def _buscar_justificativa(self, servidor_id: int, data: date) -> Optional[Justificativa]:
        """
        Busca uma justificativa para o servidor na data especificada.
        
        Args:
            servidor_id (int): ID do servidor.
            data (date): Data a ser verificada.
            
        Returns:
            Optional[Justificativa]: Justificativa encontrada ou None.
        """
        return self.db.query(Justificativa).filter(
            Justificativa.servidor_id == servidor_id,
            Justificativa.data == data,
            Justificativa.status == "aprovada"
        ).first()
    
    def _salvar_batidas_processadas(self, servidor_id: int, data: date, horarios: List[datetime], 
                                   status: str, justificativa_id: Optional[int]) -> None:
        """
        Salva as batidas processadas no banco de dados.
        
        Args:
            servidor_id (int): ID do servidor.
            data (date): Data das batidas.
            horarios (List[datetime]): Lista de horários de batidas.
            status (str): Status do processamento.
            justificativa_id (Optional[int]): ID da justificativa, se houver.
        """
        # Verificar se já existem batidas processadas para este servidor e data
        batidas_existentes = self.db.query(BatidaProcessada).filter(
            BatidaProcessada.servidor_id == servidor_id,
            BatidaProcessada.data_hora >= datetime.combine(data, time.min),
            BatidaProcessada.data_hora <= datetime.combine(data, time.max)
        ).all()
        
        # Se existirem, excluir
        if batidas_existentes:
            for batida in batidas_existentes:
                self.db.delete(batida)
            
        # Criar novas batidas processadas
        for i, horario in enumerate(horarios):
            # Determinar o tipo da batida (entrada/saída)
            tipo = "entrada" if i % 2 == 0 else "saida"
            
            # Criar batida processada
            batida_processada = BatidaProcessada(
                servidor_id=servidor_id,
                data_hora=horario,
                tipo=tipo,
                status=status,
                justificativa_id=justificativa_id,
                processado_por="sistema"
            )
            
            # Adicionar ao banco de dados
            self.db.add(batida_processada)
            
        # Commit das alterações
        self.db.commit()
    
    @staticmethod
    def _formatar_horas(td: timedelta) -> str:
        """
        Formata um objeto timedelta para uma string no formato "HH:MM".

        Args:
            td (timedelta): Objeto timedelta a ser formatado.

        Returns:
            str: String formatada no padrão "HH:MM".
        """
        total_segundos = abs(int(td.total_seconds()))
        horas, segundos = divmod(total_segundos, 3600)
        minutos = segundos // 60
        return f"{horas:02d}:{minutos:02d}"
