# app/api/api.py
from fastapi import APIRouter
from app.api.endpoints import batidas, feriados, justificativas, secretarias, servidores, importacao
from app.api.endpoints import auth  # Importação explícita
from app.api.endpoints import logs_auditoria

api_router = APIRouter()

# Primeiro inclua o router de autenticação
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Depois os outros routers
api_router.include_router(batidas.router, prefix="/batidas", tags=["batidas"])
api_router.include_router(feriados.router, prefix="/feriados", tags=["feriados"])
api_router.include_router(justificativas.router, prefix="/justificativas", tags=["justificativas"])
api_router.include_router(secretarias.router, prefix="/secretarias", tags=["secretarias"])
api_router.include_router(servidores.router, prefix="/servidores", tags=["servidores"])
api_router.include_router(importacao.router, prefix="/importacao", tags=["importacao"])
api_router.include_router(logs_auditoria.router, prefix="/logs_auditoria", tags=["logs_auditoria"])


