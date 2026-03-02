from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class PropertyAnalysisRequest(BaseModel):
    url: HttpUrl


class TextAnalysisRequest(BaseModel):
    text: str


class ManualAnalysisRequest(BaseModel):
    precio: float
    m2: float
    habitaciones: Optional[int] = None
    planta: Optional[str] = None
    estado: Optional[str] = None
    ubicacion: Optional[str] = None
    coste_reforma: Optional[float] = None  # Si se proporciona, se usa en lugar de calcular
    alquiler_mensual: Optional[float] = None  # Si se proporciona, se usa en lugar de calcular


class ExtractionLog(BaseModel):
    """Log de auditoría de la extracción de datos por IA."""
    found_fields: List[str]  # Campos encontrados directamente en el texto
    missing_fields: List[str]  # Campos que no estaban y han sido estimados
    reasoning: str  # Explicación del razonamiento de la IA
    is_complete: bool  # True si tiene precio y m2 (campos críticos)
    warnings: Optional[List[str]] = None  # Avisos adicionales (ej: descuento OMR > 50%)


class RecalculateRequest(BaseModel):
    """Request para recalcular análisis con nuevo alquiler."""
    analysis_id: Optional[str] = None  # ID del análisis original (opcional)
    alquiler_mensual: float
    precio_compra: float
    m2: float
    gastos_adquisicion: float
    coste_reforma: float
    ubicacion: Optional[str] = None
    extraction_log: Optional[ExtractionLog] = None  # Log de auditoría para incluir en PDF


class PropertyData(BaseModel):
    precio: float
    m2: float
    habitaciones: Optional[int] = None
    planta: Optional[str] = None
    estado: Optional[str] = None
    ubicacion: Optional[str] = None
    url_origen: str
    alquiler_mensual_estimado: Optional[float] = None  # Alquiler estimado por LLM o calculadora


class RentabilityAnalysis(BaseModel):
    precio_compra: float
    gastos_adquisicion: float
    coste_reforma: float
    inversion_total: float
    alquiler_mensual: float
    alquiler_anual: float
    gastos_fijos_anuales: float
    beneficio_neto_anual: float
    rentabilidad_neta: float
    semaforo: str  # "VERDE", "AMARILLO", "ROJO"
    omr: float  # Oferta Máxima Recomendada (precio para 8% rentabilidad)
    property_data: PropertyData


class AnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[RentabilityAnalysis] = None
    pdf_path: Optional[str] = None
    error: Optional[str] = None
    extraction_log: Optional[ExtractionLog] = None  # Log de auditoría de IA

