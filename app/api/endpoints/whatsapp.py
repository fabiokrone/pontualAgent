# app/api/endpoints/whatsapp.py
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.core.auth import obter_usuario_atual, verificar_gestor
from app.db.session import get_db
from app.services.whatsapp_service import WhatsAppService
from app.models.servidor import Servidor
from app.models.justificativa import Justificativa
from app.schemas.usuario import UserInDB

router = APIRouter()

@router.post("/enviar-mensagem", status_code=status.HTTP_200_OK)
async def enviar_mensagem(
    numero_telefone: str = Body(..., embed=True),
    mensagem: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    usuario_atual: UserInDB = Depends(verificar_gestor)  # Apenas gestores podem enviar mensagens
) -> Dict[str, Any]:
    """
    Envia uma mensagem de texto via WhatsApp.
    """
    # Inicializar serviço
    whatsapp_service = WhatsAppService()
    
    # Enviar mensagem
    resultado = whatsapp_service.enviar_mensagem(numero_telefone, mensagem)
    
    return {
        "success": "error" not in resultado,
        "message": "Mensagem enviada com sucesso" if "error" not in resultado else "Erro ao enviar mensagem",
        "details": resultado
    }

@router.post("/notificar-justificativa/{justificativa_id}", status_code=status.HTTP_200_OK)
async def notificar_justificativa(
    justificativa_id: int,
    observacao: str = Body(None, embed=True),
    db: Session = Depends(get_db),
    usuario_atual: UserInDB = Depends(verificar_gestor)  # Apenas gestores podem notificar
) -> Dict[str, Any]:
    """
    Notifica um servidor sobre o status de sua justificativa via WhatsApp.
    """
    # Buscar justificativa
    justificativa = db.query(Justificativa).filter(Justificativa.id == justificativa_id).first()
    if not justificativa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Justificativa não encontrada",
        )
    
    # Buscar servidor
    servidor = db.query(Servidor).filter(Servidor.id == justificativa.servidor_id).first()
    if not servidor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servidor não encontrado",
        )
    
    # Verificar se o gestor tem permissão (mesma secretaria)
    if usuario_atual.perfil != "admin" and usuario_atual.secretaria_id != servidor.secretaria_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente para esta secretaria",
        )
    
    # Verificar se o servidor tem número de telefone cadastrado
    if not servidor.telefone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Servidor não possui número de telefone cadastrado",
        )
    
    # Inicializar serviço
    whatsapp_service = WhatsAppService()
    
    # Formatar data
    data_formatada = justificativa.data.strftime("%d/%m/%Y")
    
    # Enviar notificação
    resultado = whatsapp_service.enviar_notificacao_justificativa(
        servidor.telefone,
        servidor.nome,
        data_formatada,
        justificativa.status,
        observacao
    )
    
    return {
        "success": "error" not in resultado,
        "message": "Notificação enviada com sucesso" if "error" not in resultado else "Erro ao enviar notificação",
        "details": resultado
    }

@router.post("/notificar-batidas-irregulares/{servidor_id}", status_code=status.HTTP_200_OK)
async def notificar_batidas_irregulares(
    servidor_id: int,
    data_inicio: str = Body(..., embed=True),
    data_fim: str = Body(..., embed=True),
    total_irregulares: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    usuario_atual: UserInDB = Depends(verificar_gestor)  # Apenas gestores podem notificar
) -> Dict[str, Any]:
    """
    Notifica um servidor sobre batidas irregulares via WhatsApp.
    """
    # Buscar servidor
    servidor = db.query(Servidor).filter(Servidor.id == servidor_id).first()
    if not servidor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servidor não encontrado",
        )
    
    # Verificar se o gestor tem permissão (mesma secretaria)
    if usuario_atual.perfil != "admin" and usuario_atual.secretaria_id != servidor.secretaria_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente para esta secretaria",
        )
    
    # Verificar se o servidor tem número de telefone cadastrado
    if not servidor.telefone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Servidor não possui número de telefone cadastrado",
        )
    
    # Inicializar serviço
    whatsapp_service = WhatsAppService()
    
    # Enviar notificação
    resultado = whatsapp_service.enviar_notificacao_batidas_irregulares(
        servidor.telefone,
        servidor.nome,
        data_inicio,
        data_fim,
        total_irregulares
    )
    
    return {
        "success": "error" not in resultado,
        "message": "Notificação enviada com sucesso" if "error" not in resultado else "Erro ao enviar notificação",
        "details": resultado
    }

@router.get("/status", status_code=status.HTTP_200_OK)
async def verificar_status(
    db: Session = Depends(get_db),
    usuario_atual: UserInDB = Depends(obter_usuario_atual)
) -> Dict[str, Any]:
    """
    Verifica o status da integração com WhatsApp.
    """
    # Inicializar serviço
    whatsapp_service = WhatsAppService()
    
    return {
        "api_type": whatsapp_service.api_type,
        "modo_simulado": whatsapp_service.modo_simulado,
        "configurado": not whatsapp_service.modo_simulado,
        "api_url": whatsapp_service.api_url if not whatsapp_service.modo_simulado else None
    }
