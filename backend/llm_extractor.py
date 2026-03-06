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
            raise ValueError("OPENAI_API_KEY not configured. Please configure OPENAI_API_KEY in the .env file")
        
        self.client = OpenAI(api_key=api_key, timeout=15.0)  # Timeout of 15 seconds
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
        system_prompt = """You are a JSON data extractor with audit capabilities. Your goal is to read the text of a real estate listing and return a JSON object with two parts:

1. "data": Object with the extracted fields: precio (int), metros_cuadrados (int), habitaciones (int, optional), planta (string, optional), ubicacion (string, optional), estado (string: "reforma"/"bueno"/"nuevo", optional), alquiler_mensual (float, optional).

2. "extraction_log": Object with:
   - "found_fields": List of strings with the names of fields found directly in the text (e.g., ["precio", "metros_cuadrados", "habitaciones"])
   - "missing_fields": List of strings with the fields that were NOT in the text and have been estimated or assumed (e.g., ["estado", "planta", "alquiler_mensual"])
   - "reasoning": String briefly explaining how values were determined, especially for estimated fields. Mention text fragments if relevant. MUST BE IN ENGLISH.

RENT ESTIMATION (if not in text):
- Look for the average rental price per m² for the city/neighborhood detected in "ubicacion"
- If it is a capital like Madrid or Barcelona, use a conservative ratio of 18-22 EUR/m²
- If it is another area, use 12-14 EUR/m²
- Multiply by square meters to get the estimated "alquiler_mensual"
- If you estimate the rent, add it to "missing_fields" and explain the reasoning in "reasoning"

IMPORTANT:
- If the text does not contain property data, return {"error": "No property data detected"}
- The fields precio and metros_cuadrados are MANDATORY. If they are missing, mark the analysis as incomplete.
- For the state (estado), if it is not clear, estimate based on keywords in the text (reforma, nuevo, bueno, etc.)
- Be specific in the reasoning, mention which parts of the text helped you extract each piece of data.
- The "reasoning" MUST be in English."""
        
        user_prompt = f"Extract the data from the following real estate listing and generate the audit log:\n\n{cleaned_text}"

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
            
            # Extract the JSON from the response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM response is empty")
            
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
                    reasoning=f"Incomplete analysis: critical fields missing ({', '.join(missing_critical)}). " + extraction_log_data.get("reasoning", ""),
                    is_complete=False
                )
                
                # Aún así devolvemos los datos parciales para que el frontend pueda mostrar qué falta
                property_data = PropertyData(
                    precio=float(precio) if precio else 0.0,
                    m2=float(metros_cuadrados) if metros_cuadrados else 0.0,
                    habitaciones=int(data["habitaciones"]) if data.get("habitaciones") else None,
                    planta=str(data["planta"]) if data.get("planta") else None,
                    estado=None,
                    ubicacion=data.get("ubicacion") or "Not specified",
                    url_origen="texto_manual"
                )
                
                return property_data, extraction_log
            
            # Normalizar estado
            estado_raw = data.get("estado", "").lower() if data.get("estado") else None
            estado_normalized = None
            if estado_raw:
                if "reformar" in estado_raw or "reforma" in estado_raw or "reform" in estado_raw:
                    estado_normalized = "reform"
                elif "bueno" in estado_raw or "buen" in estado_raw or "good" in estado_raw:
                    estado_normalized = "good"
                elif "nuevo" in estado_raw or "nueva" in estado_raw or "new" in estado_raw:
                    estado_normalized = "new"
                else:
                    estado_normalized = "good"  # Default
            
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
                ubicacion=data.get("ubicacion") or "Not specified",
                url_origen="texto_manual",
                alquiler_mensual_estimado=alquiler_mensual_estimado
            )
            
            # Crear ExtractionLog
            extraction_log = ExtractionLog(
                found_fields=extraction_log_data.get("found_fields", []),
                missing_fields=extraction_log_data.get("missing_fields", []),
                reasoning=extraction_log_data.get("reasoning", "Data extracted from listing text."),
                is_complete=True,
                warnings=None
            )
            
            return property_data, extraction_log
            
        except APITimeoutError:
            raise TimeoutError("OpenAI request timed out after 15 seconds. Please try again.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing LLM response: {str(e)}. Response received: {content[:200] if 'content' in locals() else 'N/A'}")
        except TimeoutError:
            raise  # Re-raise TimeoutError
        except Exception as e:
            # Detect connection errors
            error_msg = str(e).lower()
            if "connection" in error_msg or "timeout" in error_msg or "network" in error_msg:
                raise ConnectionError(f"OpenAI connection error: {str(e)}. Please check your connection and try again.")
            raise Exception(f"Error extracting data with LLM: {str(e)}")

