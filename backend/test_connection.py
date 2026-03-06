"""
Script de prueba para verificar la conexión con la API de Libertad Sniper AI.
Este script hace una petición real al endpoint /analyze y muestra los resultados.
"""

import requests
import json
import sys
from datetime import datetime

# Configuración
# NOTA: El backend debe estar corriendo en el puerto 8000
# Ejecuta: uvicorn main:app --reload
API_URL = "http://localhost:8000"
ENDPOINT_ANALYZE = f"{API_URL}/analyze"
ENDPOINT_HEALTH = f"{API_URL}/health"

# URL de ejemplo de Idealista (puedes cambiarla por una URL real)
# Ejemplo: https://www.idealista.com/inmueble/12345678/
TEST_URL = "https://www.idealista.com/inmueble/12345678/"


def print_section(title: str):
    """Imprime un separador visual para las secciones."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health_check():
    """Verifica que el servidor esté funcionando."""
    print_section("1. VERIFICANDO SALUD DEL SERVIDOR")
    try:
        response = requests.get(ENDPOINT_HEALTH, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor activo: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Error: Código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print(f"   Asegúrate de que el servidor esté corriendo en {API_URL}")
        print("   Ejecuta: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False


def test_analyze_property(url: str):
    """Hace una petición de análisis a la API."""
    print_section("2. ANALIZANDO PROPIEDAD")
    print(f"URL: {url}")
    print("Enviando petición...")
    
    try:
        response = requests.post(
            ENDPOINT_ANALYZE,
            json={"url": url},
            headers={"Content-Type": "application/json"},
            timeout=30  # Timeout más largo para scraping
        )
        
        print(f"\n📡 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Mensaje: {error_data.get('error', 'Error desconocido')}")
            except:
                print(f"   Respuesta: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout - El servidor tardó demasiado en responder")
        print("   Esto puede ser normal si Firecrawl está procesando la URL")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return None


def print_analysis_results(data: dict):
    """Imprime los resultados del análisis de forma legible."""
    if not data:
        return
    
    print_section("3. RESULTADOS DEL ANÁLISIS")
    
    if not data.get("success"):
        print("❌ El análisis falló")
        print(f"   Error: {data.get('error', 'Error desconocido')}")
        return
    
    analysis = data.get("analysis")
    if not analysis:
        print("❌ No se encontraron datos de análisis en la respuesta")
        return
    
    # Información de la propiedad
    property_data = analysis.get("property_data", {})
    print("\n📋 INFORMACIÓN DE LA PROPIEDAD:")
    print(f"   Precio: {property_data.get('precio', 0):,.0f} €")
    print(f"   Superficie: {property_data.get('m2', 0):.2f} m²")
    print(f"   Habitaciones: {property_data.get('habitaciones', 'N/A')}")
    print(f"   Planta: {property_data.get('planta', 'N/A')}")
    print(f"   Estado: {property_data.get('estado', 'N/A')}")
    print(f"   Ubicación: {property_data.get('ubicacion', 'N/A')}")
    
    # Análisis financiero
    print("\n💰 ANÁLISIS FINANCIERO:")
    print(f"   Precio de compra: {analysis.get('precio_compra', 0):,.2f} €")
    print(f"   Gastos de adquisición: {analysis.get('gastos_adquisicion', 0):,.2f} €")
    print(f"   Coste de reforma: {analysis.get('coste_reforma', 0):,.2f} €")
    print(f"   Inversión total: {analysis.get('inversion_total', 0):,.2f} €")
    
    # Proyección
    print("\n📊 PROYECCIÓN:")
    print(f"   Alquiler mensual: {analysis.get('alquiler_mensual', 0):,.2f} €")
    print(f"   Alquiler anual: {analysis.get('alquiler_anual', 0):,.2f} €")
    print(f"   Gastos fijos anuales: {analysis.get('gastos_fijos_anuales', 0):,.2f} €")
    print(f"   Beneficio neto anual: {analysis.get('beneficio_neto_anual', 0):,.2f} €")
    
    # Rentabilidad
    rentabilidad = analysis.get('rentabilidad_neta', 0)
    semaforo = analysis.get('semaforo', 'N/A')
    omr = analysis.get('omr', 0)
    
    print("\n🎯 RENTABILIDAD:")
    print(f"   Rentabilidad neta: {rentabilidad:.2f}%")
    print(f"   Semáforo: {semaforo}")
    
    # OMR
    print("\n💎 OFERTA MÁXIMA RECOMENDADA (OMR):")
    print(f"   OMR: {omr:,.2f} €")
    precio_compra = analysis.get('precio_compra', 0)
    if precio_compra > 0:
        descuento = ((precio_compra - omr) / precio_compra * 100)
        print(f"   Descuento necesario: {descuento:.2f}%")
        print(f"   Diferencia: {precio_compra - omr:,.2f} €")
    
    # PDF
    pdf_path = data.get('pdf_path')
    if pdf_path:
        print(f"\n📄 PDF generado: {pdf_path}")
    
    # JSON completo
    print_section("4. RESPUESTA JSON COMPLETA")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    """Función principal del script de prueba."""
    print("\n" + "=" * 60)
    print("  TEST DE CONEXIÓN - LIBERTAD SNIPER AI")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {API_URL}")
    
    # 1. Verificar salud del servidor
    if not test_health_check():
        print("\n❌ No se puede continuar. El servidor no está disponible.")
        sys.exit(1)
    
    # 2. Obtener URL de prueba
    test_url = TEST_URL
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        print(f"\n📝 Usando URL proporcionada: {test_url}")
    else:
        print(f"\n📝 Usando URL de ejemplo: {test_url}")
        print("   Puedes proporcionar una URL real como argumento:")
        print("   python test_connection.py 'https://www.idealista.com/inmueble/...'")
    
    # 3. Analizar propiedad
    result = test_analyze_property(test_url)
    
    # 4. Mostrar resultados
    if result:
        print_analysis_results(result)
        print_section("✅ TEST COMPLETADO")
        print("El análisis se completó correctamente.")
    else:
        print_section("❌ TEST FALLIDO")
        print("No se pudo completar el análisis.")
        sys.exit(1)


if __name__ == "__main__":
    main()

