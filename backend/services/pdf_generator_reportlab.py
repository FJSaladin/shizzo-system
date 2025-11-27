import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime

# Carpeta por defecto para PDFs
CARPETA_POR_DEFECTO = "Cotizaciones"
os.makedirs(CARPETA_POR_DEFECTO, exist_ok=True)

# Colores SHIZZO
COLOR_PRIMARIO = colors.HexColor('#222222')
COLOR_AMARILLO = colors.HexColor('#eebe22')
COLOR_GRIS = colors.HexColor("#515151")
COLOR_GRIS_CLARO = colors.HexColor('#f8f8f8')

class FooterCanvas(canvas.Canvas):
    """Canvas personalizado para agregar footer en cada página"""
    
    def __init__(self, *args, **kwargs):
        self.total_paginas = kwargs.pop('total_paginas', 1)
        self.es_ultima_pagina_cotizacion = kwargs.pop('es_ultima_pagina_cotizacion', False)
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        num_pages = len(self.pages)
        for i, page in enumerate(self.pages):
            self.__dict__.update(page)
            # La última página es especial (tiene firma)
            es_ultima = (i == num_pages - 1)
            self.draw_footer(i + 1, num_pages, es_ultima)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_footer(self, page_num, total_pages, es_ultima_pagina):
        """Dibujar footer en cada página"""
        self.saveState()
        
        # === ÁREA SUPERIOR AL FOOTER (para imágenes) ===
        
        # Logo mini (siempre en la izquierda)
        logo_mini_x = 5*mm
        logo_mini_y = 15*mm
        logo_mini_width = 20*mm
        logo_mini_height = 20*mm
        
        # Sello digital - POSICIÓN DIFERENTE según página
        if es_ultima_pagina:
            # Última página: sello a la DERECHA
            sello_x = A4[0] - 70*mm
            sello_y = 20*mm
        else:
            # Páginas normales: sello al CENTRO
            sello_x = A4[0] / 2 - 26.5*mm  # Centrado
            sello_y = 10*mm
        
        sello_width = 50*mm
        sello_height = 50*mm
        
        # Firma (solo última página, al centro)
        firma_x = A4[0] / 2 - 60*mm
        firma_y = 5*mm
        firma_width = 120*mm
        firma_height = 50*mm
        
        try:
            # Logo mini (en todas las páginas)
            logo_mini_path = os.path.abspath('static/shizzologomini.jpeg')
            if os.path.exists(logo_mini_path):
                self.drawImage(
                    logo_mini_path,
                    logo_mini_x, logo_mini_y,
                    width=logo_mini_width,
                    height=logo_mini_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            
            # Firma digital (SOLO en última página)
            if es_ultima_pagina:
                firma_path = os.path.abspath('static/firmaDigitalJulioMundarai.jpeg')
                if os.path.exists(firma_path):
                    self.drawImage(
                        firma_path,
                        firma_x, firma_y,
                        width=firma_width,
                        height=firma_height,
                        preserveAspectRatio=True,
                        mask='auto'
                    )

            # Sello digital (en todas las páginas, posición variable)
            sello_path = os.path.abspath('static/shizzosello.jpeg')
            if os.path.exists(sello_path):
                self.drawImage(
                    sello_path,
                    sello_x, sello_y,
                    width=sello_width,
                    height=sello_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            
            
        
        except Exception as e:
            print(f"⚠️ Error cargando imágenes del footer: {e}")
        
        # === FOOTER CON TEXTO (barra negra) ===
        
        footer_y = 15 * mm
        
        # Fondo negro para el footer
        self.setFillColor(COLOR_PRIMARIO)
        self.rect(0, 0, A4[0], footer_y, fill=True, stroke=False)
        
        # Texto del footer
        self.setFillColor(colors.white)
        self.setFont('Helvetica', 9)
        
        # Dirección (izquierda)
        direccion = "C/ Huáscar Tejeda #9, Higüey, La Altagracia, República Dominicana"
        self.drawString(15 * mm, 7 * mm, direccion)
        
        # Número de página (derecha)
        pagina_texto = f"Página {page_num} / {total_pages}"
        self.drawRightString(A4[0] - 15 * mm, 7 * mm, pagina_texto)
        
        self.restoreState()



class PDFGenerator:
    def __init__(self, datos):
        self.datos = datos
        self.width, self.height = A4
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _header(self, canvas, doc):
        """Header fijo que se repite en TODAS las páginas (incluida la de términos)"""
        logo_path = os.path.abspath('static/shizzoHeader.jpeg')
        if not os.path.exists(logo_path):
            return  # Si falta la imagen, simplemente no dibuja nada

        header_height = 37 * mm
        try:
            canvas.drawImage(
                logo_path,
                0,                                      # x = 0 (ancho completo)
                A4[1] - header_height +1*mm,                  # y = parte superior menos altura del header
                width=A4[0],                            # ancho completo de la página
                height=header_height,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception as e:
            print(f"Error dibujando header en canvas: {e}")    

    def _setup_styles(self):
        """Configurar estilos personalizados"""
        
        # Estilo para título principal (itálica)
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=COLOR_PRIMARIO,
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'  # Solo itálica, el bold lo pones con <b>
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=COLOR_PRIMARIO,
            spaceAfter=1,
            fontName='Helvetica-Bold',
            textTransform='uppercase'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            leading=14,
            fontName='Helvetica'
        ))
        
        # Estilo para texto pequeño (vigencia)
        self.styles.add(ParagraphStyle(
            name='TextoPequeno',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=COLOR_GRIS,
            fontName='Helvetica-Oblique',
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='TextoCliente',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            leading=12,
            fontName='Helvetica'
        ))
        # Estilo para info de pago
        self.styles.add(ParagraphStyle(
            name='TextoPago',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            leading=7,
            fontName='Helvetica',
            alignment=TA_RIGHT
        ))
        
        # Estilo para términos
        self.styles.add(ParagraphStyle(
            name='Termino',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            leading=16,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
    
    def _add_info_cotizacion(self):
        """Agregar información de la cotización"""
        # Título en itálica y bold
        titulo = Paragraph("<b><i>COTIZACIÓN</i></b>", self.styles['TituloPrincipal'])  # ← Agregar <b>
        self.story.append(titulo)
        self.story.append(Spacer(1, 1*mm))
        
        # Número de cotización (centrado)
        numero_style = ParagraphStyle(
            'NumeroStyle',
            parent=self.styles['TextoNormal'],
            fontSize=11,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        numero = Paragraph(self.datos['numero'], numero_style)
        self.story.append(numero)
        self.story.append(Spacer(1, 2*mm))
        
        # Vigencia (itálica, centrada)
        vigencia_texto = f"Esta cotización cuenta con una vigencia de <b>{self.datos.get('vigencia_dias', 30)} días</b> a partir de su emisión"
        vigencia = Paragraph(vigencia_texto, self.styles['TextoPequeno'])
        self.story.append(vigencia)
        self.story.append(Spacer(1, 2*mm))
        
        # Fechas (centradas, bold)
        fechas_style = ParagraphStyle(
            'FechasStyle',
            parent=self.styles['TextoNormal'],
            fontSize=11,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        fechas = Paragraph(f"{self.datos['fecha_emision']} - {self.datos['fecha_vencimiento']}", fechas_style)
        self.story.append(fechas)
        self.story.append(Spacer(1, 4*mm))
    
    def _add_info_cliente_pago(self):
        """Agregar información del cliente y pago en dos columnas"""
        cliente = self.datos['cliente']
        
        # Crear estilos
        titulo_style = ParagraphStyle(
            'TituloSeccion',
            parent=self.styles['Subtitulo'],
            fontSize=12,
            spaceAfter=2.5
        )
        pago_tituo_style = ParagraphStyle(
            'TituloPago',
            parent=self.styles['Subtitulo'],
            fontSize=12,
            spaceAfter=2.5,
            alignment=TA_RIGHT
        )
        
        # Información del cliente
        cliente_data = [
            [Paragraph("<b>INFORMACIÓN DEL SOLICITANTE</b>", titulo_style)],
            [Paragraph(f"<b>Nombre:</b> {cliente['nombre']}", self.styles['TextoCliente'])],
            [Paragraph(f"<b>RNC:</b> {cliente.get('rnc', 'N/A')}", self.styles['TextoCliente'])],
            [Paragraph(f"<b>Correo:</b> {cliente.get('correo', 'N/A')}", self.styles['TextoCliente'])],
            [Paragraph(f"<b>Teléfono:</b> {cliente.get('telefono', 'N/A')}", self.styles['TextoCliente'])],
            [Paragraph(f"<b>Dirección:</b> {cliente.get('direccion', 'N/A')}", self.styles['TextoCliente'])]
        ]
        
        tabla_cliente = Table(cliente_data, colWidths=[85*mm])
        tabla_cliente.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Información de pago
        pago_data = [
            [Paragraph("<b>INFORMACIÓN DE PAGO</b>", pago_tituo_style)],
            [Paragraph("<b>Moneda:</b> Peso Dominicano", self.styles['TextoPago'])],
            [Paragraph("<b>Método de pago:</b> Transferencia bancaria", self.styles['TextoPago'])],
            [Paragraph("Banco BHD: 38770920010 – SHIZZO GROUP", self.styles['TextoPago'])],
            [Paragraph("Banco Popular: 835902214 – Daniel A. Saladin", self.styles['TextoPago'])],
            [Paragraph("Banreservas: 9603583795 – Julio Leonardo Mundaray", self.styles['TextoPago'])]
        ]
        
        tabla_pago = Table(pago_data, colWidths=[85*mm])
        tabla_pago.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Tabla contenedora con dos columnas
        tabla_info = Table(
            [[tabla_cliente, tabla_pago]],
            colWidths=[95*mm, 85*mm],
            spaceBefore=0,
            spaceAfter=0
        )
        
        tabla_info.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        self.story.append(tabla_info)
        self.story.append(Spacer(1, 0*mm))
    
    def _add_descripcion(self):
        """Agregar descripción del proyecto"""
        if self.datos.get('descripcion'):
            desc_titulo = Paragraph("<b>DESCRIPCIÓN</b>", self.styles['Subtitulo'])
            self.story.append(desc_titulo)
            self.story.append(Spacer(1, 1*mm))
            
            desc_texto = Paragraph(self.datos['descripcion'], self.styles['TextoNormal'])
            self.story.append(desc_texto)
            self.story.append(Spacer(1, 3*mm))
    
    def _add_tabla_items(self):
        """Agregar tabla de items/alcances"""
        # Header de la tabla
        header_style = ParagraphStyle(
            'HeaderTable',
            parent=self.styles['TextoNormal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        data = [
            [
                Paragraph("<b>ALCANCE</b>", header_style),
                Paragraph("<b>MONTO (DOP)</b>", header_style)
            ]
        ]
        
        # Items
        for item in self.datos.get('items', []):
            alcance = Paragraph(item['alcance'], self.styles['TextoNormal'])
            # Formato: DOP 250,000,000.00
            monto = Paragraph(f"DOP {item['monto']:,.2f}", self.styles['TextoNormal'])
            data.append([alcance, monto])
        
        # Crear tabla
        tabla = Table(data, colWidths=[130*mm, 45*mm])
        
        # Estilos de la tabla
        tabla.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_GRIS_CLARO),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_PRIMARIO),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Contenido
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Bordes
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        
        self.story.append(tabla)
        self.story.append(Spacer(1, 8*mm))
    
    def _add_totales(self):
        """Agregar tabla de totales"""
        subtotal = self.datos.get('subtotal', 0)
        itbis = self.datos.get('itbis', 0)
        total = self.datos.get('total', 0)
        
        # Estilo para totales
        total_style = ParagraphStyle(
            'TotalStyle',
            parent=self.styles['TextoNormal'],
            fontSize=11,
            fontName='Helvetica',
            alignment=TA_LEFT
        )
        
        total_bold_style = ParagraphStyle(
            'TotalBoldStyle',
            parent=self.styles['TextoNormal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        )
        
        data = [
            [Paragraph('SUBTOTAL', total_style), Paragraph(f"DOP {subtotal:,.2f}", total_style)],
            [Paragraph('ITBIS (18%)', total_style), Paragraph(f"DOP {itbis:,.2f}", total_style)],
            [Paragraph('<b>TOTAL</b>', total_bold_style), Paragraph(f"<b>DOP {total:,.2f}</b>", total_bold_style)]
        ]
        
        tabla_totales = Table(data, colWidths=[40*mm, 50*mm])
        
        tabla_totales.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LINEABOVE', (0, 2), (-1, 2), 1, COLOR_PRIMARIO),
        ]))
        
        # Alinear a la derecha
        tabla_container = Table([[tabla_totales]], colWidths=[180*mm])
        tabla_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ]))
        
        self.story.append(tabla_container)
    
    def _add_terminos(self):
        """Agregar términos y condiciones"""
        if not self.datos.get('terminos'):
            return
        
        self.story.append(PageBreak())
        
        
        titulo = Paragraph("<b>TÉRMINOS Y CONDICIONES</b>", self.styles['Subtitulo'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 5*mm))
        
        for idx, termino in enumerate(self.datos['terminos'], 1):
            termino_texto = Paragraph(
                f"<b>{idx}.</b> {termino}",
                self.styles['Termino']
            )
            self.story.append(termino_texto)
            self.story.append(Spacer(1, 2*mm))
    
    def generar(self, ruta_salida=None):
        """Generar el PDF completo con header fijo en todas las páginas"""
        # === Determinar ruta y nombre del archivo ===
        if ruta_salida:
            ruta_final = ruta_salida
            os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        else:
            cliente = self.datos['cliente']['nombre'].strip()
            fecha = self.datos['fecha_emision'].replace("/", "-")
            cliente_limpio = "".join(c for c in cliente if c.isalnum() or c in " -_").rstrip()
            nombre_pdf = f"COT-{self.datos['numero']} {cliente_limpio} {fecha}.pdf"
            ruta_final = os.path.join(CARPETA_POR_DEFECTO, nombre_pdf)
        
        # === Estimación de páginas (solo para el footer) ===
        num_items = len(self.datos.get('items', []))
        num_terminos = len(self.datos.get('terminos', []))
        paginas_items = max(1, (num_items // 8) + 1)
        paginas_terminos = 1 if num_terminos > 0 else 0
        total_paginas = paginas_items + paginas_terminos

        # === Crear documento con márgenes correctos ===
        doc = SimpleDocTemplate(
            ruta_final,
            pagesize=A4,
            topMargin=37 * mm,       # 37 mm header + 5 mm de espacio respiratorio
            bottomMargin=55 * mm,    # footer + sello + firma (un poco más seguro)
            leftMargin=15 * mm,
            rightMargin=15 * mm
        )

        # === Construir el contenido SIN añadir el header manualmente ===
        self._add_info_cotizacion()
        self._add_info_cliente_pago()
        self._add_descripcion()
        self._add_tabla_items()
        self._add_totales()
        self._add_terminos()   # ya no llama a _add_header()

        # === Generar PDF con header repetido y footer personalizado ===
        doc.build(
            self.story,
            onFirstPage=self._header,      # Header en la primera página
            onLaterPages=self._header,     # Header en todas las demás
            canvasmaker=lambda *args, **kwargs: FooterCanvas(
                *args,
                total_paginas=total_paginas,
                **kwargs
            )
        )

        print(f"PDF generado: {ruta_final}")
        return ruta_final
      


def generar_pdf_con_datos(datos, ruta_salida=None):
    """
    Función wrapper para mantener compatibilidad con el código existente
    """
    generator = PDFGenerator(datos)
    return generator.generar(ruta_salida)