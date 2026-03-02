# Instrucciones para Debug del Scraper

## Problema: No se puede extraer el precio

Si estás viendo el error "No se pudieron extraer datos esenciales. Precio: None", sigue estos pasos:

### 1. Usar el endpoint de debug (Backend - Puerto 8000)

El endpoint de debug está en el **backend** (puerto 8000), NO en el frontend (puerto 8080).

**Opción A: Desde la terminal:**
```bash
curl -X POST http://localhost:8000/debug/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "TU_URL_DE_IDEALISTA_AQUI"}'
```

**Opción B: Desde el navegador (Swagger UI):**
1. Abre: http://localhost:8000/docs
2. Busca el endpoint `/debug/scrape`
3. Haz clic en "Try it out"
4. Pega tu URL de Idealista
5. Haz clic en "Execute"

### 2. Interpretar los resultados

El endpoint te mostrará:
- `content_length`: Longitud del contenido de texto
- `html_length`: Longitud del HTML
- `content_preview`: Primeros 500 caracteres del contenido
- `extracted_price`: Precio extraído (o null si no se encontró)
- `extracted_m2`: Metros cuadrados extraídos

### 3. Problemas comunes

#### Problema: Captcha detectado
**Síntoma:** El contenido contiene "captcha"
**Solución:** 
- Idealista está bloqueando el scraping
- Espera unos minutos y vuelve a intentar
- Prueba con una URL diferente
- Considera usar un proxy o configuración diferente en Firecrawl

#### Problema: Contenido muy corto
**Síntoma:** `content_length` es menor a 100 caracteres
**Solución:**
- La página no se cargó correctamente
- Verifica que la URL sea válida y accesible
- Puede que requiera login o tenga protección

#### Problema: Precio es null pero hay contenido
**Síntoma:** `extracted_price` es null pero `content_length` es grande
**Solución:**
- El formato del precio en la página puede ser diferente
- Revisa el `content_preview` para ver cómo aparece el precio
- Puede necesitarse ajustar los patrones regex en `scraper.py`

### 4. Solución temporal: Entrada manual

Si el scraping no funciona, puedes modificar temporalmente el código para permitir entrada manual de datos mientras se soluciona el problema de scraping.

### 5. Contacto

Si el problema persiste, comparte:
- La URL que estás intentando analizar
- El resultado del endpoint `/debug/scrape`
- Cualquier mensaje de error adicional

