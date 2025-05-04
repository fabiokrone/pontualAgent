from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from sqlalchemy import text

# Usar a mesma configuração de hash em todos os lugares
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_ou_atualizar_usuarios(db: Session):
    """
    Cria ou atualiza usuários padrão com senhas consistentes
    """
    # Senhas definidas em texto puro
    usuarios = [
        {
            "username": "admin",
            "email": "rhmondai@pontoagent.com.br",
            "nome_completo": "Administrador do Sistema",
            "senha": "admin123#",
            "perfil": "admin",
            "secretaria_id": 1,
            "servidor_id": None
        },
        {
            "username": "fabio",
            "email": "fabiokrone10@gmail.com",
            "nome_completo": "Fábio Krone",
            "senha": "admin123#",
            "perfil": "gestor",
            "secretaria_id": 1,
            # "servidor_id": db.execute(text("SELECT id FROM ponto.servidores WHERE matricula = '4832'")).scalar() # Removido temporariamente para evitar erro na inicialização
            "servidor_id": None # Definido como None inicialmente
        },
    ]
    
    # Para cada usuário na lista
    for user_data in usuarios:
        # Extrair a senha em texto puro
        senha_plain = user_data.pop("senha")
        
        # Gerar hash consistente
        senha_hash = pwd_context.hash(senha_plain)
        
        # Verificar se o usuário já existe
        usuario_existente = db.query(Usuario).filter(Usuario.username == user_data["username"]).first()
        
        if usuario_existente:
            # Atualizar hash da senha
            usuario_existente.senha_hash = senha_hash
            db.add(usuario_existente)
        else:
            # Criar novo usuário
            novo_usuario = Usuario(
                **user_data,
                senha_hash=senha_hash,
                ativo=True
            )
            db.add(novo_usuario)
    
    # Confirmar as alterações
    db.commit()