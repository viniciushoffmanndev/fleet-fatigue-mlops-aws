from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

# Base declarativa corporativa para mapeamento ORM
Base = declarative_base()

class TelemetryRecord(Base):
    """
    Modelo ORM para a tabela de eventos de telemetria no PostgreSQL (AWS RDS).
    Desenhado para suportar altíssimo volume de escrita em série temporal.
    """
    __tablename__ = "telemetry_events"

    # Chave Primária Otimizada: Recebe o UUIDv7 gerado na API.
    # O index=True é crucial aqui para otimização do B-Tree.
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    
    # Índices para relatórios de Governança e PMO
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    vehicle_id = Column(String(50), index=True, nullable=False)
    driver_id = Column(String(50), index=True, nullable=False)

    # Armazenamento semi-estruturado: JSONB no Postgres permite escalar
    # novas métricas (ex: piscar de olhos, rotação do ombro) sem alterar o schema do banco.
    metrics = Column(JSON, nullable=False)

    # Auditoria de Imagem (Data Lake)
    frame_s3_url = Column(String(255), nullable=True)
    
    # Inferência do Modelo Edge
    confidence_score = Column(Float, nullable=False)
    
    # Flag indexada para acionamento de triggers e queries rápidas de emergência
    is_critical = Column(Boolean, default=False, index=True)