import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional

def generate_uuidv7() -> uuid.UUID:
    """
    Gera um UUIDv7. 
    Nota de Engenharia: Garante ordenação temporal para evitar 'page splits' 
    e degradação de performance nos índices B-Tree do PostgreSQL.
    """
    # Em Python 3.13+, uuid.uuid7() é nativo. Em versões anteriores, 
    # simulamos a abstração ou utilizamos bibliotecas como 'uuid6'.
    try:
        return uuid.uuid7()
    except AttributeError:
        # Fallback seguro caso o ambiente ainda não suporte a função nativa
        import uuid6
        return uuid6.uuid7()

class FatigueMetrics(BaseModel):
    """Métricas brutas extraídas pelo modelo de Visão Computacional embarcado (Edge)."""
    eye_aspect_ratio: float = Field(
        ..., 
        description="EAR: Mede o fechamento dos olhos. Valores < 0.2 indicam risco de microssono.", 
        ge=0.0, le=1.0
    )
    mouth_aspect_ratio: float = Field(
        ..., 
        description="MAR: Mede a abertura da boca. Valores > 0.6 indicam bocejo profundo.", 
        ge=0.0, le=1.0
    )
    head_pitch: float = Field(
        ..., 
        description="Pitch: Ângulo de inclinação da cabeça (graus). Valores negativos altos indicam 'pescoço caído' (distração/sono)."
    )

class TelemetryEvent(BaseModel):
    """
    Contrato de dados corporativo para ingestão de eventos da frota.
    Garante a Governança de Dados antes da inserção no Data Lake (AWS S3) ou RDS.
    """
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    event_id: uuid.UUID = Field(
        default_factory=generate_uuidv7, 
        description="Chave primária ordenada no tempo (UUIDv7)."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="Data e hora exata do evento de telemetria em UTC."
    )
    vehicle_id: str = Field(
        ..., 
        min_length=5, 
        description="Identificador da placa ou chassi do caminhão."
    )
    driver_id: str = Field(
        ..., 
        description="Matrícula/Identificador único do motorista logado via biometria/cartão."
    )
    
    # Aninhamento estratégico: Separa metadados do veículo das métricas do algoritmo
    metrics: FatigueMetrics = Field(
        ..., 
        description="Indicadores de risco extraídos do frame atual."
    )
    
    # Integração nativa desenhada para a arquitetura AWS
    frame_s3_url: Optional[HttpUrl] = Field(
        None, 
        description="Link do bucket AWS S3 contendo a imagem/vídeo para auditoria do ModelOps e PMO."
    )
    confidence_score: float = Field(
        ..., 
        description="Nível de confiança da inferência do modelo na borda.", 
        ge=0.0, le=1.0
    )
    is_critical: bool = Field(
        default=False, 
        description="Flag determinística que aciona fluxos de emergência (AWS Lambda / n8n) para a central."
    )