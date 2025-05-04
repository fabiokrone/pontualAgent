# app/core/email.py
"""
Módulo responsável pelo envio de emails da aplicação.
Suporta envio via Postmark (API ou SMTP) e salva localmente em desenvolvimento.
"""
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Union

# Manter importação original do PostmarkClient para compatibilidade
from postmarker.core import PostmarkClient
from app.core.config import settings

# Configuração de logging
logger = logging.getLogger(__name__)

def send_email_postmark_api(
    to_email: str, 
    subject: str, 
    html_content: str,
    text_content: Optional[str] = None,
    message_stream: str = "outbound"
) -> bool:
    """
    Envia um e-mail usando a API do Postmark.
    
    Args:
        to_email (str): Endereço de e-mail do destinatário
        subject (str): Assunto do e-mail
        html_content (str): Conteúdo HTML do e-mail
        text_content (str, opcional): Conteúdo texto simples do e-mail
        message_stream (str): Stream de mensagem do Postmark
        
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    # Verificar configurações do Postmark
    if not settings.POSTMARK_SERVER_TOKEN or not settings.EMAILS_FROM_EMAIL:
        logger.warning("Configurações de Postmark (POSTMARK_SERVER_TOKEN ou EMAILS_FROM_EMAIL) não definidas.")
        return False

    try:
        # Inicializar cliente Postmark
        postmark = PostmarkClient(server_token=settings.POSTMARK_SERVER_TOKEN)
        
        # Preparar parâmetros
        email_params = {
            "From": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
            "To": to_email,
            "Subject": subject,
            "HtmlBody": html_content,
            "MessageStream": message_stream
        }
        
        # Adicionar corpo de texto se fornecido
        if text_content:
            email_params["TextBody"] = text_content
        
        # Enviar e-mail
        response = postmark.emails.send(**email_params)
        
        logger.info(f"E-mail enviado para {to_email} via API Postmark. ID da mensagem: {response.get('MessageID')}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail via API Postmark para {to_email}: {e}")
        return False

def send_email_postmark_template(
    to_email: str,
    template_id: Union[str, int],
    template_model: Dict[str, Any],
    message_stream: str = "outbound"
) -> bool:
    """
    Envia um e-mail usando um template do Postmark.
    
    Args:
        to_email (str): Endereço de e-mail do destinatário
        template_id (str ou int): ID ou alias do template no Postmark
        template_model (dict): Modelo de dados para o template
        message_stream (str): Stream de mensagem do Postmark
        
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    # Verificar configurações do Postmark
    if not settings.POSTMARK_SERVER_TOKEN or not settings.EMAILS_FROM_EMAIL:
        logger.warning("Configurações de Postmark (POSTMARK_SERVER_TOKEN ou EMAILS_FROM_EMAIL) não definidas.")
        return False

    try:
        # Inicializar cliente Postmark
        postmark = PostmarkClient(server_token=settings.POSTMARK_SERVER_TOKEN)
        
        # Determinar se estamos usando ID ou alias
        template_param = "TemplateId" if isinstance(template_id, int) else "TemplateAlias"
        
        # Enviar e-mail com template
        response = postmark.emails.send_with_template(
            From=f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
            To=to_email,
            **{template_param: template_id},
            TemplateModel=template_model,
            MessageStream=message_stream
        )
        
        logger.info(f"E-mail com template enviado para {to_email} via API Postmark. ID da mensagem: {response.get('MessageID')}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail com template via API Postmark para {to_email}: {e}")
        return False

def send_email_smtp(
    to_email: str, 
    subject: str, 
    html_content: str, 
    text_content: Optional[str] = None,
    message_stream: str = "pontoagent"
) -> bool:
    """
    Envia um e-mail usando o protocolo SMTP via Postmark.
    
    Args:
        to_email (str): Endereço de e-mail do destinatário
        subject (str): Assunto do e-mail
        html_content (str): Conteúdo HTML do e-mail
        text_content (str, opcional): Conteúdo texto simples do e-mail
        message_stream (str): Stream de mensagem do Postmark
        
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    # Verificar configurações SMTP
    smtp_config = {
        'host': settings.SMTP_HOST or "smtp.postmarkapp.com",
        'port': settings.SMTP_PORT or 587,
        'user': settings.SMTP_USER or settings.POSTMARK_SERVER_TOKEN,
        'password': settings.SMTP_PASSWORD or settings.POSTMARK_SERVER_TOKEN,
    }
    
    if not smtp_config['user'] or not settings.EMAILS_FROM_EMAIL:
        logger.warning("Configurações SMTP (token ou email de origem) não definidas.")
        return False
    
    try:
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Adicionar cabeçalho para Message Stream
        msg['X-PM-Message-Stream'] = message_stream
        
        # Adicionar conteúdo texto simples se fornecido
        if text_content:
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        
        # Adicionar conteúdo HTML (obrigatório)
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # Conectar ao servidor SMTP
        logger.info(f"Conectando ao servidor SMTP: {smtp_config['host']}:{smtp_config['port']}")
        server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
        server.starttls()  # Ativar criptografia TLS
        
        # Autenticar
        logger.info("Autenticando no servidor SMTP")
        server.login(smtp_config['user'], smtp_config['password'])
        
        # Enviar email
        logger.info(f"Enviando email para: {to_email}")
        server.send_message(msg)
        server.quit()
        
        logger.info(f"E-mail enviado com sucesso para {to_email} via SMTP")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail via SMTP para {to_email}: {e}")
        return False

def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None, template_id: Optional[str] = None) -> bool:
    """
    Função principal de envio de e-mail - tenta primeiro SMTP, depois API, depois fallback local
    
    Args:
        to_email (str): Endereço de e-mail do destinatário
        subject (str): Assunto do e-mail
        html_content (str): Conteúdo HTML do e-mail
        text_content (str, opcional): Conteúdo texto simples do e-mail
        
    Returns:
        bool: True se o e-mail foi enviado/salvo com sucesso, False caso contrário
    """
    # Primeira tentativa: SMTP
    if (settings.SMTP_HOST and settings.SMTP_USER) or settings.POSTMARK_SERVER_TOKEN:
        smtp_result = send_email_smtp(to_email, subject, html_content, text_content)
        if smtp_result:
            return True
        logger.warning("Falha no envio via SMTP, tentando API Postmark...")
    
    # Segunda tentativa: API Postmark
    if settings.POSTMARK_SERVER_TOKEN:
        api_result = send_email_postmark_api(to_email, subject, html_content, text_content)
        if api_result:
            return True
        logger.warning("Falha no envio via API Postmark, tentando salvar localmente...")
    
    # Terceira tentativa: salvar localmente apenas em modo debug
    if settings.DEBUG:
        return save_email_locally(to_email, subject, html_content)
    
    return False

def save_email_locally(to_email: str, subject: str, html_content: str) -> bool:
    """
    Salva um e-mail localmente como arquivo HTML para desenvolvimento.
    
    Args:
        to_email (str): Endereço de e-mail do destinatário
        subject (str): Assunto do e-mail
        html_content (str): Conteúdo HTML do e-mail
        
    Returns:
        bool: True se o e-mail foi salvo com sucesso, False caso contrário
    """
    try:
        # Criar diretório de emails se não existir
        email_dir = Path("./email_logs")
        email_dir.mkdir(exist_ok=True)
        
        # Gerar nome de arquivo baseado no timestamp e destinatário
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_email = to_email.replace("@", "_at_").replace(".", "_dot_")
        filename = f"{timestamp}_{safe_email}.html"
        
        # Criar um HTML com todas as informações
        full_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{subject}</title>
            <style>
                .email-info {{ background-color: #f0f0f0; padding: 10px; margin-bottom: 20px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="email-info">
                <p><strong>Para:</strong> {to_email}</p>
                <p><strong>Assunto:</strong> {subject}</p>
                <p><strong>Data:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            <div class="email-content">
                {html_content}
            </div>
        </body>
        </html>
        """
        
        # Salvar no arquivo
        file_path = email_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        logger.info(f"E-mail salvo localmente em: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar e-mail localmente: {e}")
        return False

def send_reset_password_email(to_email: str, username: str, token: str) -> bool:
    """
    Envia um e-mail de redefinição de senha. Tenta usar o template do Postmark primeiro,
    depois cai para versões de fallback.
    
    Args:
        to_email (str): Endereço de e-mail do destinatário
        username (str): Nome de usuário para personalização do e-mail
        token (str): Token de redefinição de senha (não codificado)
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    # Verificar configuração de FRONTEND_URL
    if not settings.FRONTEND_URL:
        frontend_url = "http://localhost:3000"  # URL padrão para desenvolvimento
        logger.warning(f"FRONTEND_URL não configurado. Usando valor padrão: {frontend_url}")
    else:
        frontend_url = settings.FRONTEND_URL
        
    from urllib.parse import quote
    encoded_token = quote(token)
        
    # Adicionar logs para verificar o token recebido (já deve estar codificado)
    logger.debug(f"Token original recebido: {token}")
    logger.debug(f"Comprimento do token original: {len(token)}")
    logger.debug(f"Token codificado para URL: {encoded_token}")
    logger.debug(f"Comprimento do token codificado: {len(encoded_token)}")
    
    # Verificar se contém caracteres especiais
    special_chars = ['+', '/', '_', '=', '%']
    found_special_chars = [char for char in special_chars if char in token]
    if found_special_chars:
        logger.debug(f"O token contém os caracteres especiais: {found_special_chars}")
    
    # Gerar a URL de redefinição (usando o token já codificado)
    reset_url = f"{frontend_url}/redefinir-senha/{encoded_token}"
    logger.info(f"URL de redefinição de senha gerada: {reset_url}")    
    
    
    # Tentar enviar usando template do Postmark primeiro
    template_model = {
        "username": username,
        "reset_url": reset_url,
        "expiry_hours": settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
        "project_name": settings.PROJECT_NAME
    }
    
    if settings.POSTMARK_SERVER_TOKEN:
        try:
            # Tentar enviar com template
            template_result = send_email_postmark_template(
                to_email=to_email,
                template_id="password-reset-1",  # Usar o alias ou ID do seu template
                template_model=template_model
            )
            
            if template_result:
                logger.info(f"E-mail de redefinição de senha enviado com sucesso via template para {to_email}")
                return True
                
            logger.warning("Falha ao enviar via template Postmark, usando fallback...")
        except Exception as e:
            logger.error(f"Erro ao usar template Postmark: {e}")
    
    # Fallback: conteúdo HTML gerado manualmente
    html_content = f"""
    <html>
    <body>
        <p>Olá {username},</p>
        <p>Você solicitou a redefinição da sua senha para o {settings.PROJECT_NAME}.</p>
        <p>Clique no link abaixo para criar uma nova senha:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>Este link expirará em {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hora(s).</p>
        <p>Se você não solicitou esta redefinição, por favor ignore este e-mail.</p>
        <p>Obrigado,</p>
        <p>Equipe {settings.PROJECT_NAME}</p>
    </body>
    </html>
    """
    
    # Conteúdo texto simples
    text_content = f"""
    Olá {username},
    
    Você solicitou a redefinição da sua senha para o {settings.PROJECT_NAME}.
    
    Clique no link abaixo para criar uma nova senha:
    {reset_url}
    
    Este link expirará em {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hora(s).
    
    Se você não solicitou esta redefinição, por favor ignore este e-mail.
    
    Obrigado,
    Equipe {settings.PROJECT_NAME}
    """
    
    # Enviar email usando função principal
    return send_email(
        to_email=to_email,
        subject=f"{settings.PROJECT_NAME} - Redefinição de Senha",
        html_content=html_content,
        text_content=text_content
        
    )

def send_test_email(to_email: str) -> bool:
    """
    Envia um e-mail de teste para verificar a configuração.
    
    Args:
        to_email (str): Endereço de e-mail do destinatário
        
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    html_content = f"""
    <html>
    <body>
        <h2>Teste de Envio de Email</h2>
        <p>Este é um email de teste do sistema {settings.PROJECT_NAME}.</p>
        <p>Se você está vendo esta mensagem, a configuração de email está funcionando corretamente!</p>
        <hr>
        <p><small>Enviado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</small></p>
        <p><small>Configuração SMTP: {"Ativa" if settings.SMTP_HOST and settings.SMTP_USER else "Inativa"}</small></p>
        <p><small>Configuração API Postmark: {"Ativa" if settings.POSTMARK_SERVER_TOKEN else "Inativa"}</small></p>
    </body>
    </html>
    """
    
    text_content = f"""
    Teste de Envio de Email
    
    Este é um email de teste do sistema {settings.PROJECT_NAME}.
    
    Se você está vendo esta mensagem, a configuração de email está funcionando corretamente!
    
    Enviado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    Configuração SMTP: {"Ativa" if settings.SMTP_HOST and settings.SMTP_USER else "Inativa"}
    Configuração API Postmark: {"Ativa" if settings.POSTMARK_SERVER_TOKEN else "Inativa"}
    """
    
    return send_email(
        to_email=to_email,
        subject=f"[TESTE] {settings.PROJECT_NAME} - Teste de Email",
        html_content=html_content,
        text_content=text_content
    )