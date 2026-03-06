from fpdf import FPDF
from models import RentabilityAnalysis, ExtractionLog
from typing import Optional
import os
import re
from datetime import datetime


class PDFGenerator:
    """Generador de informes PDF estilo dossier bancario profesional."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Inicializa el generador de PDFs.
        
        Args:
            output_dir: Directorio donde se guardarán los PDFs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def get_semaforo_color(self, semaforo: str) -> tuple:
        """Retorna el color RGB según el semáforo."""
        colors = {
            "VERDE": (0, 150, 0),
            "AMARILLO": (255, 200, 0),
            "ROJO": (255, 0, 0)
        }
        return colors.get(semaforo, (128, 128, 128))
    
    def clean_filename(self, text: str) -> str:
        """Limpia un texto para usarlo como nombre de archivo."""
        # Extraer nombre de calle si está en la ubicación
        # Formato típico: "Ciudad, Calle" o "Calle, Ciudad"
        if ',' in text:
            parts = [p.strip() for p in text.split(',')]
            # Asumir que el nombre de la calle es el segundo elemento o el primero
            street = parts[1] if len(parts) > 1 else parts[0]
        else:
            street = text
        
        # Limpiar caracteres especiales
        street = re.sub(r'[^\w\s-]', '', street)
        street = re.sub(r'[-\s]+', '_', street)
        return street[:50]  # Limitar longitud
    
    def safe_text(self, text: str) -> str:
        """Reemplaza caracteres Unicode problemáticos por alternativas ASCII."""
        if not isinstance(text, str):
            text = str(text)
        # Reemplazar símbolo de euro (múltiples variantes)
        text = text.replace('€', 'EUR')
        text = text.replace('\u20AC', 'EUR')  # Código Unicode del euro
        # Reemplazar símbolo de metros cuadrados
        text = text.replace('m²', 'm2')
        text = text.replace('m\u00B2', 'm2')  # Unicode del superíndice 2
        text = text.replace('²', '2')
        text = text.replace('\u00B2', '2')  # Unicode del superíndice 2
        return text
    
    def draw_table_row(self, pdf: FPDF, label: str, value: str, width_label: float = 60, width_value: float = 130):
        """Dibuja una fila de tabla."""
        y = pdf.get_y()
        pdf.set_font("Arial", "B", 10)
        pdf.cell(width_label, 8, self.safe_text(label), border=1, ln=0, align="L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(width_value, 8, self.safe_text(value), border=1, ln=1, align="R")
    
    def draw_header(self, pdf: FPDF):
        """Dibuja el encabezado profesional del informe con diseño Deluxe."""
        # Azul Medianoche (RGB: 25, 25, 112)
        pdf.set_fill_color(25, 25, 112)
        pdf.rect(10, 10, 190, 30, 'F')
        
        # Título principal en blanco
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(10, 15)
        pdf.cell(190, 10, "DOSSIER DE INVERSION - LIBERTAD SNIPER AI", ln=1, align="C")
        
        # Fecha en gris claro
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(200, 200, 200)
        pdf.set_xy(10, 28)
        pdf.cell(190, 6, self.safe_text(f"Fecha de emision: {datetime.now().strftime('%d/%m/%Y %H:%M')}"), ln=1, align="C")
    
    def draw_footer(self, pdf: FPDF, include_formula: bool = False):
        """Dibuja el pie de página con número de página y opcionalmente la fórmula ultra-compacta."""
        page_height = pdf.h
        
        # Fórmula ultra-compacta solo en página 2, al final (una sola línea)
        if include_formula and pdf.page_no() == 2:
            # Fórmula en una sola línea ultra-compacta al final de la página
            pdf.set_xy(10, page_height - 10)
            pdf.set_font("Arial", "", 6)
            pdf.set_text_color(80, 80, 80)
            formula_text = self.safe_text("Rent. Neta = (Alq. Anual - Gastos Fijos) / Inv. Total x 100 | Gastos Fijos = 20% Alq. Anual | Inv. Total = Precio + ITP(10%) + Notaría(3.000EUR) + Reforma")
            pdf.cell(150, 3, formula_text, ln=0, align="L")
            
            # Página al lado
            pdf.set_font("Arial", "I", 7)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(40, 3, f"Página {pdf.page_no()}", ln=1, align="R")
        else:
            # Solo número de página
            pdf.set_xy(10, page_height - 10)
            pdf.set_font("Arial", "I", 7)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(190, 3, f"Página {pdf.page_no()}", ln=1, align="R")
    
    def draw_omr_box(self, pdf: FPDF, analysis: RentabilityAnalysis):
        """Dibuja una caja destacada para la OMR si es buena inversión."""
        is_good_investment = analysis.rentabilidad_neta >= 7.0
        
        # Eliminar comprobaciones manuales - dejar que auto_page_break maneje los saltos
        y_start = pdf.get_y()
        
        if is_good_investment:
            # Caja verde para buena inversión (más compacta)
            box_height = 22
            pdf.set_fill_color(230, 255, 230)
            pdf.set_draw_color(0, 150, 0)
            pdf.set_line_width(0.5)
            pdf.rect(10, y_start, 190, box_height, 'FD')
            
            # Título OMR
            pdf.set_xy(15, y_start + 4)
            pdf.set_font("Arial", "B", 11)
            pdf.set_text_color(0, 100, 0)
            pdf.cell(180, 5, self.safe_text("OFERTA MAXIMA RECOMENDADA (OMR)"), ln=0, align="L")
            
            # Valor OMR (Dorado suave)
            pdf.set_xy(15, y_start + 11)
            pdf.set_font("Arial", "B", 18)
            pdf.set_text_color(184, 134, 11)  # Dorado suave
            omr_formatted = f"{int(round(analysis.omr)):,} EUR"
            pdf.cell(180, 7, self.safe_text(omr_formatted), ln=0, align="L")
            
            # Descuento necesario (si aplica) - más compacto
            diferencia = analysis.precio_compra - analysis.omr
            if diferencia > 0:
                porcentaje = (diferencia / analysis.precio_compra * 100) if analysis.precio_compra > 0 else 0
                pdf.set_xy(15, y_start + 18)
                pdf.set_font("Arial", "", 9)
                pdf.set_text_color(0, 100, 0)
                pdf.cell(180, 3, self.safe_text(f"Descuento: {int(round(diferencia)):,} EUR ({porcentaje:.1f}%)"), ln=0, align="L")
            
            # Reposicionar cursor después de la caja
            pdf.set_y(y_start + box_height + 3)
            pdf.set_text_color(0, 0, 0)
        else:
            # Caja amarilla/roja para inversión no recomendada (más compacta)
            box_height = 18
            pdf.set_fill_color(255, 250, 230) if analysis.rentabilidad_neta >= 5.0 else pdf.set_fill_color(255, 230, 230)
            pdf.set_draw_color(255, 200, 0) if analysis.rentabilidad_neta >= 5.0 else pdf.set_draw_color(255, 0, 0)
            pdf.set_line_width(0.5)
            pdf.rect(10, y_start, 190, box_height, 'FD')
            
            # Título OMR
            pdf.set_xy(15, y_start + 4)
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(150, 100, 0) if analysis.rentabilidad_neta >= 5.0 else pdf.set_text_color(150, 0, 0)
            pdf.cell(180, 4, self.safe_text("OFERTA MAXIMA RECOMENDADA (OMR)"), ln=0, align="L")
            
            # Valor OMR (Dorado suave)
            pdf.set_xy(15, y_start + 11)
            pdf.set_font("Arial", "B", 15)
            pdf.set_text_color(184, 134, 11)  # Dorado suave
            omr_formatted = f"{int(round(analysis.omr)):,} EUR"
            pdf.cell(180, 5, self.safe_text(omr_formatted), ln=0, align="L")
            
            # Reposicionar cursor después de la caja
            pdf.set_y(y_start + box_height + 3)
            pdf.set_text_color(0, 0, 0)
    
    def draw_bar_chart(self, pdf: FPDF, precio_actual: float, omr: float, y_position: float):
        """Dibuja un gráfico de barras simple comparando precio actual vs OMR."""
        chart_width = 170
        chart_height = 32  # Reducido para ahorrar espacio
        chart_x = 20
        chart_y = y_position
        
        # Título del gráfico (más compacto)
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(25, 25, 112)  # Azul medianoche
        pdf.set_xy(chart_x, chart_y)
        pdf.cell(chart_width, 5, self.safe_text("Comparacion: Precio Actual vs OMR"), ln=1, align="L")
        
        chart_y += 6
        
        # Calcular escala
        max_value = max(precio_actual, omr)
        bar_max_width = chart_width - 60  # Dejar espacio para etiquetas
        
        # Dibujar fondo del gráfico
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.5)
        pdf.rect(chart_x, chart_y, chart_width, chart_height, 'D')
        
        # Barra Precio Actual (Azul) - más compacta
        bar1_width = (precio_actual / max_value) * bar_max_width
        pdf.set_fill_color(25, 25, 112)  # Azul medianoche
        pdf.rect(chart_x + 5, chart_y + 3, bar1_width, 10, 'F')
        
        # Barra OMR (Dorado) - más compacta
        bar2_width = (omr / max_value) * bar_max_width
        pdf.set_fill_color(184, 134, 11)  # Dorado suave
        pdf.rect(chart_x + 5, chart_y + 16, bar2_width, 10, 'F')
        
        # Etiquetas (formato sin decimales)
        pdf.set_font("Arial", "", 8)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(chart_x + bar_max_width + 10, chart_y + 5)
        pdf.cell(50, 5, self.safe_text(f"{int(round(precio_actual)):,} EUR"), ln=0, align="L")
        pdf.set_xy(chart_x + bar_max_width + 10, chart_y + 19)
        pdf.cell(50, 5, self.safe_text(f"{int(round(omr)):,} EUR"), ln=0, align="L")
        
        # Leyenda (más compacta)
        pdf.set_font("Arial", "I", 7)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(chart_x + 5, chart_y + chart_height + 2)
        pdf.cell(80, 3, self.safe_text("Precio Actual"), ln=0, align="L")
        pdf.set_xy(chart_x + 90, chart_y + chart_height + 2)
        pdf.cell(80, 3, self.safe_text("OMR (8% rentabilidad)"), ln=0, align="L")
        
        return chart_y + chart_height + 6
    
    def draw_audit_section(self, pdf: FPDF, extraction_log: Optional[ExtractionLog], y_start: float):
        """Dibuja la sección de auditoría de IA (versión compacta para ahorrar espacio)."""
        if not extraction_log:
            return y_start
        
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(25, 25, 112)  # Azul medianoche
        pdf.set_xy(10, y_start)
        pdf.cell(190, 6, self.safe_text("AUDITORIA DE IA"), ln=1, align="L")
        pdf.ln(2)
        
        # Campos encontrados (compacto, una línea)
        if extraction_log.found_fields:
            pdf.set_font("Arial", "B", 7)
            pdf.set_text_color(0, 150, 0)  # Verde
            pdf.cell(50, 3, self.safe_text("Encontrados: "), ln=0, align="L")
            pdf.set_font("Arial", "", 7)
            pdf.set_text_color(0, 0, 0)
            found_text = ", ".join(extraction_log.found_fields[:4])  # Limitar a 4 campos
            pdf.cell(140, 3, self.safe_text(found_text), ln=1, align="L")
        
        # Campos estimados (compacto, una línea)
        if extraction_log.missing_fields:
            pdf.set_font("Arial", "B", 7)
            pdf.set_text_color(255, 140, 0)  # Naranja
            pdf.cell(50, 3, self.safe_text("Estimados: "), ln=0, align="L")
            pdf.set_font("Arial", "", 7)
            pdf.set_text_color(0, 0, 0)
            missing_text = ", ".join(extraction_log.missing_fields[:4])  # Limitar a 4 campos
            pdf.cell(140, 3, self.safe_text(missing_text), ln=1, align="L")
        
        # Warnings (solo el primero, compacto)
        if extraction_log.warnings:
            pdf.set_font("Arial", "B", 7)
            pdf.set_text_color(255, 0, 0)  # Rojo
            pdf.cell(50, 3, self.safe_text("Aviso: "), ln=0, align="L")
            pdf.set_font("Arial", "", 7)
            pdf.set_text_color(0, 0, 0)
            warning_text = extraction_log.warnings[0][:70]  # Primer warning, limitado
            pdf.cell(140, 3, self.safe_text(warning_text), ln=1, align="L")
        
        # Razonamiento (resumido a 2 líneas máximo)
        if extraction_log.reasoning:
            pdf.set_font("Arial", "B", 7)
            pdf.set_text_color(25, 25, 112)  # Azul medianoche
            pdf.cell(190, 3, self.safe_text("Razonamiento: "), ln=1, align="L")
            pdf.set_font("Arial", "I", 6)
            pdf.set_text_color(0, 0, 0)
            # Limitar razonamiento a 150 caracteres para ahorrar espacio
            reasoning_short = extraction_log.reasoning[:150] + ("..." if len(extraction_log.reasoning) > 150 else "")
            pdf.multi_cell(190, 3, self.safe_text(reasoning_short), align="L", max_line_height=3)
        
        return pdf.get_y() + 2
    
    def generate_pdf(self, analysis: RentabilityAnalysis, extraction_log: Optional[ExtractionLog] = None) -> str:
        """
        Genera un PDF estilo dossier bancario con el análisis de rentabilidad.
        
        Args:
            analysis: Análisis de rentabilidad completo
            
        Returns:
            Ruta del archivo PDF generado
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)  # Margen menor para evitar saltos innecesarios
        pdf.set_margins(10, 35, 10)  # left, top, right
        
        # Página 1
        pdf.add_page()
        
        # Encabezado
        self.draw_header(pdf)
        
        # Título principal
        pdf.set_y(40)
        pdf.set_font("Arial", "B", 20)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, self.safe_text("ANÁLISIS DE RENTABILIDAD INMOBILIARIA"), ln=1, align="C")
        
        pdf.ln(5)
        
        # Semáforo y rentabilidad
        pdf.set_font("Arial", "B", 16)
        color = self.get_semaforo_color(analysis.semaforo)
        pdf.set_text_color(*color)
        pdf.cell(0, 8, self.safe_text(f"Estado: {analysis.semaforo} | Rentabilidad Neta: {analysis.rentabilidad_neta:.2f}%"), ln=1, align="C")
        pdf.set_text_color(0, 0, 0)
        
        pdf.ln(4)
        
        # TABLA 1: DATOS DEL INMUEBLE
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(190, 8, self.safe_text("DATOS DEL INMUEBLE"), ln=1, align="L", fill=True)
        pdf.ln(2)
        
        prop = analysis.property_data
        
        # Encabezado de tabla
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(250, 250, 250)
        pdf.cell(60, 8, "Concepto", border=1, ln=0, align="L", fill=True)
        pdf.cell(130, 8, "Valor", border=1, ln=1, align="R", fill=True)
        
        # Filas de datos
        self.draw_table_row(pdf, "Precio de venta", f"{prop.precio:,.2f} EUR")
        self.draw_table_row(pdf, "Superficie", f"{prop.m2:.2f} m2")
        self.draw_table_row(pdf, "Habitaciones", f"{prop.habitaciones if prop.habitaciones else 'N/A'}")
        self.draw_table_row(pdf, "Planta", f"{prop.planta if prop.planta else 'N/A'}")
        self.draw_table_row(pdf, "Estado", f"{prop.estado if prop.estado else 'N/A'}")
        self.draw_table_row(pdf, "Ubicación", f"{prop.ubicacion}")
        
        pdf.ln(4)
        
        # TABLA 2: ANÁLISIS FINANCIERO
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(190, 8, self.safe_text("ANÁLISIS FINANCIERO"), ln=1, align="L", fill=True)
        pdf.ln(2)
        
        # Encabezado de tabla
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(250, 250, 250)
        pdf.cell(60, 8, "Concepto", border=1, ln=0, align="L", fill=True)
        pdf.cell(130, 8, "Importe", border=1, ln=1, align="R", fill=True)
        
        # Inversión inicial
        self.draw_table_row(pdf, "Precio de compra", f"{analysis.precio_compra:,.2f} EUR")
        self.draw_table_row(pdf, "Gastos adquisicion (ITP 10%)", f"{analysis.gastos_adquisicion - 3000:,.2f} EUR")
        self.draw_table_row(pdf, "Notaria y gestoria", "3.000,00 EUR")
        self.draw_table_row(pdf, "Coste de reforma", f"{analysis.coste_reforma:,.2f} EUR")
        
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(60, 8, self.safe_text("TOTAL INVERSIÓN"), border=1, ln=0, align="L", fill=True)
        pdf.cell(130, 8, self.safe_text(f"{int(round(analysis.inversion_total)):,} EUR"), border=1, ln=1, align="R", fill=True)
        
        pdf.ln(3)
        
        # Proyección de ingresos
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, self.safe_text("PROYECCIÓN DE INGRESOS Y GASTOS"), ln=1, align="L")
        pdf.ln(2)
        
        # Encabezado de tabla
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(250, 250, 250)
        pdf.cell(60, 8, "Concepto", border=1, ln=0, align="L", fill=True)
        pdf.cell(130, 8, "Importe", border=1, ln=1, align="R", fill=True)
        
        self.draw_table_row(pdf, "Alquiler mensual estimado", f"{int(round(analysis.alquiler_mensual)):,} EUR")
        self.draw_table_row(pdf, "Alquiler anual", f"{int(round(analysis.alquiler_anual)):,} EUR")
        self.draw_table_row(pdf, "Gastos fijos anuales (20%)", f"{int(round(analysis.gastos_fijos_anuales)):,} EUR")
        
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(230, 255, 230)
        pdf.cell(60, 8, self.safe_text("BENEFICIO NETO ANUAL"), border=1, ln=0, align="L", fill=True)
        pdf.cell(130, 8, self.safe_text(f"{int(round(analysis.beneficio_neto_anual)):,} EUR"), border=1, ln=1, align="R", fill=True)
        
        # Eliminar todas las comprobaciones manuales - dejar que auto_page_break maneje los saltos
        pdf.ln(4)
        
        # Caja destacada OMR (compacta)
        self.draw_omr_box(pdf, analysis)
        
        pdf.ln(4)
        
        # Gráfico de barras: Precio Actual vs OMR (compacto)
        y_after_chart = self.draw_bar_chart(pdf, analysis.precio_compra, analysis.omr, pdf.get_y())
        pdf.set_y(y_after_chart)
        
        pdf.ln(4)
        
        # Sección de Auditoría de IA (si existe)
        if extraction_log:
            self.draw_audit_section(pdf, extraction_log, pdf.get_y())
        
        pdf.ln(4)
        
        # Método de cálculo (resumido y compacto)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 4, self.safe_text("METODOLOGÍA"), ln=1, align="L")
        pdf.set_font("Arial", "", 7)
        
        # Calcular ratio de alquiler usado - SIEMPRE usar ratio_texto dinámico
        ratio_alquiler = analysis.alquiler_mensual / prop.m2 if prop.m2 > 0 else 0
        ubicacion_metodologia = prop.ubicacion or "la zona"
        
        # Determinar si es Madrid/Barcelona u otra zona
        ubicacion_lower = ubicacion_metodologia.lower()
        if "madrid" in ubicacion_lower:
            ratio_texto = "20EUR/m2 para Madrid"
        elif "barcelona" in ubicacion_lower:
            ratio_texto = "20EUR/m2 para Barcelona"
        else:
            ratio_texto = f"{int(round(ratio_alquiler))}EUR/m2 para {ubicacion_metodologia}"
        
        # Asegurar que ratio_texto se use SIEMPRE - eliminar cualquier referencia a 6-8EUR/m2
        metodologia_text = self.safe_text(
            f"Este análisis utiliza el método de Libertad Inmobiliaria de Carlos Galán. "
            f"Los gastos de adquisición incluyen ITP (10%) y notaría/gestoría (3.000EUR). "
            f"La reforma se estima en 400EUR/m2 si está 'a reformar' o 50EUR/m2 si está 'bueno'. "
            f"El alquiler se estima mediante un análisis de mercado de la zona (en este caso, {ratio_texto}). "
            f"Los gastos fijos representan el 20% del alquiler anual."
        )
        pdf.multi_cell(0, 3, metodologia_text)
        
        pdf.ln(2)
        
        # URL origen (compacto)
        pdf.set_font("Arial", "I", 6)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 2, self.safe_text(f"Fuente: {prop.url_origen}"), ln=1, align="L")
        
        # Pie de página con fórmula solo en página 2
        is_page_2 = pdf.page_no() == 2
        self.draw_footer(pdf, include_formula=is_page_2)
        
        # Generar nombre de archivo con nombre de calle
        street_name = self.clean_filename(prop.ubicacion) if prop.ubicacion else "Propiedad"
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"Analisis_Sniper_{street_name}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Guardar PDF
        pdf.output(filepath)
        
        return filepath
