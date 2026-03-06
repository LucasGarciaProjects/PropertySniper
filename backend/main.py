from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
from models import PropertyAnalysisRequest, AnalysisResponse, TextAnalysisRequest, ManualAnalysisRequest, RecalculateRequest, RentabilityAnalysis
from scraper import PropertyScraper
from calculator import RentabilityCalculator
from pdf_generator import PDFGenerator
from llm_extractor import LLMDataExtractor
from pydantic import BaseModel
from typing import List
from models import PropertyData
from finance_service import finance_service, Transaction, Asset, FinancialSummary
import json
import uvicorn

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="Libertad Sniper AI API",
    description="API for real estate rentability analysis using the Property Liberty method by Carlos Galán",
    version="1.0.0"
)

# Configurar CORS para permitir conexiones desde Lovable y otros frontends
# Obtener orígenes permitidos desde variables de entorno o usar "*" por defecto
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env == "*":
    # Permitir cualquier origen (útil para desarrollo)
    # Incluir explícitamente localhost:5173 (Vite por defecto)
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
else:
    # Permitir orígenes específicos (separados por comas)
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]
    # Asegurar que localhost:5173 esté incluido si no está en la lista
    if "http://localhost:5173" not in allowed_origins:
        allowed_origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Inicializar componentes
scraper = PropertyScraper(api_key=os.getenv("FIRECRAWL_API_KEY"))
calculator = RentabilityCalculator()
pdf_generator = PDFGenerator()

# Inicializar extractor LLM (opcional, solo si hay API key)
try:
    llm_extractor = LLMDataExtractor(api_key=os.getenv("OPENAI_API_KEY"))
except ValueError:
    llm_extractor = None  # Permitir que funcione sin LLM si no hay API key


@app.get("/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {
        "message": "Libertad Sniper AI API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "healthy"}


@app.post("/debug/scrape")
async def debug_scrape(request: PropertyAnalysisRequest):
    """
    Endpoint de debug para ver qué devuelve Firecrawl.
    Útil para diagnosticar problemas de extracción de datos.
    """
    try:
        url_str = str(request.url)
        result = scraper.app.scrape_url(url_str)
        
        # Extraer contenido
        content = ""
        html_content = ""
        
        if isinstance(result, dict):
            content = result.get('markdown', '') or result.get('content', '') or result.get('text', '')
            html_content = result.get('html', '') or result.get('sourceHTML', '')
        else:
            content = str(result)
        
        # Intentar extraer datos
        precio = scraper.extract_price(content + " " + html_content)
        m2 = scraper.extract_m2(content + " " + html_content)
        
        return {
            "url": url_str,
            "content_length": len(content),
            "html_length": len(html_content),
            "content_preview": content[:500] if content else "No content",
            "html_preview": html_content[:500] if html_content else "No HTML",
            "extracted_price": precio,
            "extracted_m2": m2,
            "raw_result_keys": list(result.keys()) if isinstance(result, dict) else "Not a dict"
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_property(request: PropertyAnalysisRequest):
    """
    Analiza una propiedad inmobiliaria desde una URL de Idealista o Fotocasa.
    
    Args:
        request: Request con la URL de la propiedad
        
    Returns:
        AnalysisResponse con el análisis completo y ruta del PDF generado
    """
    try:
        url_str = str(request.url)
        
        # Validar que sea una URL de Idealista o Fotocasa
        if "idealista" not in url_str.lower() and "fotocasa" not in url_str.lower():
            return AnalysisResponse(
                success=False,
                error="URL must be from Idealista or Fotocasa"
            )
        
        # 1. Scrapear la propiedad
        property_data = await scraper.scrape_property(url_str)
        
        # 2. Calcular rentabilidad
        analysis = calculator.calculate_rentability(property_data)
        
        # 3. Generar PDF
        pdf_path = pdf_generator.generate_pdf(analysis, None)
        
        return AnalysisResponse(
            success=True,
            analysis=analysis,
            pdf_path=pdf_path
        )
        
    except ValueError as e:
        return AnalysisResponse(
            success=False,
            error=f"Validation error: {str(e)}"
        )
    except Exception as e:
        return AnalysisResponse(
            success=False,
            error=f"Error processing property: {str(e)}"
        )


@app.post("/analyze-text", response_model=AnalysisResponse)
async def analyze_from_text(request: TextAnalysisRequest):
    """
    Analiza una propiedad desde texto plano copiado de un portal inmobiliario.
    Usa LLM (OpenAI gpt-4o-mini) para extraer los datos estructurados con optimización de costes.
    
    Args:
        request: Request con el texto plano de la propiedad
        
    Returns:
        AnalysisResponse con el análisis completo y ruta del PDF generado
    """
    if not llm_extractor:
        return AnalysisResponse(
            success=False,
            error="OpenAI API key not configured. Please configure OPENAI_API_KEY in .env file"
        )
    
    # Validar que el texto no esté vacío
    if not request.text or not request.text.strip():
        return AnalysisResponse(
            success=False,
            error="Text is empty. Please paste the real estate ad content."
        )
    
    try:
        # 1. Extraer datos del texto usando LLM (con timeout de 15s y max_tokens=800)
        property_data, extraction_log = llm_extractor.extract_from_text(request.text)
        
        # 2. Verificar si el análisis está completo (tiene precio y m2)
        if not extraction_log.is_complete:
            return AnalysisResponse(
                success=False,
                error="Incomplete analysis: critical data missing (price or m2). Please complete these fields manually or paste a more complete text.",
                extraction_log=extraction_log
            )
        
        # 3. Calcular rentabilidad
        analysis = calculator.calculate_rentability(property_data)
        
        # 4. Añadir información del cálculo de alquiler al extraction_log
        if extraction_log:
            # Calcular ratio de alquiler por m²
            ratio_alquiler = analysis.alquiler_mensual / property_data.m2 if property_data.m2 > 0 else 0
            ubicacion_display = property_data.ubicacion or "unspecified location"
            
            # Determinar si el alquiler fue estimado o encontrado
            alquiler_fue_estimado = "alquiler_mensual" in extraction_log.missing_fields or property_data.alquiler_mensual_estimado is None
            
            if alquiler_fue_estimado:
                # Añadir información de estimación al razonamiento
                alquiler_info = f"Estimated monthly rent at {analysis.alquiler_mensual:.0f} EUR based on a ratio of {ratio_alquiler:.0f} EUR/m2 for the area of {ubicacion_display}."
                if extraction_log.reasoning:
                    extraction_log.reasoning = alquiler_info + " " + extraction_log.reasoning
                else:
                    extraction_log.reasoning = alquiler_info
            
            # Verificar si el descuento OMR es > 50% y añadir warning
            descuento_porcentaje = ((analysis.precio_compra - analysis.omr) / analysis.precio_compra * 100) if analysis.precio_compra > 0 else 0
            warnings = extraction_log.warnings or []
            
            if descuento_porcentaje > 50:
                warnings.append("Market price far exceeds the 8% yield target. Required discount is over 50%.")
                extraction_log.warnings = warnings
        
        # 5. Generar PDF
        pdf_path = pdf_generator.generate_pdf(analysis, extraction_log)
        
        return AnalysisResponse(
            success=True,
            analysis=analysis,
            pdf_path=pdf_path,
            extraction_log=extraction_log
        )
        
    except TimeoutError as e:
        return AnalysisResponse(
            success=False,
            error=f"Timeout: {str(e)}"
        )
    except ConnectionError as e:
        return AnalysisResponse(
            success=False,
            error=f"Connection error: {str(e)}"
        )
    except ValueError as e:
        return AnalysisResponse(
            success=False,
            error=f"Validation error: {str(e)}"
        )
    except Exception as e:
        return AnalysisResponse(
            success=False,
            error=f"Error processing text: {str(e)}"
        )


@app.post("/analyze-manual", response_model=AnalysisResponse)
async def analyze_manual(request: ManualAnalysisRequest):
    """
    Analiza una propiedad con datos introducidos manualmente.
    
    Args:
        request: Request con los datos manuales de la propiedad
        
    Returns:
        AnalysisResponse con el análisis completo y ruta del PDF generado
    """
    try:
        # Crear PropertyData desde los datos manuales
        property_data = PropertyData(
            precio=request.precio,
            m2=request.m2,
            habitaciones=request.habitaciones,
            planta=request.planta,
            estado=request.estado or 'good',
            ubicacion=request.ubicacion or 'Not specified',
            url_origen="manual_entry"
        )
        
        # Si se proporciona coste de reforma o alquiler, necesitamos ajustar el calculador
        # Por ahora, usamos el calculador normal
        analysis = calculator.calculate_rentability(property_data)
        
        # Si se proporcionó coste de reforma manual, reemplazarlo
        if request.coste_reforma is not None:
            # Recalcular inversión total con el coste de reforma manual
            analysis.coste_reforma = request.coste_reforma
            analysis.inversion_total = (
                analysis.precio_compra + 
                analysis.gastos_adquisicion + 
                request.coste_reforma
            )
            # Recalcular rentabilidad
            analysis.rentabilidad_neta = (analysis.beneficio_neto_anual / analysis.inversion_total) * 100
            
            # Actualizar semáforo
            if analysis.rentabilidad_neta >= 7.0:
                analysis.semaforo = "GREEN"
            elif analysis.rentabilidad_neta >= 5.0:
                analysis.semaforo = "YELLOW"
            else:
                analysis.semaforo = "RED"
        
        # Si se proporcionó alquiler mensual manual, recalcular todo
        if request.alquiler_mensual is not None:
            analysis.alquiler_mensual = request.alquiler_mensual
            analysis.alquiler_anual = request.alquiler_mensual * 12
            analysis.gastos_fijos_anuales = analysis.alquiler_anual * 0.20
            analysis.beneficio_neto_anual = analysis.alquiler_anual - analysis.gastos_fijos_anuales
            analysis.rentabilidad_neta = (analysis.beneficio_neto_anual / analysis.inversion_total) * 100
            
            # Actualizar semáforo
            if analysis.rentabilidad_neta >= 7.0:
                analysis.semaforo = "GREEN"
            elif analysis.rentabilidad_neta >= 5.0:
                analysis.semaforo = "YELLOW"
            else:
                analysis.semaforo = "RED"
            
            # Recalcular OMR con el nuevo alquiler (crear PropertyData temporal con alquiler actualizado)
            # Para OMR, necesitamos usar el alquiler proporcionado
            temp_property = PropertyData(
                precio=property_data.precio,
                m2=property_data.m2,
                habitaciones=property_data.habitaciones,
                planta=property_data.planta,
                estado=property_data.estado,
                ubicacion=property_data.ubicacion,
                url_origen=property_data.url_origen
            )
            # Crear calculador temporal con alquiler personalizado
            temp_calculator = RentabilityCalculator(precio_medio_alquiler_zona=request.alquiler_mensual / property_data.m2 if property_data.m2 > 0 else None)
            analysis.omr = temp_calculator.calculate_omr(temp_property)
        
        # Generar PDF
        pdf_path = pdf_generator.generate_pdf(analysis, None)
        
        return AnalysisResponse(
            success=True,
            analysis=analysis,
            pdf_path=pdf_path
        )
        
    except ValueError as e:
        return AnalysisResponse(
            success=False,
            error=f"Validation error: {str(e)}"
        )
    except Exception as e:
        return AnalysisResponse(
            success=False,
            error=f"Error processing data: {str(e)}"
        )


@app.post("/recalculate", response_model=AnalysisResponse)
async def recalculate_analysis(request: RecalculateRequest):
    """
    Recalcula el análisis con un nuevo alquiler mensual.
    Útil para ajustar el alquiler y ver cómo afecta a la rentabilidad y OMR.
    
    Args:
        request: Request con el nuevo alquiler y datos del análisis original
        
    Returns:
        AnalysisResponse con el análisis recalculado
    """
    try:
        # Crear PropertyData temporal para el recálculo
        temp_property = PropertyData(
            precio=request.precio_compra,
            m2=request.m2,
            ubicacion=request.ubicacion or "Not specified",
            url_origen="recalculated"
        )
        
        # Crear calculador con el alquiler personalizado
        temp_calculator = RentabilityCalculator()
        
        # Calcular rentabilidad con el nuevo alquiler
        # Necesitamos crear un análisis temporal para usar calculate_rentability
        # Pero podemos calcular manualmente los valores clave
        
        # Gastos de adquisición ya están calculados
        gastos_adquisicion = request.gastos_adquisicion
        
        # Coste de reforma ya está calculado
        coste_reforma = request.coste_reforma
        
        # Inversión total
        inversion_total = request.precio_compra + gastos_adquisicion + coste_reforma
        
        # Nuevo alquiler
        alquiler_mensual = request.alquiler_mensual
        alquiler_anual = alquiler_mensual * 12
        
        # Gastos fijos anuales (20% del alquiler anual)
        gastos_fijos_anuales = alquiler_anual * 0.20
        
        # Beneficio neto anual
        beneficio_neto_anual = alquiler_anual - gastos_fijos_anuales
        
        # Rentabilidad neta
        rentabilidad_neta = (beneficio_neto_anual / inversion_total) * 100
        
        # Determinar semáforo
        if rentabilidad_neta >= 7.0:
            semaforo = "GREEN"
        elif rentabilidad_neta >= 5.0:
            semaforo = "YELLOW"
        else:
            semaforo = "RED"
        
        # Calcular nueva OMR con el nuevo alquiler
        # OMR necesita recalcularse con el nuevo alquiler
        beneficio_neto_anual_omr = alquiler_anual - gastos_fijos_anuales
        inversion_total_necesaria = beneficio_neto_anual_omr / 0.08
        omr = (inversion_total_necesaria - 3000 - coste_reforma) / 1.10
        omr = max(0, omr)
        
        # Crear análisis recalculado
        analysis = RentabilityAnalysis(
            precio_compra=request.precio_compra,
            gastos_adquisicion=gastos_adquisicion,
            coste_reforma=coste_reforma,
            inversion_total=inversion_total,
            alquiler_mensual=alquiler_mensual,
            alquiler_anual=alquiler_anual,
            gastos_fijos_anuales=gastos_fijos_anuales,
            beneficio_neto_anual=beneficio_neto_anual,
            rentabilidad_neta=rentabilidad_neta,
            semaforo=semaforo,
            omr=omr,
            property_data=temp_property
        )
        
        # Generar PDF con los datos actualizados
        pdf_path = pdf_generator.generate_pdf(analysis, request.extraction_log)
        
        return AnalysisResponse(
            success=True,
            analysis=analysis,
            pdf_path=pdf_path,
            extraction_log=request.extraction_log
        )
        
    except Exception as e:
        return AnalysisResponse(
            success=False,
            error=f"Error recalculating: {str(e)}"
        )


@app.get("/download/{filename}")
async def download_pdf(filename: str):
    """
    Descarga un PDF generado previamente.
    
    Args:
        filename: Nombre del archivo PDF
        
    Returns:
        Archivo PDF para descargar
    """
    filepath = os.path.join("reports", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=filename
    )



# --- WEALTH MANAGEMENT ENDPOINTS ---

@app.get("/dashboard/summary", response_model=FinancialSummary)
async def get_dashboard_summary():
    return finance_service.get_summary()

@app.get("/transactions", response_model=List[Transaction])
async def get_transactions():
    return finance_service.get_transactions()

@app.post("/transactions", response_model=Transaction)
async def add_transaction(transaction: Transaction):
    return finance_service.add_transaction(transaction)

@app.get("/assets", response_model=List[Asset])
async def get_assets():
    return finance_service.get_assets()

@app.post("/assets", response_model=Asset)
async def add_asset(asset: Asset):
    return finance_service.add_asset(asset)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_with_coach(request: ChatRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Obtener contexto financiero
    summary = finance_service.get_summary()
    transactions = finance_service.get_transactions()[:10] # Últimas 10
    
    context = f"""
    Act as an expert and motivating personal financial advisor. Your goal is to help the user improve their financial health.
    
    CURRENT FINANCIAL STATUS:
    - Total Income: {summary.total_income:.2f}€
    - Total Expenses: {summary.total_expenses:.2f}€
    - Net Balance: {summary.balance:.2f}€
    - Savings Rate: {summary.savings_rate:.1f}% (Recommended target: >20%)
    
    LATEST TRANSACTIONS:
    {json.dumps([t.dict() for t in transactions], ensure_ascii=False, indent=2)}
    
    INSTRUCTIONS:
    1. Analyze the provided data to give precise answers.
    2. If the user asks "how am I doing", use the KPIs above.
    3. If you detect high spending in categories like "Leisure" or "Restaurants", suggest moderation but with empathy.
    4. Maintain a professional, minimalist, and direct tone (Revolut/Apple style).
    5. Short and actionable answers (maximum 3 paragraphs).
    6. ALWAYS ANSWER IN ENGLISH.
    """
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": request.message}
            ]
        )
        
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

