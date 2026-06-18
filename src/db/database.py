import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from collections.abc import AsyncGenerator

# Carrega as variáveis do arquivo .env para a mamória do sistema
load_dotenv()

# Buscando a URL da Neon
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# Fail-Fast: Se não achar a variável, levanta um erro crítico imediatamente
if not DATABASE_URL:
    raise ValueError("CRÍTICO: a variável de ambiente DATABASE_URL não foi encontrada. Verifique o arquivo .env")

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