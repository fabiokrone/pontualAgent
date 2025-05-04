from fastapi import Request
from sqlalchemy.orm import Session

from app.models.log_auditoria import LogAuditoria
from app.core.auth import obter_usuario_atual_opcional

async def registrar_log(
    db: Session,
    request: Request,
    acao: str,
    tabela: str,
    registro_id: int = None,
    detalhes: str = None
):
    """
    Registra uma ação no log de auditoria.
    
    Args:
        db: Sessão do banco de dados
        request: Objeto de requisição do FastAPI
        acao: Tipo de ação (ex: "criar", "atualizar", "excluir")
        tabela: Nome da tabela ou entidade afetada
        registro_id: ID do registro afetado (opcional)
        detalhes: Informações adicionais sobre a ação (opcional)
    """
    # Tenta obter o usuário atual (pode ser None se não autenticado)
    usuario = await obter_usuario_atual_opcional(db, request)
    
    # Obtém o IP do cliente
    ip = request.client.host if request.client else None
    
    # Cria o registro de log
    log = LogAuditoria(
        usuario_id=usuario.id if usuario else None,
        acao=acao,
        tabela=tabela,
        registro_id=registro_id,
        detalhes=detalhes,
        ip=ip
    )
    
    # Salva no banco de dados
    db.add(log)
    db.commit()
    
    return log
