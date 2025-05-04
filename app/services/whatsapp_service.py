# app/services/whatsapp_service.py
import logging
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

class WhatsAppService:
    """Serviço para integração com WhatsApp."""
    
    def __init__(self):
        """Inicializa o serviço de WhatsApp."""
        # Determinar qual API usar com base na configuração
        self.api_type = settings.WHATSAPP_API_TYPE  # "evolution" ou "official"
        self.api_url = settings.WHATSAPP_API_URL
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID  # Necessário apenas para API oficial
        
        if not self.api_url or not self.api_token:
            logger.warning("Configuração de WhatsApp incompleta. Serviço funcionará em modo simulado.")
            self.modo_simulado = True
        else:
            self.modo_simulado = False
    
    def enviar_mensagem(self, numero_telefone: str, mensagem: str) -> Dict[str, Any]:
        """
        Envia uma mensagem de texto para um número de telefone.
        
        Args:
            numero_telefone (str): Número de telefone do destinatário (formato: 5511999999999)
            mensagem (str): Texto da mensagem
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        if self.modo_simulado:
            logger.info(f"[SIMULADO] Enviando mensagem para {numero_telefone}: {mensagem}")
            return {"success": True, "message": "Mensagem simulada enviada com sucesso", "timestamp": datetime.now().isoformat()}
        
        if self.api_type == "evolution":
            return self._enviar_mensagem_evolution(numero_telefone, mensagem)
        else:
            return self._enviar_mensagem_official(numero_telefone, mensagem)
    
    def _enviar_mensagem_evolution(self, numero_telefone: str, mensagem: str) -> Dict[str, Any]:
        """
        Envia mensagem usando a Evolution API.
        
        Args:
            numero_telefone (str): Número de telefone do destinatário
            mensagem (str): Texto da mensagem
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        url = f"{self.api_url}/message/sendText"
        
        # Formatar payload conforme documentação da Evolution API
        payload = {
            "number": numero_telefone,
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
            "textMessage": {
                "text": mensagem
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_token
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar mensagem via Evolution API: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _enviar_mensagem_official(self, numero_telefone: str, mensagem: str) -> Dict[str, Any]:
        """
        Envia mensagem usando a API oficial do WhatsApp.
        
        Args:
            numero_telefone (str): Número de telefone do destinatário
            mensagem (str): Texto da mensagem
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
        
        # Formatar payload conforme documentação da API oficial
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero_telefone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": mensagem
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar mensagem via API oficial: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def enviar_template(self, numero_telefone: str, template_name: str, 
                       language_code: str = "pt_BR", 
                       components: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Envia uma mensagem baseada em template.
        
        Args:
            numero_telefone (str): Número de telefone do destinatário
            template_name (str): Nome do template
            language_code (str): Código do idioma
            components (List[Dict[str, Any]]): Componentes do template
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        if self.modo_simulado:
            logger.info(f"[SIMULADO] Enviando template {template_name} para {numero_telefone}")
            return {"success": True, "message": "Template simulado enviado com sucesso", "timestamp": datetime.now().isoformat()}
        
        if self.api_type == "evolution":
            return self._enviar_template_evolution(numero_telefone, template_name, language_code, components)
        else:
            return self._enviar_template_official(numero_telefone, template_name, language_code, components)
    
    def _enviar_template_evolution(self, numero_telefone: str, template_name: str, 
                                 language_code: str, components: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Envia template usando a Evolution API.
        
        Args:
            numero_telefone (str): Número de telefone do destinatário
            template_name (str): Nome do template
            language_code (str): Código do idioma
            components (List[Dict[str, Any]]): Componentes do template
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        url = f"{self.api_url}/message/sendTemplate"
        
        # Formatar payload conforme documentação da Evolution API
        payload = {
            "number": numero_telefone,
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        # Adicionar componentes se fornecidos
        if components:
            payload["template"]["components"] = components
        
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_token
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar template via Evolution API: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _enviar_template_official(self, numero_telefone: str, template_name: str, 
                                language_code: str, components: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Envia template usando a API oficial do WhatsApp.
        
        Args:
            numero_telefone (str): Número de telefone do destinatário
            template_name (str): Nome do template
            language_code (str): Código do idioma
            components (List[Dict[str, Any]]): Componentes do template
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
        
        # Formatar payload conforme documentação da API oficial
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero_telefone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        # Adicionar componentes se fornecidos
        if components:
            payload["template"]["components"] = components
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar template via API oficial: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def enviar_notificacao_justificativa(self, numero_telefone: str, nome_servidor: str, 
                                        data_justificativa: str, status: str, 
                                        observacao: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia notificação sobre status de justificativa.
        
        Args:
            numero_telefone (str): Número de telefone do destinatário
            nome_servidor (str): Nome do servidor
            data_justificativa (str): Data da justificativa
            status (str): Status da justificativa (aprovada/rejeitada)
            observacao (str, optional): Observação adicional
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        # Construir mensagem
        mensagem = f"Olá! A justificativa de {nome_servidor} para o dia {data_justificativa} foi {status}."
        
        if observacao:
            mensagem += f"\n\nObservação: {observacao}"
        
        mensagem += "\n\nAcesse o sistema para mais detalhes."
        
        # Enviar mensagem
        return self.enviar_mensagem(numero_telefone, mensagem)
    
    def enviar_notificacao_batidas_irregulares(self, numero_telefone: str, nome_servidor: str, 
                                             data_inicio: str, data_fim: str, 
                                             total_irregulares: int) -> Dict[str, Any]:
        """
        Envia notificação sobre batidas irregulares.
        
        Args:
            numero_telefone (str): Número de telefone do destinatário
            nome_servidor (str): Nome do servidor
            data_inicio (str): Data de início do período
            data_fim (str): Data de fim do período
            total_irregulares (int): Total de batidas irregulares
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        # Construir mensagem
        mensagem = f"Olá! Foram detectadas {total_irregulares} ocorrências irregulares no ponto de {nome_servidor} no período de {data_inicio} a {data_fim}."
        
        mensagem += "\n\nAcesse o sistema para verificar e justificar se necessário."
        
        # Enviar mensagem
        return self.enviar_mensagem(numero_telefone, mensagem)
