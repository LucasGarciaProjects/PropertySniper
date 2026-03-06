"""
Script de ejemplo para probar la API de Libertad Sniper AI.
Este archivo es solo para referencia y pruebas locales.
"""
import requests
import json

# URL de la API (ajustar según corresponda)
API_URL = "http://localhost:8000"

def test_analyze_property(url: str):
    """
    Prueba el endpoint de análisis de propiedades.
    
    Args:
        url: URL de una propiedad de Idealista o Fotocasa
    """
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json={"url": url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                analysis = data.get("analysis", {})
                print("✅ Análisis completado exitosamente")
                print(f"\n📊 Rentabilidad Neta: {analysis.get('rentabilidad_neta', 0):.2f}%")
                print(f"🚦 Semáforo: {analysis.get('semaforo', 'N/A')}")
                print(f"💰 Inversión Total: {analysis.get('inversion_total', 0):,.2f} €")
                print(f"📄 PDF generado: {data.get('pdf_path', 'N/A')}")
            else:
                print(f"❌ Error: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a la API. ¿Está el servidor corriendo?")
        print("   Ejecuta: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== Test de Libertad Sniper AI API ===\n")
    
    # Reemplazar con una URL real de Idealista o Fotocasa
    test_url = "https://www.idealista.com/inmueble/12345678/"
    
    print(f"Analizando propiedad: {test_url}\n")
    test_analyze_property(test_url)

