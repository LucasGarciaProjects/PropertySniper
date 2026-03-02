"""
Extractor de datos de propiedades usando LLM (OpenAI) con optimización de costes.
"""
import os
import json
import re
from typing import Optional, Tuple
from openai import OpenAI
from openai import APITimeoutError
from models import PropertyData, ExtractionLog


class LLMDataExtractor:
    """Extrae datos de propiedades desde texto plano usando LLM con optimización de costes."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el extractor de datos con LLM.
        
        Args:
            api_key: API key de OpenAI. Si no se proporciona, se obtiene de OPENAI_API_KEY
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no configurada. Por favor, configura OPENAI_API_KEY en el archivo .env")
        
        self.client = OpenAI(api_key=api_key, timeout=15.0)  # Timeout de 15 segundos
        self.model = "gpt-4o-mini"  # Modelo más eficiente y barato
        self.max_tokens = 800  # Límite estricto para control de costes
    
    def clean_text(self, text: str) -> str:
        """
        Limpia el texto antes de enviarlo a OpenAI para reducir consumo de tokens.
        
        Args:
            text: Texto crudo del usuario
            
        Returns:
            Texto limpio con espacios normalizados
        """
        # Eliminar espacios múltiples y saltos de línea excesivos
        text = re.sub(r'\s+', ' ', text)
        # Eliminar espacios al inicio y final
        text = text.strip()
        # Limitar longitud máxima para evitar textos excesivamente largos
        # (un anuncio típico no debería superar 5000 caracteres)
        if len(text) > 5000:
            text = text[:5000] + "..."
        return text
    
    def extract_from_text(self, text: str) -> Tuple[PropertyData, ExtractionLog]:
        """
        Extrae datos de una propiedad desde texto plano usando LLM con optimización de costes.
        Incluye log de auditoría para mostrar cómo se extrajeron los datos.
        
        Args:
            text: Texto plano copiado de un portal inmobiliario
            
        Returns:
            Tupla (PropertyData, ExtractionLog) con los datos extraídos y el log de auditoría
            
        Raises:
            ValueError: Si no se pueden extraer los datos o hay un error de validación
            TimeoutError: Si la petición excede el timeout de 15 segundos
            Exception: Si hay un error de conexión o de la API
        """
        # Limpiar texto antes de enviar
        cleaned_text = self.clean_text(text)
        
        # System prompt mejorado con auditoría y estimación de alquiler
        system_prompt = """Eres un extractor de datos JSON con capacidad de auditoría. Tu objetivo es leer el texto de un anuncio inmobiliario y devolver un objeto JSON con dos partes:

1. "data": Objeto con los campos extraídos: precio (int), metros_cuadrados (int), habitaciones (int, opcional), planta (string, opcional), ubicacion (string, opcional), estado (string: "reforma"/"bueno"/"nuevo", opcional), alquiler_mensual (float, opcional).

2. "extraction_log": Objeto con:
   - "found_fields": Lista de strings con los nombres de campos encontrados directamente en el texto (ej: ["precio", "metros_cuadrados", "habitaciones"])
   - "missing_fields": Lista de strings con los campos que NO estaban en el texto y han sido estimados o asumidos (ej: ["estado", "planta", "alquiler_mensual"])
   - "reasoning": String explicando brevemente cómo se determinaron los valores, especialmente para campos estimados. Menciona fragmentos del texto si es relevante.

ESTIMACIÓN DE ALQUILER (si no está en el texto):
- Busca el precio medio de alquiler por m² para la ciudad/barrio detectado en "ubicacion"
- Si es una capital como Madrid o Barcelona, usa un ratio conservador de 18-22 EUR/m²
- Si es otra zona, usa 12-14 EUR/m²
- Multiplica por los metros cuadrados para obtener el "alquiler_mensual" estimado
- Si estimas el alquiler, añádelo a "missing_fields" y explica el razonamiento en "reasoning"

IMPORTANTE:
- Si el texto no contiene datos de un piso, devuelve {"error": "No se detectaron datos inmobiliarios"}
- Los campos precio y metros_cuadrados son OBLIGATORIOS. Si no están, marca el análisis como incompleto.
- Para el estado, si no está claro, estima basándote en palabras clave del texto (reforma, nuevo, bueno, etc.)
- Sé específico en el reasoning, menciona qué partes del texto te ayudaron a extraer cada dato."""
        
        user_prompt = f"Extrae los datos del siguiente anuncio inmobiliario y genera el log de auditoría:\n\n{cleaned_text}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Baja temperatura para respuestas consistentes
                max_tokens=self.max_tokens,  # Límite estricto de tokens
                response_format={"type": "json_object"}  # Forzar respuesta JSON
            )
            
            # Extraer el JSON de la respuesta
            content = response.choices[0].message.content
            if not content:
                raise ValueError("La respuesta del LLM está vacía")
            
            full_response = json.loads(content)
            
            # Verificar si hay error del LLM
            if "error" in full_response:
                raise ValueError(full_response["error"])
            
            # Extraer data y extraction_log
            data = full_response.get("data", {})
            extraction_log_data = full_response.get("extraction_log", {})
            
            # Validar campos requeridos
            precio = data.get("precio")
            metros_cuadrados = data.get("metros_cuadrados")
            
            is_complete = bool(precio and metros_cuadrados)
            
            if not is_complete:
                # Si faltan campos críticos, crear log de error
                missing_critical = []
                if not precio:
                    missing_critical.append("precio")
                if not metros_cuadrados:
                    missing_critical.append("metros_cuadrados")
                
                extraction_log = ExtractionLog(
                    found_fields=extraction_log_data.get("found_fields", []),
                    missing_fields=missing_critical + extraction_log_data.get("missing_fields", []),
                    reasoning=f"Análisis incompleto: faltan campos críticos ({', '.join(missing_critical)}). " + extraction_log_data.get("reasoning", ""),
                    is_complete=False
                )
                
                # Aún así devolvemos los datos parciales para que el frontend pueda mostrar qué falta
                property_data = PropertyData(
                    precio=float(precio) if precio else 0.0,
                    m2=float(metros_cuadrados) if metros_cuadrados else 0.0,
                    habitaciones=int(data["habitaciones"]) if data.get("habitaciones") else None,
                    planta=str(data["planta"]) if data.get("planta") else None,
                    estado=None,
                    ubicacion=data.get("ubicacion") or "No especificada",
                    url_origen="texto_manual"
                )
                
                return property_data, extraction_log
            
            # Normalizar estado
            estado_raw = data.get("estado", "").lower() if data.get("estado") else None
            estado_normalized = None
            if estado_raw:
                if "reformar" in estado_raw or "reforma" in estado_raw:
                    estado_normalized = "a reformar"
                elif "bueno" in estado_raw or "buen" in estado_raw:
                    estado_normalized = "bueno"
                elif "nuevo" in estado_raw or "nueva" in estado_raw:
                    estado_normalized = "nuevo"
                else:
                    estado_normalized = "bueno"  # Por defecto
            
            # Extraer alquiler si está disponible
            alquiler_mensual_estimado = data.get("alquiler_mensual")
            if alquiler_mensual_estimado:
                alquiler_mensual_estimado = float(alquiler_mensual_estimado)
            else:
                alquiler_mensual_estimado = None
            
            # Crear PropertyData
            property_data = PropertyData(
                precio=float(precio),
                m2=float(metros_cuadrados),
                habitaciones=int(data["habitaciones"]) if data.get("habitaciones") else None,
                planta=str(data["planta"]) if data.get("planta") else None,
                estado=estado_normalized,
                ubicacion=data.get("ubicacion") or "No especificada",
                url_origen="texto_manual",
                alquiler_mensual_estimado=alquiler_mensual_estimado
            )
            
            # Crear ExtractionLog
            extraction_log = ExtractionLog(
                found_fields=extraction_log_data.get("found_fields", []),
                missing_fields=extraction_log_data.get("missing_fields", []),
                reasoning=extraction_log_data.get("reasoning", "Datos extraídos del texto del anuncio."),
                is_complete=True,
                warnings=None
            )
            
            return property_data, extraction_log
            
        except APITimeoutError:
            raise TimeoutError("La petición a OpenAI excedió el timeout de 15 segundos. Por favor, intenta de nuevo.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear la respuesta del LLM: {str(e)}. Respuesta recibida: {content[:200] if 'content' in locals() else 'N/A'}")
        except TimeoutError:
            raise  # Re-lanzar TimeoutError
        except Exception as e:
            # Detectar errores de conexión
            error_msg = str(e).lower()
            if "connection" in error_msg or "timeout" in error_msg or "network" in error_msg:
                raise ConnectionError(f"Error de conexión con OpenAI: {str(e)}. Por favor, verifica tu conexión e intenta de nuevo.")
            raise Exception(f"Error al extraer datos con LLM: {str(e)}")

