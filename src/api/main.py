import logging
from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.schemas import TelemetryEvent
from src.db.database import get_db
from src.db.models import TelemetryRecord

# Configuração básica de observabilidade (Logs) para o PMO e DevOps
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instanciando a aplicação com metadados para o Swagger corporativo
app = FastAPI(
    title="ArgusVision - Telemetry Ingestion API",
    description="Edge-to-Cloud API para ingestão e validação de eventos de visão computacional (fadiga em frotas).",
    version="1.0.0"
)

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Endpoint de health check para Load Balancers da AWS e CI/CD."""
    return {"status": "healthy", "service": "telemetry-ingestion-api"}

@app.post(
    "/telemetry/ingest", 
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Ingestion"],
    summary="Recebe e valida eventos de telemetria da borda (caminhão)"
)
async def ingest_telemetry(
    event: TelemetryEvent, 
    db: AsyncSession = Depends(get_db) # <-- INJEÇÃO DE DEPENDÊNCIA AQUI
):
    """
    Recebe o payload do modelo de Visão Computacional embarcado,
    valida via Pydantic e persiste as informações no banco de dados PostgreSQL (AWS/Neon).
    """
    logger.info(f"Recebendo evento de telemetria do veículo {event.vehicle_id} (Driver: {event.driver_id})")

    # 1. De/Para: Transformando o contrato da API (Pydantic) no modelo de Banco (SQLAlchemy)
    novo_registro = TelemetryRecord(
        id=event.event_id,
        timestamp=event.timestamp,
        vehicle_id=event.vehicle_id,
        driver_id=event.driver_id,
        # O model_dump() transforma as métricas aninhadas em um dicionário para a coluna JSONB
        metrics=event.metrics.model_dump(), 
        # Extrai a string da URL, caso ela exista
        frame_s3_url=str(event.frame_s3_url) if event.frame_s3_url else None,
        confidence_score=event.confidence_score,
        is_critical=event.is_critical
    )

    # 2. Persistência de Dados Assíncrona (A ponte com o Neon)
    try:
        db.add(novo_registro) # Adiciona à sessão
        await db.commit()     # Confirma a transação lá na nuvem
        logger.info(f"Evento {event.event_id} gravado com sucesso no PostgreSQL.")
    except Exception as e:
        await db.rollback()   # Em caso de erro, desfaz tudo para não corromper o banco
        logger.error(f"Erro ao gravar no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gravar dados de telemetria.")

    # 3. Simulação de regra de negócio / Roteamento Condicional (AWS SNS / Lambda trigger)
    if event.is_critical or event.metrics.eye_aspect_ratio < 0.2:
        logger.warning(
            f"ALERTA CRÍTICO: Risco de microssono detectado! "
            f"EAR: {event.metrics.eye_aspect_ratio} | Confiança: {event.confidence_score * 100}%"
        )
    else:
        logger.info("Evento padrão processado. EAR dentro da normalidade.")

    return {
        "message": "Evento ingerido, validado e persistido com sucesso.",
        "event_id": str(event.event_id),
        "status": "stored_and_processing"
    }