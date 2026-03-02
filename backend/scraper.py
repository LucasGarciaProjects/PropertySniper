import re
import os
import time
import asyncio
from typing import Dict, Optional
from firecrawl import FirecrawlApp
from models import PropertyData


class PropertyScraper:
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el scraper con Firecrawl.
        Si no se proporciona API key, se intentará obtener de variables de entorno.
        """
        api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            # Permitir inicialización sin API key (se requerirá al hacer scraping)
            self.app = None
            self.api_key = None
        else:
            self.app = FirecrawlApp(api_key=api_key)
            self.api_key = api_key
    
    def extract_price(self, text: str) -> Optional[float]:
        """Extrae el precio del texto."""
        # Limpiar el texto de caracteres especiales que puedan interferir
        text_clean = text.replace('\n', ' ').replace('\t', ' ')
        
        # Patrones más robustos para capturar precios en diferentes formatos
        patterns = [
            # Formato español: "250.000 €" o "250.000€"
            r'(\d{1,3}(?:\.\d{3})+)\s*€',
            # Formato sin puntos: "250000 €" o "250000€"
            r'(\d{4,})\s*€',
            # Con texto "precio": "precio: 250.000 €"
            r'precio[:\s]+(\d{1,3}(?:\.\d{3})+)',
            # Con "euros"
            r'(\d{1,3}(?:\.\d{3})+)\s*euros?',
            # En HTML/data attributes: data-price="250000"
            r'["\']?price["\']?\s*[:=]\s*["\']?(\d{1,3}(?:\.\d{3})+)',
            # Formato con comas: "250,000 €"
            r'(\d{1,3}(?:,\d{3})+)\s*€',
            # Números grandes al inicio de línea (común en Idealista)
            r'^\s*(\d{1,3}(?:\.\d{3})+)\s*€',
            # En contexto de "€/mes" o similar
            r'(\d{1,3}(?:\.\d{3})+)\s*€(?!\s*/\s*(?:mes|m2|m²))',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_clean, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                price_str = match.group(1)
                # Limpiar el string: quitar puntos de miles y convertir comas a puntos
                price_str = price_str.replace('.', '').replace(',', '.')
                try:
                    price = float(price_str)
                    # Validar que sea un precio razonable (entre 10.000 y 10.000.000)
                    if 10000 <= price <= 10000000:
                        return price
                except ValueError:
                    continue
        
        # Si no encontramos nada, buscar cualquier número grande seguido de €
        fallback_pattern = r'(\d{5,})\s*€'
        match = re.search(fallback_pattern, text_clean, re.IGNORECASE)
        if match:
            try:
                price = float(match.group(1))
                if 10000 <= price <= 10000000:
                    return price
            except ValueError:
                pass
        
        return None
    
    def extract_m2(self, text: str) -> Optional[float]:
        """Extrae los metros cuadrados del texto."""
        patterns = [
            r'(\d+(?:[.,]\d+)?)\s*m[²2]',
            r'(\d+(?:[.,]\d+)?)\s*metros?\s*cuadrados?',
            r'superficie[:\s]+(\d+(?:[.,]\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                m2_str = match.group(1).replace(',', '.')
                try:
                    return float(m2_str)
                except ValueError:
                    continue
        return None
    
    def extract_habitaciones(self, text: str) -> Optional[int]:
        """Extrae el número de habitaciones."""
        patterns = [
            r'(\d+)\s*hab(?:itaciones?)?',
            r'(\d+)\s*dorm(?:itorios?)?',
            r'habitaciones?[:\s]+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        return None
    
    def extract_planta(self, text: str) -> Optional[str]:
        """Extrae la planta del inmueble."""
        patterns = [
            r'planta\s+(\d+|baja|sótano|ático)',
            r'(\d+)\s*ª?\s*planta',
            r'planta[:\s]+([^,\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def extract_estado(self, text: str) -> Optional[str]:
        """Extrae el estado del inmueble."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['a reformar', 'reformar', 'necesita reforma', 'rehabilitar']):
            return 'a reformar'
        elif any(word in text_lower for word in ['buen estado', 'bueno', 'excelente', 'nuevo']):
            return 'bueno'
        elif any(word in text_lower for word in ['regular', 'aceptable']):
            return 'regular'
        return None
    
    def extract_ubicacion(self, text: str, url: str) -> Optional[str]:
        """Extrae la ubicación del inmueble."""
        # Intentar extraer de la URL primero (Idealista/Fotocasa suelen tener la ciudad en la URL)
        url_patterns = [
            r'/([^/]+)/([^/]+)/',
            r'/([^/]+)-([^/]+)/',
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, url)
            if match:
                # Intentar encontrar ciudad y zona
                parts = match.groups()
                if len(parts) >= 2:
                    return f"{parts[0]}, {parts[1]}"
        
        # Si no se encuentra en la URL, buscar en el texto
        patterns = [
            r'ubicaci[oó]n[:\s]+([^,\n]+)',
            r'en\s+([A-Z][^,\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _scrape_with_retries(self, url: str, max_retries: int = 3) -> Dict:
        """
        Intenta scrapear una URL con reintentos y opciones anti-bot.
        
        Args:
            url: URL a scrapear
            max_retries: Número máximo de reintentos
            
        Returns:
            Resultado del scraping de Firecrawl
        """
        if not self.app:
            raise Exception("Firecrawl API key no configurada. Por favor, configura FIRECRAWL_API_KEY en el archivo .env")
        
        # Configuración avanzada para evitar bloqueos
        # Firecrawl acepta parámetros como diccionario en el método scrape_url
        scrape_params = {
            'waitFor': 5000,  # Esperar 5 segundos reales para que cargue el contenido
            'formats': ['markdown', 'html'],  # Pedir ambos formatos
            'headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            'extract': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'precio': {'type': 'number', 'description': 'Precio de venta en euros'},
                        'metros_cuadrados': {'type': 'number', 'description': 'Superficie en metros cuadrados'},
                        'habitaciones': {'type': 'number', 'description': 'Número de habitaciones'},
                        'planta': {'type': 'string', 'description': 'Planta del inmueble'},
                        'estado': {'type': 'string', 'description': 'Estado del inmueble (a reformar, bueno, etc.)'},
                        'ubicacion': {'type': 'string', 'description': 'Ubicación completa del inmueble'},
                    },
                    'required': ['precio', 'metros_cuadrados']
                },
                'systemPrompt': 'Eres un asistente que extrae datos de inmuebles de Idealista o Fotocasa. Si la página muestra un captcha, bloqueo, o mensaje de error, responde únicamente con la palabra "BLOQUEO" en el campo precio. Extrae solo datos reales de la propiedad.'
            }
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Intentar scrapear con parámetros avanzados
                # Firecrawl puede aceptar params como segundo argumento o como parte de un diccionario
                try:
                    result = self.app.scrape_url(url, params=scrape_params)
                except TypeError:
                    # Si no acepta params, intentar pasarlos directamente
                    result = self.app.scrape_url(url, **scrape_params)
                
                # Verificar si hay bloqueo en la respuesta
                if isinstance(result, dict):
                    content = result.get('markdown', '') or result.get('content', '') or ''
                    extracted = result.get('extract', {})
                    
                    # Verificar si el LLM detectó bloqueo
                    if isinstance(extracted, dict) and extracted.get('precio') == 'BLOQUEO':
                        raise Exception("Bloqueo detectado por el sistema de extracción")
                    
                    # Verificar captcha en el contenido
                    if 'captcha' in content.lower() or 'blocked' in content.lower():
                        if attempt < max_retries - 1:
                            time.sleep(2)  # Esperar 2 segundos antes del siguiente intento
                            continue
                        raise Exception("Idealista está mostrando un captcha o bloqueo después de múltiples intentos")
                
                return result
                
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Esperar antes del siguiente intento (backoff exponencial)
                    wait_time = 2 * (attempt + 1)
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Error después de {max_retries} intentos: {str(e)}")
        
        raise Exception(f"No se pudo scrapear después de {max_retries} intentos. Último error: {str(last_error)}")
    
    async def scrape_property(self, url: str) -> PropertyData:
        """
        Scrapea una propiedad desde Idealista o Fotocasa usando Firecrawl con opciones anti-bot.
        """
        try:
            # Usar método con reintentos y opciones avanzadas
            result = self._scrape_with_retries(url, max_retries=3)
            
            # Obtener el texto completo - manejar diferentes formatos de respuesta
            content = ""
            html_content = ""
            extracted_data = {}
            
            if isinstance(result, dict):
                # Intentar usar datos extraídos por LLM primero (más confiable)
                extracted_data = result.get('extract', {})
                
                # Si el LLM extrajo datos, usarlos directamente
                if isinstance(extracted_data, dict) and extracted_data.get('precio'):
                    precio_llm = extracted_data.get('precio')
                    m2_llm = extracted_data.get('metros_cuadrados')
                    
                    # Validar que no sea bloqueo
                    if precio_llm != 'BLOQUEO' and precio_llm is not None:
                        # Usar datos del LLM si están disponibles
                        precio = float(precio_llm) if precio_llm else None
                        m2 = float(m2_llm) if m2_llm else None
                        habitaciones = extracted_data.get('habitaciones')
                        planta = extracted_data.get('planta')
                        estado = extracted_data.get('estado')
                        ubicacion = extracted_data.get('ubicacion')
                        
                        # Si tenemos precio y m2 del LLM, usarlos
                        if precio and m2:
                            return PropertyData(
                                precio=precio,
                                m2=m2,
                                habitaciones=int(habitaciones) if habitaciones else None,
                                planta=planta,
                                estado=estado or 'bueno',
                                ubicacion=ubicacion or self.extract_ubicacion("", url) or 'No especificada',
                                url_origen=url
                            )
                
                # Si no hay datos del LLM, usar extracción tradicional
                content = (
                    result.get('markdown', '') or 
                    result.get('content', '') or 
                    result.get('text', '') or
                    ''
                )
                html_content = result.get('html', '') or result.get('sourceHTML', '') or ''
            elif hasattr(result, 'markdown'):
                content = result.markdown
            elif hasattr(result, 'content'):
                content = result.content
            elif hasattr(result, 'html'):
                html_content = result.html
            else:
                content = str(result)
            
            # Verificar si hay captcha o bloqueo
            if 'captcha' in content.lower() or 'captcha' in html_content.lower() or 'blocked' in content.lower():
                raise Exception("Idealista está mostrando un captcha o bloqueo. Esto puede deberse a protección anti-bot. Intenta con una URL diferente o espera unos minutos.")
            
            # Si tenemos HTML, extraer texto limpio de él
            if html_content and not content:
                # Remover tags HTML pero mantener el contenido
                html_text = re.sub(r'<[^>]+>', ' ', html_content)
                html_text = re.sub(r'\s+', ' ', html_text)
                content = html_text
            
            # Combinar contenido de texto y HTML para máxima cobertura
            full_content = content + " " + html_content if html_content else content
            
            # Si el contenido es muy corto o parece vacío, puede ser un problema
            if len(full_content.strip()) < 100:
                raise Exception(f"El contenido obtenido es muy corto ({len(full_content)} caracteres). Puede que la página no se haya cargado correctamente o esté bloqueada.")
            
            # Extraer datos usando métodos tradicionales (fallback)
            precio = self.extract_price(full_content)
            m2 = self.extract_m2(full_content)
            habitaciones = self.extract_habitaciones(full_content)
            planta = self.extract_planta(full_content)
            estado = self.extract_estado(full_content)
            ubicacion = self.extract_ubicacion(full_content, url)
            
            # Validar que tenemos al menos precio y m2
            if not precio or not m2:
                raise ValueError(f"No se pudieron extraer datos esenciales. Precio: {precio}, m2: {m2}")
            
            return PropertyData(
                precio=precio,
                m2=m2,
                habitaciones=habitaciones,
                planta=planta,
                estado=estado or 'bueno',  # Por defecto 'bueno' si no se encuentra
                ubicacion=ubicacion or 'No especificada',
                url_origen=url
            )
            
        except Exception as e:
            raise Exception(f"Error al scrapear la propiedad: {str(e)}")

