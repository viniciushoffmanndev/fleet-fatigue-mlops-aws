import logging
from fastapi import FastAPI, HTTPException, status
from src.core.schemas import TelemetryEvent

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
async def ingest_telemetry(event: TelemetryEvent):
    """
    Recebe o payload do modelo de Visão Computacional embarcado.
    
    A validação estrutural, topológica e de domínio (EAR, MAR, Limites) 
    é garantida implicitamente pela injeção do schema `TelemetryEvent` (Pydantic V2).
    """
    logger.info(f"Recebendo evento de telemetria do veículo {event.vehicle_id} (Driver: {event.driver_id})")

    # Simulação de regra de negócio / Roteamento Condicional (AWS SNS / Lambda trigger)
    if event.is_critical or event.metrics.eye_aspect_ratio < 0.2:
        logger.warning(
            f"🚨 ALERTA CRÍTICO: Risco de microssono detectado! "
            f"EAR: {event.metrics.eye_aspect_ratio} | Confiança: {event.confidence_score * 100}%"
        )
        # Aqui, em produção real, empurraríamos para uma fila SQS ou dispararíamos o n8n
    else:
        logger.info("Evento padrão registrado com sucesso. EAR dentro da normalidade.")

    return {
        "message": "Evento ingerido e validado com sucesso.",
        "event_id": str(event.event_id),
        "status": "processing_in_background"
    }