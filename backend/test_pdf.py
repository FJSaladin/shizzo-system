# test_pdf.py
import sys
import os

# Asegurarse de que puede importar desde services
sys.path.insert(0, os.path.dirname(__file__))

from services.pdf_generator_reportlab import generar_pdf_con_datos

# Datos de prueba
datos_prueba = {
    "numero": "COT-2025-045",
    "fecha_emision": "26/11/2025",
    "fecha_vencimiento": "10/12/2025",
    "vigencia_dias": 15,
    "cliente": {
        "nombre": "Ferretería El Progreso",
        "rnc": "1-09-45678-3",
        "correo": "ventas@ferreteriaelprogreso.com",
        "telefono": "(809) 555-6789",
        "direccion": "Calle Duarte #45, Santiago de los Caballeros"
    },
    "descripcion": (
        "Cotización para suministro e instalación de materiales eléctricos básicos en una pequeña oficina. "
        "Incluye lámparas LED, tomacorrientes, interruptores y cableado estándar."
    ),
    "items": [
        {
            "alcance": "Instalación de 20 lámparas LED de bajo consumo (18W) en áreas comunes",
            "monto": 28000.00
        },
        {
            "alcance": "Colocación de 40 tomacorrientes dobles con tapa de seguridad",
            "monto": 18000.00
        },
        {
            "alcance": "Instalación de 25 interruptores sencillos y 10 dobles",
            "monto": 12000.00
        },
        {
            "alcance": "Cableado eléctrico estándar para distribución en 5 oficinas y sala de reuniones",
            "monto": 35000.00
        }
    ],
    "terminos": [
        "La presente cotización tiene una vigencia de 15 días a partir de su emisión.",
        "Los precios incluyen ITBIS (18%).",
        "Forma de pago: 50% anticipo, 50% contra entrega.",
        "Tiempo estimado de instalación: 7 días hábiles después de confirmado el pedido."
    ],
    "subtotal": 93000.00,
    "itbis": 16740.00,
    "total": 109740.00
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