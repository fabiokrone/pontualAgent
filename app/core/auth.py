# app/core/auth.py
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.usuario import Usuario

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuração de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/token")

# Modelos Pydantic para autenticação
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    nome_completo: str
    ativo: bool
    perfil: str
    secretaria_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Funções de autenticação
def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se a senha plana corresponde ao hash armazenado."""
    logger.debug(f"Verificando senha. Primeiros 3 caracteres: {senha_plana[:3]}***")
    logger.debug(f"Hash da senha do banco: {senha_hash}")
    
    try:
        resultado = pwd_context.verify(senha_plana, senha_hash)
        logger.debug(f"Resultado da verificação de senha: {resultado}")
        return resultado
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {str(e)}")
        return False

def obter_hash_senha(senha_plana: str) -> str:
    """Gera um hash para a senha plana."""
    logger.debug(f"Gerando hash para senha. Primeiros 3 caracteres: {senha_plana[:3]}***")
    hash_senha = pwd_context.hash(senha_plana)
    logger.debug(f"Hash gerado: {hash_senha}")
    return hash_senha

def autenticar_usuario(db: Session, email: str, password: str) -> Optional[Usuario]:
    """Autentica um usuário verificando seu e-mail e senha."""
    logger.debug(f"Tentativa de autenticação para e-mail: {email}")
    logger.debug(f"Senha recebida (primeiros 3 caracteres): {password[:3]}***")
    
    # Buscar usuário pelo e-mail
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        logger.debug(f"Usuário com e-mail '{email}' não encontrado no banco de dados")
        return None
    
    logger.debug(f"Usuário encontrado: {usuario.username}, id: {usuario.id}, ativo: {usuario.ativo}")
    
    if not verificar_senha(password, usuario.senha_hash):
        logger.debug("Verificação de senha falhou")
        return None
    
    logger.debug("Autenticação bem-sucedida")
    return usuario

def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT de acesso."""
    to_encode = data.copy()
    logger.debug(f"Criando token para dados: {to_encode}")
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug(f"Token JWT criado com expiração em: {expire}")
    
    return encoded_jwt

async def obter_usuario_atual(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> UserInDB:
    """Obtém o usuário atual a partir do token JWT."""
    logger.debug("Verificando token de acesso")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            logger.debug("Token não contém 'sub' (subject)")
            raise credentials_exception
        
        token_data = TokenData(username=username, scopes=payload.get("scopes", []))
        logger.debug(f"Token decodificado para usuário: {username}")
    
    except JWTError as e:
        logger.error(f"Erro ao decodificar token JWT: {str(e)}")
        raise credentials_exception
    
    usuario = db.query(Usuario).filter(Usuario.username == token_data.username).first()
    
    if usuario is None:
        logger.debug(f"Usuário {token_data.username} não encontrado no banco de dados")
        raise credentials_exception
    
    if not usuario.ativo:
        logger.debug(f"Usuário {usuario.username} está inativo")
        raise HTTPException(status_code=400, detail="Usuário inativo")
    
    logger.debug(f"Usuário {usuario.username} autenticado com sucesso via token")
    return UserInDB.from_orm(usuario)

# Dependências para verificação de permissões
def verificar_admin(usuario_atual: UserInDB = Depends(obter_usuario_atual)) -> UserInDB:
    """Verifica se o usuário atual tem perfil de administrador."""
    logger.debug(f"Verificando permissão de administrador para usuário {usuario_atual.username}")
    
    if usuario_atual.perfil != "admin":
        logger.debug(f"Acesso negado: {usuario_atual.username} não é administrador")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )
    
    logger.debug(f"Permissão de administrador concedida para {usuario_atual.username}")
    return usuario_atual

def verificar_gestor(usuario_atual: UserInDB = Depends(obter_usuario_atual)) -> UserInDB:
    """Verifica se o usuário atual tem perfil de gestor ou administrador."""
    logger.debug(f"Verificando permissão de gestor para usuário {usuario_atual.username}")
    
    if usuario_atual.perfil not in ["admin", "gestor"]:
        logger.debug(f"Acesso negado: {usuario_atual.username} não é gestor nem administrador")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )
    
    logger.debug(f"Permissão de gestor concedida para {usuario_atual.username}")
    return usuario_atual

def verificar_secretaria_acesso(
    secretaria_id: int,
    usuario_atual: UserInDB = Depends(obter_usuario_atual),
) -> bool:
    """Verifica se o usuário tem acesso à secretaria especificada."""
    logger.debug(f"Verificando acesso à secretaria {secretaria_id} para usuário {usuario_atual.username}")
    
    # Administradores têm acesso a todas as secretarias
    if usuario_atual.perfil == "admin":
        logger.debug(f"Acesso concedido: {usuario_atual.username} é administrador")
        return True
    
    # Gestores só têm acesso à sua própria secretaria
    if usuario_atual.perfil == "gestor" and usuario_atual.secretaria_id == secretaria_id:
        logger.debug(f"Acesso concedido: {usuario_atual.username} é gestor da secretaria {secretaria_id}")
        return True
    
    # Outros usuários não têm acesso
    logger.debug(f"Acesso negado: {usuario_atual.username} não tem permissão para acessar a secretaria {secretaria_id}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Sem permissão para acessar esta secretaria",
    )
    
    
async def obter_usuario_atual_opcional(db: Session, request: Request) -> Optional[UserInDB]:
    """
    Tenta obter o usuário atual a partir do token de autenticação.
    Retorna None se não houver token ou se o token for inválido.
    """
    try:
        # Tenta extrair o token do cabeçalho Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header.replace("Bearer ", "")
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
            
        # Busca o usuário no banco de dados
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        if usuario is None:
            return None
            
        return UserInDB(
            id=usuario.id,
            username=usuario.username,
            email=usuario.email,
            perfil=usuario.perfil,
            secretaria_id=usuario.secretaria_id,
            is_active=usuario.is_active
        )
    except (JWTError, ValidationError):
        return None
    

def verificar_permissao_justificativa(
    justificativa_id: int,
    db: Session = Depends(get_db),
    usuario_atual: UserInDB = Depends(obter_usuario_atual),
) -> bool:
    """Verifica se o usuário tem permissão para aprovar/rejeitar uma justificativa."""
    logger.debug(f"Verificando permissão para justificativa {justificativa_id} do usuário {usuario_atual.username}")
    
    from app.models.justificativa import Justificativa
    from app.models.servidor import Servidor
    
    # Buscar a justificativa
    justificativa = db.query(Justificativa).filter(Justificativa.id == justificativa_id).first()
    if not justificativa:
        logger.debug(f"Justificativa {justificativa_id} não encontrada")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Justificativa não encontrada",
        )
    
    # Buscar o servidor da justificativa
    servidor = db.query(Servidor).filter(Servidor.id == justificativa.servidor_id).first()
    if not servidor:
        logger.debug(f"Servidor da justificativa {justificativa_id} não encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servidor não encontrado",
        )
    
    logger.debug(f"Verificando acesso à secretaria {servidor.secretaria_id} para justificativa {justificativa_id}")
    # Verificar permissão
    return verificar_secretaria_acesso(servidor.secretaria_id, usuario_atual)