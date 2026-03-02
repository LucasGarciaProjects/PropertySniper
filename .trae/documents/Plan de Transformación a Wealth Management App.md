# Transformación a Wealth Management App

## 1. Arquitectura & Navegación
Transformaré la aplicación actual (React/Vite) implementando una navegación por pestañas (Tabs) que integre todas las funcionalidades:

1.  **Dashboard**: Resumen visual con KPIs y gráficos.
2.  **Libro de Registro**: Gestión de ingresos y gastos.
3.  **Sniper Inmobiliario**: La herramienta actual de análisis (reubicada).
4.  **AI Coach**: Chat con el asesor financiero.

## 2. Backend: Servicios Financieros (FastAPI)
Crearé un nuevo módulo `finance_service.py` y extenderé `main.py` para soportar:

-   **Persistencia Ligera**: Implementaré un sistema de almacenamiento basado en archivos JSON (`data/transactions.json`, `data/assets.json`) para guardar tus datos sin complicar la infraestructura con bases de datos SQL por ahora.
-   **Seed Data**: Al iniciar, el sistema verificará si hay datos; si no, cargará automáticamente los registros de ejemplo (Nómina, Hipoteca, etc.).
-   **Endpoints**:
    -   `GET/POST /transactions`: Para el Libro de Registro.
    -   `GET/POST /assets`: Para guardar las proyecciones del Sniper.
    -   `POST /chat`: Para el AI Coach (conectado a OpenAI).

## 3. Frontend: Componentes Nuevos
Desarrollaré los siguientes componentes en `frontend/src/components/`:

-   **`WealthDashboard.tsx`**:
    -   Tarjetas de métricas: Ingresos, Gastos, Ahorro (con lógica de colores).
    -   Gráfico de Barras: Comparativa mensual usando `recharts` (si está disponible) o componentes UI existentes.
-   **`ExpenseLog.tsx`**:
    -   Tabla de movimientos limpia.
    -   Formulario de "Añadir Movimiento" con los Dropdowns de categorías solicitados.
-   **`SniperSection.tsx`**:
    -   Encapsularé la lógica actual del analizador inmobiliario.
    -   Añadiré el botón **"Añadir a mis proyecciones"** al finalizar un análisis.
-   **`AICoach.tsx`**:
    -   Interfaz de chat minimalista.
    -   Conexión con el backend para enviar tu contexto financiero al modelo AI.

## 4. Ejecución
1.  **Backend**: Implementar lógica de finanzas, almacenamiento JSON y carga de datos iniciales.
2.  **API**: Actualizar `frontend/src/services/api.ts` con los nuevos endpoints.
3.  **Frontend**:
    -   Crear los nuevos componentes.
    -   Refactorizar `Index.tsx` para usar el sistema de Tabs.
    -   Integrar todo bajo la estética "Apple Health/Revolut" (sombras suaves, bordes redondeados).
