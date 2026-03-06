from models import PropertyData, RentabilityAnalysis
from typing import Optional


class RentabilityCalculator:
    """
    Calculadora de rentabilidad basada en el método de Libertad Inmobiliaria de Carlos Galán.
    """
    
    # Constantes del método
    ITP_PERCENTAGE = 0.10  # 10% ITP
    GASTOS_NOTARIA = 3000  # 3000€ notaría/gestoría
    REFORMA_A_REFORMAR = 400  # €/m2
    REFORMA_BUENO = 50  # €/m2
    GASTOS_FIJOS_PERCENTAGE = 0.20  # 20% de gastos fijos sobre alquiler
    RENTABILIDAD_VERDE = 0.07  # > 7%
    RENTABILIDAD_AMARILLO = 0.05  # 5% - 7%
    RENTABILIDAD_OBJETIVO_OMR = 0.08  # 8% para OMR
    
    def __init__(self, precio_medio_alquiler_zona: Optional[float] = None):
        """
        Inicializa la calculadora.
        
        Args:
            precio_medio_alquiler_zona: Precio medio de alquiler por m2 en la zona.
                                       Si no se proporciona, se usa un ratio de 6-8€/m2.
        """
        self.precio_medio_alquiler_zona = precio_medio_alquiler_zona
    
    def calculate_alquiler_mensual(self, m2: float, ubicacion: Optional[str] = None, alquiler_estimado_llm: Optional[float] = None) -> float:
        """
        Calcula el alquiler mensual estimado.
        
        Prioridad:
        1. Si el LLM proporcionó una estimación, usarla
        2. Si hay ubicación, estimar basado en la zona (Madrid/Barcelona: 18-22€/m², otras: 12-14€/m²)
        3. Si hay precio medio de zona configurado, usarlo
        4. Por defecto: 7€/m2 (promedio conservador)
        
        Args:
            m2: Metros cuadrados
            ubicacion: Ubicación de la propiedad (para estimar según zona)
            alquiler_estimado_llm: Alquiler estimado por el LLM (si está disponible)
        """
        # Prioridad 1: Usar estimación del LLM si está disponible
        if alquiler_estimado_llm and alquiler_estimado_llm > 0:
            return alquiler_estimado_llm
        
        # Prioridad 2: Estimar basado en ubicación
        if ubicacion:
            ubicacion_lower = ubicacion.lower()
            # Capitales principales: Madrid, Barcelona
            if any(city in ubicacion_lower for city in ["madrid", "barcelona"]):
                # Ratio conservador para capitales: 18-22€/m² (usamos 20€/m² como promedio)
                precio_por_m2 = 20.0
            else:
                # Otras zonas: 12-14€/m² (usamos 13€/m² como promedio)
                precio_por_m2 = 13.0
            return m2 * precio_por_m2
        
        # Prioridad 3: Usar precio medio de zona si está configurado
        if self.precio_medio_alquiler_zona:
            precio_por_m2 = self.precio_medio_alquiler_zona
        else:
            # Por defecto: ratio conservador de 7€/m2
            precio_por_m2 = 7.0
        
        return m2 * precio_por_m2
    
    def calculate_gastos_adquisicion(self, precio: float) -> float:
        """Calcula los gastos de adquisición (ITP + notaría/gestoría)."""
        itp = precio * self.ITP_PERCENTAGE
        return itp + self.GASTOS_NOTARIA
    
    def calculate_coste_reforma(self, m2: float, estado: str) -> float:
        """
        Calcula el coste de reforma según el estado del inmueble.
        
        Args:
            m2: Metros cuadrados
            estado: Estado del inmueble ('a reformar', 'bueno', 'regular')
        """
        estado_lower = estado.lower()
        
        if 'reformar' in estado_lower or 'reform' in estado_lower or 'fix' in estado_lower:
            return m2 * self.REFORMA_A_REFORMAR
        elif 'bueno' in estado_lower or 'good' in estado_lower or 'excelente' in estado_lower or 'excellent' in estado_lower or 'nuevo' in estado_lower or 'new' in estado_lower:
            return m2 * self.REFORMA_BUENO
        else:
            # Para estados intermedios, usar un promedio
            return m2 * ((self.REFORMA_A_REFORMAR + self.REFORMA_BUENO) / 2)
    
    def calculate_rentability(self, property_data: PropertyData) -> RentabilityAnalysis:
        """
        Calcula la rentabilidad completa de una propiedad.
        
        Args:
            property_data: Datos de la propiedad extraídos del scraper
            
        Returns:
            RentabilityAnalysis con todos los cálculos
        """
        precio_compra = property_data.precio
        m2 = property_data.m2
        estado = property_data.estado or 'bueno'
        
        # Calcular gastos de adquisición
        gastos_adquisicion = self.calculate_gastos_adquisicion(precio_compra)
        
        # Calcular coste de reforma
        coste_reforma = self.calculate_coste_reforma(m2, estado)
        
        # Inversión total
        inversion_total = precio_compra + gastos_adquisicion + coste_reforma
        
        # Calcular alquiler (usando estimación del LLM si está disponible, o estimando por ubicación)
        alquiler_mensual = self.calculate_alquiler_mensual(
            m2, 
            ubicacion=property_data.ubicacion,
            alquiler_estimado_llm=property_data.alquiler_mensual_estimado
        )
        alquiler_anual = alquiler_mensual * 12
        
        # Gastos fijos anuales (20% del alquiler anual)
        gastos_fijos_anuales = alquiler_anual * self.GASTOS_FIJOS_PERCENTAGE
        
        # Beneficio neto anual
        beneficio_neto_anual = alquiler_anual - gastos_fijos_anuales
        
        # Rentabilidad neta
        rentabilidad_neta = (beneficio_neto_anual / inversion_total) * 100
        
        # Determinar semáforo
        if rentabilidad_neta >= self.RENTABILIDAD_VERDE * 100:
            semaforo = "GREEN"
        elif rentabilidad_neta >= self.RENTABILIDAD_AMARILLO * 100:
            semaforo = "YELLOW"
        else:
            semaforo = "RED"
        
        # Calcular Oferta Máxima Recomendada (OMR)
        omr = self.calculate_omr(property_data)
        
        return RentabilityAnalysis(
            precio_compra=precio_compra,
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
            property_data=property_data
        )
    
    def calculate_omr(self, property_data: PropertyData) -> float:
        """
        Calcula la Oferta Máxima Recomendada (OMR).
        La OMR es el precio de compra necesario para que la rentabilidad neta sea exactamente del 8%.
        Esta es la oferta que Carlos usará para negociar con el vendedor.
        
        Fórmula:
        - Rentabilidad objetivo = 8% = (Alquiler anual - Gastos fijos) / Inversión total
        - Inversión total necesaria = (Alquiler anual - Gastos fijos) / 0.08
        - Inversión total = Precio compra + Gastos adquisición + Coste reforma
        - Gastos adquisición = 10% * Precio compra + 3.000€
        - Por lo tanto: Precio compra = (Inversión total - 3.000 - Coste reforma) / 1.10
        
        Args:
            property_data: Datos de la propiedad extraídos del scraper
            
        Returns:
            Oferta Máxima Recomendada (precio de compra en euros)
        """
        m2 = property_data.m2
        estado = property_data.estado or 'bueno'
        
        # Calcular coste de reforma (independiente del precio de compra)
        coste_reforma = self.calculate_coste_reforma(m2, estado)
        
        # Calcular alquiler anual (independiente del precio de compra)
        alquiler_mensual = self.calculate_alquiler_mensual(
            m2,
            ubicacion=property_data.ubicacion,
            alquiler_estimado_llm=property_data.alquiler_mensual_estimado
        )
        alquiler_anual = alquiler_mensual * 12
        
        # Gastos fijos anuales (20% del alquiler anual)
        gastos_fijos_anuales = alquiler_anual * self.GASTOS_FIJOS_PERCENTAGE
        
        # Beneficio neto anual
        beneficio_neto_anual = alquiler_anual - gastos_fijos_anuales
        
        # Calcular la inversión total necesaria para obtener 8% de rentabilidad
        # Rentabilidad = Beneficio neto / Inversión total
        # 0.08 = Beneficio neto / Inversión total
        # Inversión total = Beneficio neto / 0.08
        inversion_total_necesaria = beneficio_neto_anual / self.RENTABILIDAD_OBJETIVO_OMR
        
        # Calcular el precio de compra necesario
        # Inversión total = Precio compra + Gastos adquisición + Coste reforma
        # Inversión total = Precio compra + (0.10 * Precio compra + 3.000) + Coste reforma
        # Inversión total = Precio compra * 1.10 + 3.000 + Coste reforma
        # Precio compra = (Inversión total - 3.000 - Coste reforma) / 1.10
        omr = (inversion_total_necesaria - self.GASTOS_NOTARIA - coste_reforma) / (1 + self.ITP_PERCENTAGE)
        
        # Asegurar que la OMR no sea negativa
        return max(0, omr)

