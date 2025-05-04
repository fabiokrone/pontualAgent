# app/db/session.py
import logging
import time
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da URL do banco de dados
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URI

# Configuração do engine com pool de conexões
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verifica se a conexão está ativa antes de usar
    echo=settings.DB_ECHO_LOG,  # Habilita log de SQL quando em modo debug
)

# Configurar evento para logging de queries
if settings.DB_ECHO_LOG:
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        logger.debug(f"Executando query: {statement}")

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        logger.debug(f"Query executada em {total:.3f}s")

# Criar sessão com retry para falhas temporárias
def get_session_with_retry(retries=3, backoff=0.5):
    """Cria uma sessão com mecanismo de retry para falhas temporárias."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    for attempt in range(retries):
        try:
            db = SessionLocal()
            # Testar a conexão
            db.execute("SELECT 1")
            return db
        except OperationalError as e:
            if attempt < retries - 1:
                wait = backoff * (2 ** attempt)
                logger.warning(f"Falha na conexão com o banco de dados. Tentando novamente em {wait:.2f}s. Erro: {str(e)}")
                time.sleep(wait)
            else:
                logger.error(f"Falha na conexão com o banco de dados após {retries} tentativas: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
            raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependência para obter a sessão do banco de dados
def get_db():
    """Dependência para obter uma sessão do banco de dados para uso nas rotas."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Erro na transação do banco de dados: {str(e)}")
        raise
    finally:
        db.close()

# Função para inicializar o banco de dados
def init_db():
    """Inicializa o banco de dados criando todas as tabelas definidas."""
    try:
        # Criar schema 'ponto' se não existir
        with engine.connect() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS ponto"))
            connection.commit()
            # Criar todas as tabelas
            Base.metadata.create_all(bind=engine)
            logger.info("Banco de dados inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {str(e)}")
        raise
