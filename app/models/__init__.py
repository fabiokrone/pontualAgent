from app.db.session import Base

# Importar todos os modelos aqui para que o Alembic possa detectá-los
from app.models.secretaria import Secretaria
from app.models.servidor import Servidor
from app.models.batida import BatidaOriginal, BatidaProcessada
from app.models.justificativa import Justificativa
from app.models.feriado import Feriado
from app.models.relatorio import Relatorio
# Adicione outras importações conforme necessário