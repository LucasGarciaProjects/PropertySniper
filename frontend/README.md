# Libertad Sniper AI - Frontend

Frontend de la herramienta de análisis de rentabilidad inmobiliaria basada en el método de Libertad Inmobiliaria de Carlos Galán.

## Tecnologías

- **Vite** - Build tool y dev server
- **React 18** - Framework UI
- **TypeScript** - Tipado estático
- **shadcn/ui** - Componentes UI
- **Tailwind CSS** - Estilos
- **React Router** - Navegación
- **TanStack Query** - Gestión de estado del servidor

## Instalación

```bash
npm install
# o
bun install
```

## Desarrollo

```bash
npm run dev
# o
bun dev
```

La aplicación estará disponible en `http://localhost:5173`

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```env
VITE_API_URL=http://localhost:8000
```

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/      # Componentes React
│   │   ├── Dashboard.tsx
│   │   ├── HeroInput.tsx
│   │   ├── Header.tsx
│   │   └── ui/          # Componentes shadcn/ui
│   ├── pages/           # Páginas de la aplicación
│   │   └── Index.tsx    # Página principal
│   ├── services/        # Servicios API
│   │   └── api.ts       # Cliente API para backend
│   └── lib/             # Utilidades
└── public/              # Archivos estáticos
```

## Funcionalidades

- ✅ Análisis de propiedades desde URLs de Idealista/Fotocasa
- ✅ Visualización de rentabilidad, cashflow y OMR
- ✅ Generación de guion de negociación
- ✅ Descarga de informes PDF

## Build para Producción

```bash
npm run build
```

Los archivos compilados se generarán en `dist/`
