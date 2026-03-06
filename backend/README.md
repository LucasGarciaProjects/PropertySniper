# Libertad Sniper AI

Herramienta de análisis de rentabilidad inmobiliaria basada en el método de Libertad Inmobiliaria de Carlos Galán.

## Características

- ✅ Scraping automático de propiedades de Idealista y Fotocasa
- ✅ Cálculo de rentabilidad según método de Libertad Inmobiliaria
- ✅ Generación de informes PDF con semáforo de rentabilidad
- ✅ API REST lista para conectar con frontend (Lovable)

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno:
```bash
# Crear archivo .env
echo "FIRECRAWL_API_KEY=tu_api_key_aqui" > .env

# Opcional: Configurar orígenes CORS permitidos (por defecto permite todos "*")
# echo "ALLOWED_ORIGINS=https://tu-proyecto.lovable.app,http://localhost:3000" >> .env
```

## Uso

### Iniciar el servidor

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`

### Documentación de la API

Una vez iniciado el servidor, accede a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints principales

- `POST /analyze`: Analiza una propiedad desde una URL
- `GET /download/{filename}`: Descarga un PDF generado

### Ejemplo de uso

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"url": "https://www.idealista.com/inmueble/12345678/"}
)

data = response.json()
print(f"Rentabilidad: {data['analysis']['rentabilidad_neta']:.2f}%")
print(f"Semáforo: {data['analysis']['semaforo']}")
```

## Método de Cálculo

### Gastos de adquisición
- 10% ITP
- 3.000€ (notaría/gestoría)

### Reforma estimada
- Estado "a reformar": 400€/m²
- Estado "bueno": 50€/m²

### Alquiler estimado
- Basado en precio medio de la zona
- Ratio por defecto: 6-8€/m² (promedio 7€/m²)

### Rentabilidad
- Gastos fijos: 20% del alquiler anual
- Rentabilidad Neta = (Alquiler anual - Gastos fijos) / Inversión total

### Semáforo
- 🟢 VERDE: Rentabilidad > 7%
- 🟡 AMARILLO: 5% - 7%
- 🔴 ROJO: < 5%

## Estructura del proyecto

```
libertad-sniper-ai/
├── main.py              # FastAPI app principal
├── scraper.py           # Lógica de scraping con Firecrawl
├── calculator.py        # Cálculo de rentabilidad
├── pdf_generator.py     # Generación de PDFs
├── models.py            # Modelos Pydantic
├── requirements.txt     # Dependencias
└── reports/             # PDFs generados (se crea automáticamente)
```

## Configuración de CORS

La API está configurada con CORS para permitir conexiones desde frontends externos (como Lovable).

### Configuración por defecto
- Por defecto, permite conexiones desde **cualquier origen** (`*`), lo cual es útil para desarrollo.

### Configuración para producción
Para restringir los orígenes permitidos, configura la variable de entorno `ALLOWED_ORIGINS` en tu archivo `.env`:

```bash
# Permitir múltiples orígenes (separados por comas)
ALLOWED_ORIGINS=https://tu-proyecto.lovable.app,https://otro-dominio.com

# O permitir solo uno
ALLOWED_ORIGINS=https://tu-proyecto.lovable.app
```

### Headers permitidos
- **Métodos**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Todos (`*`)
- **Credentials**: Habilitado
- **Expose Headers**: Todos (`*`)

## Notas

- Se requiere una API key de Firecrawl para el scraping
- Los PDFs se guardan en el directorio `reports/`
- La API está lista para conectar con frontends de Lovable u otros frameworks

