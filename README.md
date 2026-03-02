# 💰 Libertad Wealth Management App & Sniper Inmobiliario

Este proyecto es una aplicación integral de gestión patrimonial ("Wealth Management") que combina el control de finanzas personales con herramientas avanzadas de análisis de inversión inmobiliaria ("Sniper Inmobiliario").

**Objetivo**: Centralizar tu salud financiera, controlar tus ingresos/gastos y analizar nuevas oportunidades de inversión desde una única interfaz moderna.

---

## 🏗 Arquitectura del Proyecto

El proyecto está dividido en dos partes principales:

### 1. Backend (API)
- **Tecnología**: Python con FastAPI.
- **Ubicación**: Carpeta `backend/`.
- **Responsabilidad**:
    - Gestionar la lógica de negocio financiera.
    - Persistencia de datos (Transacciones y Activos).
    - Scraping y análisis inmobiliario.
    - Integración con IA (OpenAI) para el Coach Financiero.
- **Datos**: Utiliza un sistema de persistencia ligera basado en archivos JSON (`data/transactions.json`, `data/assets.json`) para facilitar el despliegue local sin bases de datos complejas.

### 2. Frontend (Interfaz de Usuario)
- **Tecnología**: React + Vite + TypeScript + Tailwind CSS.
- **Ubicación**: Carpeta `frontend/`.
- **Responsabilidad**:
    - Interfaz de usuario moderna y responsiva (Estilo Apple/Revolut).
    - Visualización de datos (Gráficos, KPIs).
    - Interacción con el usuario (Formularios, Chat, Navegación).

---

## 🚀 Funcionalidades Clave

### A. 📊 Dashboard Financiero
Resumen visual de tu salud financiera en tiempo real.
- **KPIs**: Ingresos Totales, Gastos Totales, Tasa de Ahorro.
- **Gráficos**: Comparativa mensual de Ingresos vs. Gastos.
- **Cálculo automático**: Se actualiza al añadir nuevos movimientos.

### B. 📒 Libro de Registro
Gestión detallada de tu flujo de caja.
- **Registro de Movimientos**: Ingresos y Gastos categorizados.
- **Categorías Oficiales**: Nómina, Alquileres, Vivienda, Ocio, etc.
- **Historial**: Visualización limpia de todas las transacciones.

### C. 🎯 Sniper Inmobiliario
Herramienta de análisis de inversión basada en el método "Libertad Inmobiliaria".
- **Analizador**: Pega una URL (Idealista/Fotocasa) o texto para analizar una propiedad.
- **Métricas**: Calcula Rentabilidad Neta, Cashflow y Oferta Máxima Recomendada (OMR).
- **Integración**: Botón **"Añadir a mis proyecciones"** para guardar la propiedad como un activo en tu balance.
- **Generador de PDF**: Crea informes detallados de cada análisis.

### D. 🤖 AI Financial Coach
Tu asesor financiero personal disponible 24/7.
- **Chat Inteligente**: Interfaz de mensajería integrada.
- **Contexto Real**: La IA "lee" tus datos financieros antes de responder (sabe cuánto has gastado, ahorrado, etc.).
- **Motor**: Conectado a OpenAI (GPT-4o-mini).

---

## 📂 Estructura de Archivos

```
sniper-inmobiliario/
├── backend/                   # Servidor API
│   ├── main.py               # Punto de entrada y endpoints API
│   ├── finance_service.py    # Lógica de gestión financiera (NUEVO)
│   ├── scraper.py            # Lógica de scraping inmobiliario
│   ├── calculator.py         # Cálculos de rentabilidad
│   ├── models.py             # Modelos de datos Pydantic
│   ├── llm_extractor.py      # Extracción de datos con IA
│   └── reports/              # PDFs generados
│
├── frontend/                  # Cliente Web
│   ├── src/
│   │   ├── components/
│   │   │   ├── WealthDashboard.tsx  # Componente Dashboard (NUEVO)
│   │   │   ├── ExpenseLog.tsx       # Componente Registro (NUEVO)
│   │   │   ├── SniperSection.tsx    # Componente Sniper (NUEVO)
│   │   │   ├── AICoach.tsx          # Componente Chat IA (NUEVO)
│   │   │   └── ...
│   │   ├── pages/
│   │   │   └── Index.tsx            # Página principal con Tabs
│   │   └── services/
│   │       └── api.ts               # Cliente HTTP para conectar con Backend
│
├── data/                      # Base de Datos Local (JSON)
│   ├── transactions.json     # Historial de ingresos/gastos
│   └── assets.json           # Activos inmobiliarios guardados
│
└── PROJECT_OVERVIEW.md        # Este archivo
```

---

## 🛠 Instrucciones de Ejecución

Para levantar el proyecto completo, necesitas dos terminales:

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate  # O venv\Scripts\activate en Windows
# Instalar dependencias si es la primera vez: pip install -r requirements.txt
python main.py
```
*El backend correrá en `http://localhost:8000`*

### Terminal 2: Frontend
```bash
cd frontend
# Instalar dependencias si es la primera vez: npm install
npm run dev
```
*El frontend correrá en `http://localhost:8081` (o similar)*

---

## 🔄 Flujo de Trabajo Típico

1.  **Registrar**: Añades tu nómina y gastos del mes en la pestaña "Registro".
2.  **Monitorizar**: Vas al "Dashboard" para ver cómo afecta a tu tasa de ahorro.
3.  **Analizar**: Ves un piso en Idealista, pegas la URL en "Sniper".
4.  **Proyectar**: Si es rentable, lo guardas en tus proyecciones.
5.  **Consultar**: Preguntas al "Coach" si deberías comprarlo basándote en tus ahorros actuales.

---

**Última actualización**: 2026-01-14 (Transformación a Wealth Management App)
