import asyncio
import os
from jinja2 import Environment, FileSystemLoader
from pyppeteer import launch
from datetime import datetime

# Carpeta por defecto para PDFs
CARPETA_POR_DEFECTO = "Cotizaciones"
os.makedirs(CARPETA_POR_DEFECTO, exist_ok=True)

async def generar_pdf_con_datos(datos, ruta_salida=None):
    """
    Genera un PDF a partir de datos de cotización
    
    Args:
        datos: Diccionario con la información de la cotización
        ruta_salida: Ruta donde guardar el PDF (opcional)
    
    Returns:
        str: Ruta del PDF generado
    """
    
    # === CÁLCULOS ===
    subtotal = datos.get("subtotal", 0)
    itbis = datos.get("itbis", 0)
    total = datos.get("total", 0)
    
    # === CONTAR LÍNEAS ===
    def contar_lineas(texto: str) -> int:
        lineas = len(texto.split('\n'))
        lineas += len(texto) // 90
        return max(1, lineas)
    
    # === PAGINACIÓN DE ÍTEMS ===
    MAX_LINEAS_PRIMERA = 20
    MAX_LINEAS_RESTO = 33
    paginas_items = []
    pagina_actual = []
    lineas_actual = 0
    es_primera_pagina = True

    for item in datos.get("items", []):
        lineas_item = contar_lineas(item["alcance"])
        limite = MAX_LINEAS_PRIMERA if es_primera_pagina else MAX_LINEAS_RESTO
        
        if lineas_actual + lineas_item > limite and pagina_actual:
            paginas_items.append(pagina_actual)
            pagina_actual = []
            lineas_actual = 0
            es_primera_pagina = False
        
        pagina_actual.append(item)
        lineas_actual += lineas_item
    
    if pagina_actual:
        paginas_items.append(pagina_actual)

    # === DIVIDIR TÉRMINOS EN LÍNEAS ===
    def dividir_termino_en_lineas(texto: str, max_caracteres_por_linea=85) -> list:
        palabras = texto.split()
        lineas = []
        linea_actual = ""
        
        for palabra in palabras:
            if len(linea_actual) + len(palabra) + 1 <= max_caracteres_por_linea:
                linea_actual += (" " if linea_actual else "") + palabra
            else:
                lineas.append(linea_actual)
                linea_actual = palabra
        
        if linea_actual:
            lineas.append(linea_actual)
        
        return lineas

    # === PAGINACIÓN DE TÉRMINOS ===
    MAX_LINEAS_TERMINOS = 47
    paginas_terminos = []
    pagina_actual_terminos = []
    lineas_actual_terminos = 0
    indice_termino = 1

    for termino in datos.get("terminos", []):
        lineas_termino = dividir_termino_en_lineas(termino)
        es_continuacion = False
        
        while lineas_termino:
            espacio_disponible = MAX_LINEAS_TERMINOS - lineas_actual_terminos
            fragmento = lineas_termino[:espacio_disponible]
            lineas_termino = lineas_termino[espacio_disponible:]

            if fragmento:
                pagina_actual_terminos.append({
                    "texto": "\n".join(fragmento),
                    "indice": indice_termino if not es_continuacion else None
                })
                lineas_actual_terminos += len(fragmento)

            if lineas_actual_terminos >= MAX_LINEAS_TERMINOS:
                paginas_terminos.append(pagina_actual_terminos)
                pagina_actual_terminos = []
                lineas_actual_terminos = 0
                es_continuacion = True

        indice_termino += 1

    if pagina_actual_terminos:
        paginas_terminos.append(pagina_actual_terminos)

    # === FORMATO MONEDA ===
    def format_currency(value):
        return "{:,.2f}".format(value)

    # === RENDERIZAR ===
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters['currency'] = format_currency
    
    paginas_html = []
    total_paginas_cotizacion = len(paginas_items)
    total_paginas_terminos = len(paginas_terminos)
    total_paginas_documento = total_paginas_cotizacion + total_paginas_terminos

    # Renderizar páginas de items
    for idx, items in enumerate(paginas_items, 1):
        es_primera = idx == 1
        es_ultima = idx == total_paginas_cotizacion
        
        context = {
            "items": items,
            "es_primera_pagina": es_primera,
            "es_ultima_pagina": es_ultima,
            "pagina_num": idx,
            "total_paginas": total_paginas_documento,
            "numero": datos["numero"],
            "fecha_emision": datos["fecha_emision"],
            "fecha_vencimiento": datos["fecha_vencimiento"],
            "cliente": datos["cliente"],
            "descripcion": datos.get("descripcion", ""),
            "subtotal": subtotal,
            "itbis": itbis,
            "total": total,
            "vigencia_dias": datos.get("vigencia_dias", 30)
        }
        
        html_pagina = env.get_template('cotizacion.html').render(**context)
        paginas_html.append(html_pagina)

    # Renderizar páginas de términos
    for idx, terminos_pagina in enumerate(paginas_terminos, 1):
        es_ultima_terminos = idx == total_paginas_terminos
        
        context_terminos = {
            "terminos": terminos_pagina,
            "pagina_num": total_paginas_cotizacion + idx,
            "total_paginas": total_paginas_documento,
            "es_ultima_pagina": es_ultima_terminos,
        }
        
        html_termino = env.get_template('terminos.html').render(**context_terminos)
        paginas_html.append(html_termino)

    # === HTML COMPLETO ===
    html_completo = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="style.css">
    </head>
    <body>
    <div class="container">
        {''.join(paginas_html)}
    </div>
    </body>
    </html>
    """
    
    # Guardar HTML temporal
    temp_path = "temp_completo.html"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(html_completo)

    # === NOMBRE DEL PDF ===
    cliente = datos["cliente"]["nombre"].strip()
    fecha = datos["fecha_emision"].replace("/", "-")
    cliente_limpio = "".join(c for c in cliente if c.isalnum() or c in " -_").rstrip()
    nombre_pdf = f"COT-{datos['numero']} {cliente_limpio} {fecha}.pdf"

    # === RUTA FINAL ===
    if ruta_salida:
        ruta_final = ruta_salida
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    else:
        ruta_final = os.path.join(CARPETA_POR_DEFECTO, nombre_pdf)

    # === GENERAR PDF ===
    browser = await launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security'],
        handleSIGINT=False, 
        handleSIGTERM=False, 
        handleSIGHUP=False
    )
    
    page = await browser.newPage()
    await page.goto(f"file://{os.path.abspath(temp_path)}", waitUntil='networkidle0')
    await page.pdf(
        path=ruta_final,
        format='A4',
        printBackground=True,
        margin={'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
    )
    
    await browser.close()
    os.remove(temp_path)

    print(f"✅ PDF generado: {ruta_final}")
    return ruta_final