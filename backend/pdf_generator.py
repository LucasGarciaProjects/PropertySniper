from fpdf import FPDF
from models import RentabilityAnalysis, ExtractionLog
from typing import Optional
import os
import re
from datetime import datetime

class PDFGenerator:
    """Generador de informes PDF minimalista y profesional."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def safe_text(self, text: str) -> str:
        """Limpia caracteres para compatibilidad FPDF."""
        if not isinstance(text, str): text = str(text)
        return text.replace('€', 'EUR').replace('m²', 'm2').replace('²', '2')

    def clean_filename(self, text: str) -> str:
        street = text.split(',')[0] if ',' in text else text
        street = re.sub(r'[^\w\s-]', '', street)
        return re.sub(r'[-\s]+', '_', street)[:50]

    def generate_pdf(self, analysis: RentabilityAnalysis, extraction_log: Optional[ExtractionLog] = None) -> str:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # --- 1. TÍTULO MINIMALISTA ---
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(25, 25, 112) # Azul Medianoche
        pdf.cell(0, 10, "INFORME DE INVERSIÓN - LIBERTAD SNIPER AI", ln=1, align="L")
        
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, self.safe_text(f"Emitido el {datetime.now().strftime('%d/%m/%Y')}"), ln=1, align="L")
        pdf.ln(5)

        # --- 2. RESUMEN DE RENTABILIDAD ---
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, "RESUMEN EJECUTIVO", ln=1)
        
        # Fila de datos principales
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 8, self.safe_text(f"RENTABILIDAD NETA: {analysis.rentabilidad_neta:.2f}%"), border="B", ln=0)
        pdf.cell(60, 8, self.safe_text(f"CASHFLOW: {analysis.beneficio_neto_anual/12:,.0f} EUR/mes"), border="B", ln=0)
        pdf.cell(70, 8, self.safe_text(f"OMR (8%): {int(round(analysis.omr)):,} EUR"), border="B", ln=1)
        pdf.ln(5)

        # --- 3. TABLA DE DATOS (Compacta) ---
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(190, 8, " DESGLOSE DE LA OPERACIÓN", ln=1, fill=True)
        
        pdf.set_font("Arial", "", 9)
        data = [
            ("Precio de Venta", f"{analysis.precio_compra:,.0f} EUR"),
            ("Inversión Total (ITP + Gastos + Reforma)", f"{analysis.inversion_total:,.0f} EUR"),
            ("Alquiler Mensual Estimado", f"{analysis.alquiler_mensual:,.0f} EUR"),
            ("Gastos Fijos Anuales (20%)", f"{analysis.gastos_fijos_anuales:,.0f} EUR"),
            ("Beneficio Neto Anual", f"{analysis.beneficio_neto_anual:,.0f} EUR"),
            ("Ubicación", analysis.property_data.ubicacion)
        ]
        
        for label, val in data:
            pdf.set_font("Arial", "B", 9)
            pdf.cell(80, 7, self.safe_text(label), border="B", ln=0)
            pdf.set_font("Arial", "", 9)
            pdf.cell(110, 7, self.safe_text(val), border="B", ln=1, align="R")
        
        pdf.ln(10)

        # --- 4. CAJA OMR DESTACADA ---
        pdf.set_fill_color(255, 250, 230)
        pdf.set_draw_color(184, 134, 11)
        pdf.rect(10, pdf.get_y(), 190, 20, 'FD')
        pdf.set_xy(15, pdf.get_y() + 4)
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(130, 90, 0)
        pdf.cell(180, 5, "OFERTA MÁXIMA RECOMENDADA (OMR)", ln=1)
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(184, 134, 11)
        pdf.set_x(15)
        pdf.cell(180, 7, f"{int(round(analysis.omr)):,} EUR", ln=1)
        pdf.set_y(pdf.get_y() + 10)

        # --- 5. AUDITORÍA DE IA (Si existe) ---
        if extraction_log:
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(190, 8, " NOTAS DEL ANÁLISIS IA", ln=1, fill=True)
            pdf.set_font("Arial", "I", 8)
            pdf.multi_cell(190, 4, self.safe_text(extraction_log.reasoning))
            pdf.ln(5)

        # --- 6. METODOLOGÍA (Pie de página integrado) ---
        pdf.set_font("Arial", "", 7)
        pdf.set_text_color(120, 120, 120)
        ratio = analysis.alquiler_mensual / analysis.property_data.m2 if analysis.property_data.m2 > 0 else 0
        metodo = (f"Metodología: ITP(10%) + 3k EUR Gastos. Reforma: {analysis.coste_reforma:,.0f} EUR. "
                  f"Alquiler: {ratio:.1f} EUR/m2. Gastos fijos: 20%. Objetivo ROI: 8%.")
        pdf.multi_cell(0, 4, self.safe_text(metodo), align="C")

        # Guardar archivo
        street = self.clean_filename(analysis.property_data.ubicacion)
        filename = f"Sniper_{street}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)
        
        return filepath