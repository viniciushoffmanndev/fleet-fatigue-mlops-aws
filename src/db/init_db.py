import asyncio
import logging
from src.db.database import engine
from src.db.models import Base

# Configurando log para visualizarmos a criação no terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_models():
    """
    Função assíncrona para criar as tabelas no banco de dados.
    Este script deve ser rodado uma única vez na inicialização ou em testes.
    Em produção real, usaríamos ferramentas como Alembic para migrações (migrations).
    """
    try:
        logger.info("Tentando conectar ao banco de dados Neon e criar as tabelas...")
        
        # Conecta no banco e executa a criação de todas as tabelas mapeadas pela "Base"
        async with engine.begin() as conn:
            # Drop_all apaga as tabelas antes de recriar (útil para desenvolvimento)
            # ATENÇÃO: Nunca use drop_all em produção!
            logger.info("Limpando esquema antigo (se houver)...")
            await conn.run_sync(Base.metadata.drop_all)
            
            logger.info("Criando tabela telemetry_events e índices...")
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Sucesso! Tabela criada/atualizada no banco de dados Neon.")
    except Exception as e:
        logger.error(f"Erro ao criar o banco de dados: {e}")
    finally:
        # Fecha o motor de conexão para liberar recursos
        await engine.dispose()

if __name__ == "__main__":
    # Roda a rotina assíncrona
    asyncio.run(init_models())