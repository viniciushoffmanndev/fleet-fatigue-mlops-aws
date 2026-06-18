import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from collections.abc import AsyncGenerator

# Em produção real, isso viria de variáveis de ambiente (.env) ou AWS Secrets Manager
# Estamos usando o prefixo postgresql+asyncpg para invocar o driver assíncrono de alta performance
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:senha_super_segura@localhost:5432/argus_telemetry"
)

# Criando o Motor de Banco de Dados (Engine)
# pool_size e max_overflow: controlamos o limite de conexões simultâneas
engine = create_async_engine(
    DATABASE_URL,
    echo=False, # Mantenha False em prod para não poluir os logs, mude para True para debugar SQL
    pool_size=20,
    max_overflow=10
)

# Fábrica de Sessões (O "caixa" do banco)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency Injection (Injeção de Dependência) para o FastAPI.
    Garante que cada requisição da API ganhe uma sessão isolada de banco de dados,
    e que ela seja fechada corretamente (yield/finally) mesmo se houver um erro,
    evitando o temido "Memory Leak" ou conexões travadas no banco.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()