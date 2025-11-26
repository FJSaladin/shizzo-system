# test_pdf.py
import sys
import os

# Asegurarse de que puede importar desde services
sys.path.insert(0, os.path.dirname(__file__))

from services.pdf_generator_reportlab import generar_pdf_con_datos

# Datos de prueba
datos_prueba = {
    "numero": "EST-1125-0001",
    "fecha_emision": "23/11/2025",
    "fecha_vencimiento": "23/12/2025",
    "vigencia_dias": 30,
    "cliente": {
        "nombre": "Repuestos La Solución",
        "rnc": "1-01-12345-6",
        "correo": "info@repuestos.com",
        "telefono": "(809) 555-1234",
        "direccion": "Av. Principal #123, Santo Domingo"
    },
    "descripcion": "Cotización para instalación eléctrica completa en oficinas corporativas. Incluye paneles, cableado estructurado y sistema de respaldo UPS.",
    "items": [
        {
            "alcance": "Instalación de panel eléctrico principal de 200A con breakers individuales por área",
            "monto": 75000.00
        },
        {
            "alcance": "Cableado estructurado completo para 50 puntos de red y 30 puntos eléctricos",
            "monto": 125000.00
        },
        {
            "alcance": "Sistema de respaldo UPS de 10KVA con banco de baterías",
            "monto": 95000.00
        }
    ],
    "terminos": [
        "La presente cotización tiene una vigencia de 30 días a partir de su emisión.",
        "Los precios incluyen ITBIS (18%).",
        "Forma de pago: 50% anticipo, 50% contra entrega.",
        "Tiempo de entrega: 15 días hábiles después de confirmado el pedido."
    ],
    "subtotal": 295000.00,
    "itbis": 53100.00,
    "total": 348100.00
}

if __name__ == "__main__":
    print("🔧 Generando PDF de prueba...")
    try:
        output_dir = "pdf_generados"
        os.makedirs(output_dir, exist_ok=True)
        ruta_salida = os.path.join(output_dir, "TEST_cotizacion.pdf")

        ruta = generar_pdf_con_datos(datos_prueba, ruta_salida)
        print(f"✅ PDF generado exitosamente: {ruta}")
        print("📄 Abre la carpeta pdf_generados/ para verlo")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()