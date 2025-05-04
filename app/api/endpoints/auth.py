# app/api/endpoints/auth.py
import secrets
import logging
from datetime import timedelta, datetime, timezone
from typing import Any
from app.core.email import send_reset_password_email, send_test_email 

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from fastapi import Query
from sqlalchemy.orm import Session
from urllib.parse import quote_plus

from app.core.auth import (
    Token, UserInDB, autenticar_usuario, criar_token_acesso, 
    obter_usuario_atual, obter_hash_senha, verificar_senha
)
from app.core.config import settings
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import (
    CredenciaisLogin, AlterarSenha, PasswordRecoveryRequest, ResetPasswordRequest
)

# Configuração de logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/test-email", status_code=status.HTTP_200_OK)
async def test_email(email: str = Query(..., description="Email para enviar o teste")):
    """Endpoint para testar o envio de email."""
    
    logger.info(f"Iniciando teste de envio de email para: {email}")
    
    # Tenta enviar o email de teste
    success = send_test_email(email)
    
    if success:
        return {"message": "Email de teste enviado com sucesso!", "status": "success"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Falha ao enviar email de teste. Verifique os logs para mais detalhes."
        )



# Endpoint /token modificado para usar CredenciaisLogin (email)
@router.post("/token", response_model=Token)
async def login_para_token_acesso(
    credenciais: CredenciaisLogin, # Alterado de form_data: OAuth2PasswordRequestForm
    db: Session = Depends(get_db)
) -> Any:
    """
    Endpoint para obtenção de token JWT usando e-mail e senha em JSON.
    (Substitui a necessidade de usar form-data para /token)
    """
    # Autenticar usando e-mail (CORRIGIDO)
    usuario = autenticar_usuario(db, email=credenciais.email, password=credenciais.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos", # Mensagem atualizada
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Manter username como 'sub' no token por enquanto, para compatibilidade com obter_usuario_atual
    token_data = {
        "sub": usuario.username, 
        "perfil": usuario.perfil,
        "secretaria_id": usuario.secretaria_id
    }
    
    access_token = criar_token_acesso(
        data=token_data, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint /login atualizado para usar email na autenticação
@router.post("/login", response_model=Token)
async def login(
    credenciais: CredenciaisLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Endpoint para login com credenciais (e-mail e senha) em JSON.
    """
    # Autenticar usando e-mail (CORRIGIDO)
    usuario = autenticar_usuario(db, email=credenciais.email, password=credenciais.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos", # Mensagem atualizada
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Manter username como 'sub' no token por enquanto
    token_data = {
        "sub": usuario.username,
        "perfil": usuario.perfil,
        "secretaria_id": usuario.secretaria_id
    }
    
    access_token = criar_token_acesso(
        data=token_data, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserInDB)
async def ler_usuarios_me(
    usuario_atual: UserInDB = Depends(obter_usuario_atual)
) -> Any:
    """
    Retorna informações do usuário atual (baseado no token JWT).
    """
    # Nota: obter_usuario_atual ainda busca pelo username contido no 'sub' do token.
    return usuario_atual

@router.post("/alterar-senha", status_code=status.HTTP_200_OK)
async def alterar_senha(
    dados: AlterarSenha,
    usuario_atual: UserInDB = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
) -> Any:
    """
    Altera a senha do usuário atual.
    """
    # Buscar usuário no banco pelo username (vindo do token via obter_usuario_atual)
    usuario = db.query(Usuario).filter(Usuario.username == usuario_atual.username).first()
    if not usuario:
        # Esta situação é improvável se o token for válido
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    # Verificar senha atual
    if not verificar_senha(dados.senha_atual, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )
    
    # Atualizar senha
    usuario.senha_hash = obter_hash_senha(dados.nova_senha)
    db.commit()
    
    return {"message": "Senha alterada com sucesso"}

# --- ENDPOINTS PARA RECUPERAÇÃO DE SENHA (já usam e-mail) ---
# Modificação em solicitar_recuperacao_senha
@router.post("/password-recovery", status_code=status.HTTP_200_OK)
async def solicitar_recuperacao_senha(
    request_data: PasswordRecoveryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Solicita a recuperação de senha para um e-mail.
    Gera um token, salva no banco e envia um e-mail com o link de redefinição.
    """
    logger.info(f"Solicitação de recuperação de senha para o e-mail: {request_data.email}")
    usuario = db.query(Usuario).filter(Usuario.email == request_data.email).first()

    if usuario:
        logger.info(f"Usuário encontrado: {usuario.username}, ID: {usuario.id}")
        
        # Gerar token seguro - usar secrets.token_urlsafe para gerar tokens URL-safe
        token = secrets.token_urlsafe(32)
        
        # Log detalhado do token gerado
        print(f"DEBUG - Token gerado: '{token}'")
        print(f"DEBUG - Comprimento do token: {len(token)}")
        logger.debug(f"Token gerado: {token}")
        logger.debug(f"Comprimento do token: {len(token)}")
        
        # Verificar se contém caracteres especiais
        special_chars = ['+', '/', '_', '=', '-']
        found_special_chars = [char for char in special_chars if char in token]
        if found_special_chars:
            print(f"DEBUG - O token contém caracteres especiais: {found_special_chars}")
            logger.debug(f"O token contém os caracteres especiais: {found_special_chars}")
        
        # Calcular data de expiração (UTC)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        
        # Salvar token no banco
        usuario.reset_token = token
        usuario.reset_token_expires_at = expires_at
        db.commit()
        
        # Verificar como o token foi salvo
        usuario_atualizado = db.query(Usuario).filter(Usuario.id == usuario.id).first()
        print(f"DEBUG - Token salvo no banco: '{usuario_atualizado.reset_token}'")
        logger.debug(f"Token salvo no banco: '{usuario_atualizado.reset_token}'")
        
        # Enviar e-mail em background
        background_tasks.add_task(
            send_reset_password_email,
            to_email=usuario.email,
            username=usuario.username,
            token=token  # Token original, não codificado
        )
        logger.info(f"Tarefa de envio de e-mail adicionada para {usuario.email}")
    else:
        logger.info(f"Nenhum usuário encontrado com o e-mail: {request_data.email}. Nenhuma ação será tomada, mas retornando sucesso.")

    # Retorna uma mensagem genérica para não revelar se o e-mail existe ou não
    return {"message": "Se um usuário com este e-mail existir, um link para redefinição de senha será enviado."}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request_data: PasswordRecoveryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """Alias para solicitar_recuperacao_senha"""
    return await solicitar_recuperacao_senha(request_data, background_tasks, db)



# Modificação em redefinir_senha
@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def redefinir_senha(
    request_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Redefine a senha do usuário usando o token recebido.
    """
    # Validar token
    if not request_data.token:
        logger.warning("Token não fornecido na requisição")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado."
        )
    
    # Limpar e validar o token
    token_recebido = request_data.token.strip()
    logger.info(f"Tentativa de redefinição de senha com token de {len(token_recebido)} caracteres")
    
    # Buscar usuário pelo token
    usuario = db.query(Usuario).filter(Usuario.reset_token == token_recebido).first()

    if not usuario:
        logger.warning(f"Token não encontrado no banco de dados")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado."
        )
        
    # Verificar expiração do token
    agora = datetime.now(timezone.utc)
    
    # Verificação segura da data de expiração com tratamento para diferentes tipos de fuso horário
    if not usuario.reset_token_expires_at:
        token_expirado = True
    else:
        # Verificar se reset_token_expires_at já tem fuso horário
        if usuario.reset_token_expires_at.tzinfo is None:
            # Se não tiver, assumir UTC para comparação segura
            token_expires_aware = usuario.reset_token_expires_at.replace(tzinfo=timezone.utc)
        else:
            # Se já tiver fuso horário, usar como está
            token_expires_aware = usuario.reset_token_expires_at
            
        token_expirado = token_expires_aware < agora
    
    if token_expirado:
        logger.warning(f"Token expirado para usuário {usuario.username}")
        
        # Limpar token expirado
        usuario.reset_token = None
        usuario.reset_token_expires_at = None
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado."
        )

    # Validar a nova senha
    if request_data.nova_senha != request_data.confirmacao_nova_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha e a confirmação não coincidem."
        )
    
    if len(request_data.nova_senha) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ter pelo menos 8 caracteres."
        )

    # Redefinir a senha
    try:
        # Atualizar senha
        usuario.senha_hash = obter_hash_senha(request_data.nova_senha)
        usuario.reset_token = None
        usuario.reset_token_expires_at = None
        
        db.commit()
        logger.info(f"Senha redefinida com sucesso para o usuário {usuario.username}")
        
        return {"message": "Senha redefinida com sucesso! Você já pode fazer login com sua nova senha."}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao redefinir senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao redefinir sua senha. Tente novamente mais tarde."
        )