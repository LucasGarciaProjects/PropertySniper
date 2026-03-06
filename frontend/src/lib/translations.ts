
export const translations = {
  es: {
    header: {
      title: "LIBERTAD SNIPER AI",
      by: "Por",
    },
    tabs: {
      dashboard: "Dashboard",
      log: "Registro",
      sniper: "Sniper",
      coach: "Coach",
    },
    dashboard: {
      title: "Tu Salud Financiera",
      subtitle: "Resumen de tu patrimonio y flujo de caja.",
      totalIncome: "Ingresos Totales",
      totalExpenses: "Gastos Totales",
      savingsRate: "Tasa de Ahorro",
      savingsGoal: "Objetivo recomendado: 20%",
      incomeVsExpenses: "Ingresos vs Gastos",
      loading: "Cargando dashboard...",
    },
    log: {
      title: "Libro de Registro",
      subtitle: "Controla cada euro que entra y sale.",
      newTransaction: "Nuevo Movimiento",
      type: "Tipo",
      date: "Fecha",
      category: "Categoría",
      concept: "Concepto",
      amount: "Importe (€)",
      add: "Añadir",
      history: "Historial",
      loading: "Cargando...",
      noTransactions: "No hay movimientos registrados.",
      income: "Ingreso (+)",
      expense: "Gasto (-)",
      select: "Seleccionar",
      account: "Cuenta",
    },
    sniper: {
        title: "Sniper Inmobiliario",
        subtitle: "Analiza oportunidades de inversión.",
        analyze: "Analizar propiedad...",
        extract: "Extrayendo datos...",
        calculating: "Calculando rentabilidad...",
        ocr: "Funcionalidad de OCR próximamente. Por favor, usa la pestaña 'Pegar Texto'",
        addToProjections: "Añadir a mis proyecciones",
        added: "Añadido a tus proyecciones",
        error: "Error al guardar activo",
        analysisComplete: "Análisis completado",
        generatePdf: "Generando PDF...",
        downloadPdf: "PDF descargado correctamente",
        multiInput: {
            title: "Analiza cualquier inversión",
            titleAccent: "en segundos",
            subtitle: "Elige tu método preferido para analizar la propiedad",
            tabs: {
                text: "Pegar Texto",
                image: "Foto",
                manual: "Manual"
            },
            textTab: {
                title: "Pegar Texto del Anuncio",
                description: "Copia todo el contenido del anuncio (Ctrl+A, Ctrl+C) y pégalo aquí",
                placeholder: "Pega aquí todo el contenido del anuncio de Idealista, Fotocasa, etc. (Ctrl+A, Ctrl+C, Ctrl+V)",
                paste: "Pegar",
                analyze: "Analizar desde Texto",
                analyzing: "Analizando..."
            },
            imageTab: {
                title: "Subir Captura de Pantalla",
                description: "Sube una imagen del anuncio para análisis con OCR",
                drop: "Haz clic para subir",
                dropSuffix: "o arrastra la imagen aquí",
                selected: "Archivo seleccionado:",
                size: "Tamaño:",
                analyze: "Analizar Captura de Pantalla",
                analyzing: "Analizando imagen...",
                warning: "⚠️ Funcionalidad de OCR próximamente. Por ahora, usa la pestaña 'Pegar Texto'"
            },
            manualTab: {
                title: "Entrada Manual",
                description: "Introduce los datos manualmente usando los controles deslizantes",
                labels: {
                    price: "Precio de Venta",
                    m2: "Superficie (m²)",
                    rooms: "Habitaciones",
                    reform: "Coste Reforma (Opcional)",
                    rent: "Alquiler Mensual (Opcional)",
                    floor: "Planta",
                    status: "Estado",
                    location: "Ubicación"
                },
                placeholders: {
                    floor: "Ej: 3, baja, ático",
                    location: "Ciudad, barrio"
                },
                options: {
                    good: "Bueno",
                    reform: "A reformar",
                    excellent: "Excelente",
                    regular: "Regular"
                },
                auto: "Auto",
                calculated: "Auto (calculado)",
                estimated: "Auto (estimado)",
                analyze: "Analizar Propiedad",
                analyzing: "Analizando..."
            },
            results: {
                netYield: "Rentabilidad Neta",
                goal: "Objetivo: 8%+",
                aboveAverage: "Por encima de la media",
                estimatedRent: "Alquiler Estimado",
                editRent: "Editar alquiler",
                apply: "Aplicar",
                cancel: "Cancelar",
                monthlyCashflow: "Cashflow Mensual",
                positiveCashflow: "Cashflow Positivo",
                negativeCashflow: "Cashflow Negativo",
                maxOffer: "Oferta Máxima Recomendada",
                currentPrice: "Precio actual",
                discount: "Descuento del",
                negotiationScript: {
                    title: "Guion de Negociación",
                    subtitle: "Basado en puntos débiles detectados",
                    copy: "Copiar",
                    copied: "Copiado",
                    toast: "Guion copiado al portapapeles"
                },
                audit: {
                    title: "Auditoría de IA",
                    show: "Ver detalle del análisis técnico",
                    hide: "Ocultar detalle",
                    description: "Detalle de cómo la IA ha extraído y procesado los datos del anuncio",
                    complete: "Análisis completo: Todos los datos críticos encontrados",
                    incomplete: "Análisis incompleto: Faltan datos críticos",
                    found: "Campos encontrados directamente en el texto",
                    notFound: "No se encontraron campos directamente en el texto",
                    estimated: "Campos estimados o asumidos",
                    warnings: "Avisos Importantes",
                    reasoning: "Razonamiento de la IA",
                    reasoningPlaceholder: "El razonamiento de la IA aparecerá aquí..."
                },
                fields: {
                    price: "Precio de Venta",
                    m2: "Metros Cuadrados",
                    rooms: "Habitaciones",
                    floor: "Planta",
                    status: "Estado",
                    location: "Ubicación",
                    elevator: "Ascensor"
                }
            }
        }
    },
    coach: {
        title: "AI Financial Coach",
        subtitle: "Tu asesor personal 24/7.",
        greeting: "Hola, soy tu asesor financiero personal. He analizado tus ingresos y gastos. ¿En qué puedo ayudarte hoy?",
        placeholder: "Pregúntame sobre tus gastos, ahorros...",
        error: "Lo siento, tuve un problema al procesar tu consulta.",
    },
    footer: {
      copyright: "© 2026 Libertad Wealth App. Transformado por",
      role: "Tu Senior Fullstack Engineer"
    },
    categories: {
        income: ["Nómina", "Alquileres", "Inversiones", "Otros"],
        expense: ["Vivienda", "Alimentación", "Transporte", "Salud", "Ocio/Restaurantes", "Compras", "Suministros", "Otros"]
    }
  },
  en: {
    header: {
      title: "LIBERTAD SNIPER AI",
      by: "By",
    },
    tabs: {
      dashboard: "Dashboard",
      log: "Log",
      sniper: "Sniper",
      coach: "Coach",
    },
    dashboard: {
      title: "Your Financial Health",
      subtitle: "Summary of your wealth and cash flow.",
      totalIncome: "Total Income",
      totalExpenses: "Total Expenses",
      savingsRate: "Savings Rate",
      savingsGoal: "Recommended goal: 20%",
      incomeVsExpenses: "Income vs Expenses",
      loading: "Loading dashboard...",
    },
    log: {
      title: "Transaction Log",
      subtitle: "Track every euro that comes in and goes out.",
      newTransaction: "New Transaction",
      type: "Type",
      date: "Date",
      category: "Category",
      concept: "Concept",
      amount: "Amount (€)",
      add: "Add",
      history: "History",
      loading: "Loading...",
      noTransactions: "No transactions recorded.",
      income: "Income (+)",
      expense: "Expense (-)",
      select: "Select",
      account: "Account",
    },
    sniper: {
        title: "Real Estate Sniper",
        subtitle: "Analyze investment opportunities.",
        analyze: "Analyzing property...",
        extract: "Extracting data...",
        calculating: "Calculating profitability...",
        ocr: "OCR functionality coming soon. Please use the 'Paste Text' tab.",
        addToProjections: "Add to my projections",
        added: "Added to your projections",
        error: "Error saving asset",
        analysisComplete: "Analysis complete",
        generatePdf: "Generating PDF...",
        downloadPdf: "PDF downloaded successfully",
        multiInput: {
            title: "Analyze any investment",
            titleAccent: "in seconds",
            subtitle: "Choose your preferred method to analyze the property",
            tabs: {
                text: "Paste Text",
                image: "Photo",
                manual: "Manual"
            },
            textTab: {
                title: "Paste Ad Text",
                description: "Copy all the ad content (Ctrl+A, Ctrl+C) and paste it here",
                placeholder: "Paste here all the content of the ad from Idealista, Fotocasa, etc. (Ctrl+A, Ctrl+C, Ctrl+V)",
                paste: "Paste",
                analyze: "Analyze from Text",
                analyzing: "Analyzing..."
            },
            imageTab: {
                title: "Upload Screenshot",
                description: "Upload an image of the ad for OCR analysis",
                drop: "Click to upload",
                dropSuffix: "or drag the image here",
                selected: "Selected file:",
                size: "Size:",
                analyze: "Analyze Screenshot",
                analyzing: "Analyzing image...",
                warning: "⚠️ OCR functionality coming soon. For now, use the 'Paste Text' tab"
            },
            manualTab: {
                title: "Manual Entry",
                description: "Enter data manually using the sliders",
                labels: {
                    price: "Sale Price",
                    m2: "Surface (m²)",
                    rooms: "Rooms",
                    reform: "Reform Cost (Optional)",
                    rent: "Monthly Rent (Optional)",
                    floor: "Floor",
                    status: "Condition",
                    location: "Location"
                },
                placeholders: {
                    floor: "Ex: 3, ground floor, penthouse",
                    location: "City, neighborhood"
                },
                options: {
                    good: "Good",
                    reform: "To reform",
                    excellent: "Excellent",
                    regular: "Regular"
                },
                auto: "Auto",
                calculated: "Auto (calculated)",
                estimated: "Auto (estimated)",
                analyze: "Analyze Property",
                analyzing: "Analyzing..."
            },
            results: {
                netYield: "Net Yield",
                goal: "Goal: 8%+",
                aboveAverage: "Above Average",
                estimatedRent: "Estimated Rent",
                editRent: "Edit Rent",
                apply: "Apply",
                cancel: "Cancel",
                monthlyCashflow: "Monthly Cashflow",
                positiveCashflow: "Positive Cashflow",
                negativeCashflow: "Negative Cashflow",
                maxOffer: "Max Recommended Offer",
                currentPrice: "Current Price",
                discount: "Discount of",
                negotiationScript: {
                    title: "Negotiation Script",
                    subtitle: "Based on detected weak points",
                    copy: "Copy",
                    copied: "Copied",
                    toast: "Script copied to clipboard"
                },
                audit: {
                    title: "AI Audit",
                    show: "View technical analysis details",
                    hide: "Hide details",
                    description: "Details on how AI extracted and processed ad data",
                    complete: "Analysis complete: All critical data found",
                    incomplete: "Analysis incomplete: Critical data missing",
                    found: "Fields found directly in text",
                    notFound: "No fields found directly in text",
                    estimated: "Estimated or assumed fields",
                    warnings: "Important Warnings",
                    reasoning: "AI Reasoning",
                    reasoningPlaceholder: "AI reasoning will appear here..."
                },
                fields: {
                    price: "Sale Price",
                    m2: "Square Meters",
                    rooms: "Rooms",
                    floor: "Floor",
                    status: "Status",
                    location: "Location",
                    elevator: "Elevator"
                }
            }
        }
    },
    coach: {
        title: "AI Financial Coach",
        subtitle: "Your personal advisor 24/7.",
        greeting: "Hello, I am your personal financial advisor. I have analyzed your income and expenses. How can I help you today?",
        placeholder: "Ask me about your expenses, savings...",
        error: "Sorry, I had a problem processing your request.",
    },
    footer: {
      copyright: "© 2026 Liberty Wealth App. Transformed by",
      role: "Your Senior Fullstack Engineer"
    },
     categories: {
        income: ["Salary", "Rentals", "Investments", "Other"],
        expense: ["Housing", "Food", "Transport", "Health", "Leisure/Dining", "Shopping", "Utilities", "Other"]
    }
  }
};

export type Language = "es" | "en";
export type Translation = typeof translations.es;
