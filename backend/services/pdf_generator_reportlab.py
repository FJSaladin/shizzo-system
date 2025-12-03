import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



def registrar_fuentes_century_gothic():
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    if not os.path.exists(font_dir):
        raise FileNotFoundError(f"No se encuentra la carpeta 'fonts'. Créala y coloca los 4 archivos .ttf de Century Gothic")

    pdfmetrics.registerFont(TTFont("CenturyGothic",       os.path.join(font_dir, "Gothic.ttf")))
    pdfmetrics.registerFont(TTFont("CenturyGothic-Bold",  os.path.join(font_dir, "GothicB.ttf")))
    pdfmetrics.registerFont(TTFont("CenturyGothic-Italic", os.path.join(font_dir, "GothicI.ttf")))
    pdfmetrics.registerFont(TTFont("CenturyGothic-BoldItalic", os.path.join(font_dir, "GothicBI.ttf")))

# ¡Se registra automáticamente al importar el módulo!
registrar_fuentes_century_gothic()

# ==============================================
# 2. CONFIGURACIÓN GENERAL
# ==============================================
CARPETA_POR_DEFECTO = "Cotizaciones"
os.makedirs(CARPETA_POR_DEFECTO, exist_ok=True)

COLOR_PRIMARIO = colors.HexColor("#141414")
COLOR_AMARILLO = colors.HexColor("#db901f")
COLOR_GRIS = colors.HexColor("#515151")
COLOR_GRIS_CLARO = colors.HexColor('#f8f8f8')

# ==============================================
# 3. FOOTER PERSONALIZADO (con Century Gothic)
# ==============================================
class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self.total_paginas = kwargs.pop('total_paginas', 1)
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for i, page in enumerate(self.pages):
            self.__dict__.update(page)
            es_ultima = (i == num_pages - 1)
            self.draw_footer(i + 1, num_pages, es_ultima)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_num, total_pages, es_ultima_pagina):
        self.saveState()

        # Imágenes del footer
        logo_mini_x = 10*mm
        logo_mini_y = 20*mm
        logo_mini_w = 20*mm
        logo_mini_h = 20*mm

        sello_w = 50*mm
        sello_h = 50*mm
        if es_ultima_pagina:
            sello_x = A4[0] - 70*mm
            sello_y = 20*mm
        else:
            sello_x = A4[0]/2 - 26.5*mm
            sello_y = 15*mm

        firma_x = A4[0]/2 - 60*mm
        firma_y = 5*mm
        firma_w = 120*mm
        firma_h = 50*mm

        try:
            logo_path = os.path.abspath('static/shizzologomini.jpeg')
            if os.path.exists(logo_path):
                self.drawImage(logo_path, logo_mini_x, logo_mini_y, width=logo_mini_w, height=logo_mini_h,
                               preserveAspectRatio=True, mask='auto')

            if es_ultima_pagina:
                firma_path = os.path.abspath('static/firmaDigitalJulioMundarai.jpeg')
                if os.path.exists(firma_path):
                    self.drawImage(firma_path, firma_x, firma_y, width=firma_w, height=firma_h,
                                   preserveAspectRatio=True, mask='auto')

            sello_path = os.path.abspath('static/shizzosello.jpeg')
            if os.path.exists(sello_path):
                self.drawImage(sello_path, sello_x, sello_y, width=sello_w, height=sello_h,
                               preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error cargando imágenes del footer: {e}")

        # Barra negra + texto con Century Gothic
        self.setFillColor(COLOR_PRIMARIO)
        self.rect(0, 0, A4[0], 15*mm, fill=True, stroke=False)
        self.setFillColor(COLOR_AMARILLO)
        self.rect(0, 15*mm, A4[0], 1.5*mm, fill=True, stroke=False)
        self.setFillColor(colors.white)
        

        self.setFont("CenturyGothic", 9)  # ¡Aquí usamos Century Gothic!

        self.drawString(15*mm, 7*mm, "C/ Huáscar Tejeda #9, Higüey, La Altagracia, República Dominicana")
        self.drawRightString(A4[0] - 15*mm, 7*mm, f"Página {page_num} / {total_pages}")

        self.restoreState()


# ==============================================
# 4. GENERADOR DEL PDF (todo con Century Gothic)
# ==============================================
class PDFGenerator:
    def __init__(self, datos):
        self.datos = datos
        self.width, self.height = A4
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _header(self, canvas, doc):
        logo_path = os.path.abspath('static/shizzoHeader.jpeg')
        if os.path.exists(logo_path):
            header_height = 37 * mm
            canvas.drawImage(logo_path, 0, A4[1] - header_height + 1*mm,
                             width=A4[0], height=header_height,
                             preserveAspectRatio=True, mask='auto')

    def _setup_styles(self):
        # Todos los estilos con Century Gothic
        self.styles.add(ParagraphStyle(name='TituloPrincipal',
                                       fontName='CenturyGothic-BoldItalic',
                                       fontSize=18,
                                       textColor=COLOR_PRIMARIO,
                                       alignment=TA_CENTER,
                                       spaceAfter=6*mm))

        self.styles.add(ParagraphStyle(name='Subtitulo',
                                       fontName='CenturyGothic-Bold',
                                       fontSize=13,
                                       textColor=COLOR_PRIMARIO,
                                       spaceAfter=4,
                                       textTransform='uppercase'))
        
        self.styles.add(ParagraphStyle(name='SubtituloCliente',
                                       fontName='CenturyGothic-Bold',
                                       fontSize=13,
                                       textColor=COLOR_PRIMARIO,
                                       spaceAfter=8,
                                       textTransform='uppercase'))
        
        self.styles.add(ParagraphStyle(name='SubtituloPago',
                                       fontName='CenturyGothic-Bold',
                                       fontSize=13,
                                       textColor=COLOR_PRIMARIO,
                                       spaceAfter=8,
                                       textTransform='uppercase',
                                       alignment=TA_RIGHT)
                                       )

        self.styles.add(ParagraphStyle(name='TextoNormal',
                                       fontName='CenturyGothic',
                                       fontSize=11,
                                       leading=14,
                                       alignment=TA_JUSTIFY))

        self.styles.add(ParagraphStyle(name='TextoPequeno',
                                       fontName='CenturyGothic-Italic',
                                       fontSize=10,
                                       textColor=COLOR_GRIS,
                                       alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='TextoCliente',
                                       fontName='CenturyGothic',
                                       fontSize=10,
                                       leading=12))

        self.styles.add(ParagraphStyle(name='TextoPago',
                                       fontName='CenturyGothic',
                                       fontSize=10,
                                       leading=12,
                                       alignment=TA_RIGHT))

        self.styles.add(ParagraphStyle(name='Termino',
                                       fontName='CenturyGothic',
                                       fontSize=11,
                                       leading=16,
                                       alignment=TA_JUSTIFY,
                                       spaceAfter=6))

        self.styles.add(ParagraphStyle(name='HeaderTable',
                                       fontName='CenturyGothic-Bold',
                                       fontSize=11,
                                       alignment=TA_CENTER,
                                       textColor=COLOR_PRIMARIO))

    # ====================== CONTENIDO ======================
    def _add_info_cotizacion(self):
        titulo = Paragraph("<b><i>COTIZACIÓN</i></b>", self.styles['TituloPrincipal'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 0*mm))

        num_style = ParagraphStyle('Num', fontName='CenturyGothic-Italic', fontSize=12, alignment=TA_CENTER)
        self.story.append(Paragraph(self.datos['numero'], num_style))
        self.story.append(Spacer(1, 1*mm))

        vig = f"Esta cotización cuenta con una vigencia de <b>{self.datos.get('vigencia_dias', 30)} días</b> a partir de su emisión"
        self.story.append(Paragraph(vig, self.styles['TextoPequeno']))
        self.story.append(Spacer(1, 1*mm))

        fecha_style = ParagraphStyle('Fecha', fontName='CenturyGothic-BoldItalic', fontSize=11, alignment=TA_CENTER)
        self.story.append(Paragraph(f"{self.datos['fecha_emision']} - {self.datos['fecha_vencimiento']}", fecha_style))
        self.story.append(Spacer(1, 12*mm))

    def _add_info_cliente_pago(self):
            cliente = self.datos['cliente']

            tit_cliente = Paragraph("<b>INFORMACIÓN DEL SOLICITANTE</b>", self.styles['SubtituloCliente'])
            tit_pago = Paragraph("<b>INFORMACIÓN DE PAGO</b>", self.styles['SubtituloPago'])
           
            

            data_cliente = [
                [tit_cliente],
                [Spacer(1, 2*mm)], # Espacio de 2mm (del paso anterior)
                [Paragraph(f"<b>Nombre:</b> {cliente['nombre']}", self.styles['TextoCliente'])],
                [Paragraph(f"<b>RNC:</b> {cliente.get('rnc', 'N/A')}", self.styles['TextoCliente'])],
                [Paragraph(f"<b>Correo:</b> {cliente.get('correo', 'N/A')}", self.styles['TextoCliente'])],
                [Paragraph(f"<b>Teléfono:</b> {cliente.get('telefono', 'N/A')}", self.styles['TextoCliente'])],
                [Paragraph(f"<b>Dirección:</b> {cliente.get('direccion', 'N/A')}", self.styles['TextoCliente'])]
            ]

            data_pago = [
                [tit_pago],
                [Spacer(1, 2*mm)], # Espacio de 2mm (del paso anterior)
                [Paragraph("<b>Moneda:</b> Peso Dominicano", self.styles['TextoPago'])],
                [Paragraph("<b>Método de pago:</b> Transferencia bancaria", self.styles['TextoPago'])],
                [Paragraph("Banco BHD: 38770920010 – SHIZZO GROUP", self.styles['TextoPago'])],
                [Paragraph("Banco Popular: 835902214 – Daniel A. Saladin", self.styles['TextoPago'])],
                [Paragraph("Banreservas: 9603583795 – Julio Leonardo Mundaray", self.styles['TextoPago'])]
            ]

            t_cliente = Table(data_cliente, colWidths=[95*mm])
            t_pago = Table(data_pago, colWidths=[84*mm])
            

            tabla_doble = Table([[t_cliente, t_pago]], colWidths=[105*mm, 89*mm])
            self.story.append(tabla_doble)
            self.story.append(Spacer(1, 8*mm))

    def _add_descripcion(self):
        if self.datos.get('descripcion'):
            self.story.append(Paragraph("<b>DESCRIPCIÓN</b>", self.styles['Subtitulo']))
            self.story.append(Spacer(1, 1*mm))
            self.story.append(Paragraph(self.datos['descripcion'], self.styles['TextoNormal']))
            self.story.append(Spacer(1, 4*mm))

    def _add_tabla_items(self):
        data = [[Paragraph("<b>ALCANCE</b>", self.styles['HeaderTable']),
                 Paragraph("<b>MONTO (DOP)</b>", self.styles['HeaderTable'])]]

        for item in self.datos.get('items', []):
            data.append([Paragraph(item['alcance'], self.styles['TextoNormal']),
                        Paragraph(f"DOP {item['monto']:,.2f}", self.styles['TextoNormal'])])

        tabla = Table(data, colWidths=[140*mm, 45*mm])
        tabla.setStyle(TableStyle([
            # Estilos para el encabezado (Fila 0):
            ('BACKGROUND', (0,0), (-1,0), COLOR_GRIS_CLARO),
            ('TEXTCOLOR', (0,0), (-1,0), COLOR_PRIMARIO),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'CenturyGothic-Bold'),
            ('TOPPADDING', (0,0), (-1,0), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,1), (-1,-1), 0.5, colors.lightgrey), 
            ('BOX', (0,1), (-1,-1), 1, colors.lightgrey), 
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        self.story.append(tabla)
        self.story.append(Spacer(1, 10*mm))

    def _add_totales(self):
            subtotal = self.datos.get('subtotal', 0)
            itbis = self.datos.get('itbis', 0)
            total = self.datos.get('total', 0)

            # Los estilos de alineación se pueden definir en los ParagraphStyle, pero usaremos el TableStyle
            # para aplicar la alineación a la derecha a las celdas donde va el texto.
            estilo_normal = ParagraphStyle('normal', fontName='CenturyGothic',  fontSize=11, alignment=TA_RIGHT)
            estilo_bold = ParagraphStyle('bold', fontName='CenturyGothic-Bold', fontSize=11, alignment=TA_RIGHT) 

            # Nota: Ya no necesitamos los estilos 'estilo_moneda' ni 'estilo_moneda_bold'

            data = [
                # Ahora solo tiene 2 columnas: [Etiqueta, Monto con DOP]
                [Paragraph('SUBTOTAL', estilo_normal), 
                Paragraph(f"DOP {subtotal:,.2f}", estilo_normal)], # <-- Volvemos a incluir 'DOP'
                
                [Paragraph('ITBIS (18%)', estilo_normal), 
                Paragraph(f"DOP {itbis:,.2f}", estilo_normal)], # <-- Volvemos a incluir 'DOP'
                
                [Paragraph('<b>TOTAL</b>', estilo_bold), 
                Paragraph(f"<b>DOP {total:,.2f}</b>", estilo_bold)], # <-- Volvemos a incluir 'DOP'
            ]
            
            # Ancho para 2 columnas (ejemplo: 50mm + 50mm = 100mm)
            # Queremos que la columna de monto (Col 1) sea dinámica pero la de etiqueta (Col 0) sea fija.
            # Ajustamos los anchos:
            tabla_totales = Table(data, colWidths=[30*mm, 45*mm]) # Ancho fijo para simplicidad
            
            tabla_totales.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,-1), 'RIGHT'), 
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            
            # PASO 1: Crear la tabla contenedora
            # Usamos 180mm como ancho para el contenedor y 100mm para el ancho de la tabla interna.
            cont = Table([[tabla_totales]], colWidths=[190*mm]) 
            
            # PASO 2: Aplicar alineación a la derecha a la tabla contenedora
            cont.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,0), 'RIGHT')
            ]))
            
            # PASO 3: Añadir el contenedor a la historia
            self.story.append(cont)

    def _add_terminos(self):
        if not self.datos.get('terminos'):
            return
        self.story.append(PageBreak())
        self.story.append(Paragraph("<b>TÉRMINOS Y CONDICIONES</b>", self.styles['Subtitulo']))
        self.story.append(Spacer(1, 8*mm))
        for i, t in enumerate(self.datos['terminos'], 1):
            self.story.append(Paragraph(f"<b>{i}.</b> {t}", self.styles['Termino']))
            self.story.append(Spacer(1, 3*mm))

    def generar(self, ruta_salida=None):
        if ruta_salida:
            ruta_final = ruta_salida
            os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        else:
            cliente = "".join(c for c in self.datos['cliente']['nombre'] if c.isalnum() or c in " -_").strip()
            fecha = self.datos['fecha_emision'].replace("/", "-")
            nombre = f"COT-{self.datos['numero']} {cliente} {fecha}.pdf"
            ruta_final = os.path.join(CARPETA_POR_DEFECTO, nombre)

        # Estimación de páginas (para el footer)
        items = len(self.datos.get('items', []))
        terminos = 1 if self.datos.get('terminos') else 0
        total_paginas = max(1, (items // 9) + 1) + terminos

        doc = SimpleDocTemplate(
            ruta_final,
            pagesize=A4,
            topMargin=40*mm,
            bottomMargin=40*mm,
            leftMargin=10*mm,
            rightMargin=10*mm
        )

        self._add_info_cotizacion()
        self._add_info_cliente_pago()
        self._add_descripcion()
        self._add_tabla_items()
        self._add_totales()
        self._add_terminos()

        doc.build(
            self.story,
            onFirstPage=self._header,
            onLaterPages=self._header,
            canvasmaker=lambda *a, **k: FooterCanvas(*a, total_paginas=total_paginas, **k)
        )

        print(f"PDF generado con Century Gothic → {ruta_final}")
        return ruta_final


# ==============================================
# FUNCIÓN PÚBLICA
# ==============================================
def generar_pdf_con_datos(datos, ruta_salida=None):
    gen = PDFGenerator(datos)
    return gen.generar(ruta_salida)