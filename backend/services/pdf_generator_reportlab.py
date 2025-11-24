import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime

# Carpeta por defecto para PDFs
CARPETA_POR_DEFECTO = "Cotizaciones"
os.makedirs(CARPETA_POR_DEFECTO, exist_ok=True)

# Colores SHIZZO
COLOR_PRIMARIO = colors.HexColor('#222222')
COLOR_AMARILLO = colors.HexColor('#eebe22')
COLOR_GRIS = colors.HexColor('#666666')
COLOR_GRIS_CLARO = colors.HexColor('#f8f8f8')

class PDFGenerator:
    def __init__(self, datos):
        self.datos = datos
        self.width, self.height = A4
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        """Configurar estilos personalizados"""
        
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=COLOR_PRIMARIO,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=COLOR_PRIMARIO,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            textTransform='uppercase'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=COLOR_PRIMARIO,
            leading=14,
            fontName='Helvetica'
        ))
        
        # Estilo para texto pequeño
        self.styles.add(ParagraphStyle(
            name='TextoPequeno',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=COLOR_GRIS,
            fontName='Helvetica'
        ))
        
        # Estilo para términos
        self.styles.add(ParagraphStyle(
            name='Termino',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=COLOR_PRIMARIO,
            leading=16,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
    
    def _add_header(self):
        """Agregar header con logo"""
        try:
            logo_path = os.path.abspath('static/shizzoHeader.jpeg')
            if os.path.exists(logo_path):
                img = Image(logo_path, width=self.width, height=25*mm)
                self.story.append(img)
                self.story.append(Spacer(1, 10*mm))
        except Exception as e:
            print(f"⚠️ No se pudo cargar el header: {e}")
    
    def _add_info_cotizacion(self):
        """Agregar información de la cotización"""
        # Título
        titulo = Paragraph("COTIZACIÓN", self.styles['TituloPrincipal'])
        self.story.append(titulo)
        
        # Número de cotización
        numero = Paragraph(
            f"<b>{self.datos['numero']}</b>",
            self.styles['TextoNormal']
        )
        self.story.append(numero)
        
        # Vigencia
        vigencia = Paragraph(
            f"<i>Esta cotización cuenta con una vigencia de <b>{self.datos.get('vigencia_dias', 30)} días</b> a partir de su emisión</i>",
            self.styles['TextoPequeno']
        )
        self.story.append(vigencia)
        
        # Fechas
        fechas = Paragraph(
            f"<b>{self.datos['fecha_emision']} - {self.datos['fecha_vencimiento']}</b>",
            self.styles['TextoNormal']
        )
        self.story.append(fechas)
        self.story.append(Spacer(1, 8*mm))
    
    def _add_info_cliente_pago(self):
        """Agregar información del cliente y pago en dos columnas"""
        cliente = self.datos['cliente']
        
        # Información del cliente (columna izquierda)
        info_cliente = [
            [Paragraph("<b>INFORMACIÓN DEL SOLICITANTE</b>", self.styles['Subtitulo'])],
            [Paragraph(f"<b>Nombre:</b> {cliente['nombre']}", self.styles['TextoNormal'])],
            [Paragraph(f"<b>RNC:</b> {cliente.get('rnc', 'N/A')}", self.styles['TextoNormal'])],
            [Paragraph(f"<b>Correo:</b> {cliente.get('correo', 'N/A')}", self.styles['TextoNormal'])],
            [Paragraph(f"<b>Teléfono:</b> {cliente.get('telefono', 'N/A')}", self.styles['TextoNormal'])],
            [Paragraph(f"<b>Dirección:</b> {cliente.get('direccion', 'N/A')}", self.styles['TextoNormal'])]
        ]
        
        # Información de pago (columna derecha)
        info_pago = [
            [Paragraph("<b>INFORMACIÓN DE PAGO</b>", self.styles['Subtitulo'])],
            [Paragraph("<b>Moneda:</b> Peso Dominicano", self.styles['TextoNormal'])],
            [Paragraph("<b>Método de pago:</b> Transferencia bancaria", self.styles['TextoNormal'])],
            [Paragraph("Banco BHD: 38770920010 – SHIZZO GROUP", self.styles['TextoPequeno'])],
            [Paragraph("Banco Popular: 835902214 – Daniel A. Saladin", self.styles['TextoPequeno'])],
            [Paragraph("Banreservas: 9603583795 – Julio Leonardo Mundaray", self.styles['TextoPequeno'])]
        ]
        
        # Crear tabla con dos columnas
        tabla_info = Table(
            [[info_cliente, info_pago]],
            colWidths=[self.width * 0.45, self.width * 0.45]
        )
        
        tabla_info.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        self.story.append(tabla_info)
        self.story.append(Spacer(1, 6*mm))
    
    def _add_descripcion(self):
        """Agregar descripción del proyecto"""
        if self.datos.get('descripcion'):
            desc_titulo = Paragraph("<b>DESCRIPCIÓN</b>", self.styles['Subtitulo'])
            self.story.append(desc_titulo)
            
            desc_texto = Paragraph(self.datos['descripcion'], self.styles['TextoNormal'])
            self.story.append(desc_texto)
            self.story.append(Spacer(1, 6*mm))
    
    def _add_tabla_items(self):
        """Agregar tabla de items/alcances"""
        # Header de la tabla
        data = [
            [
                Paragraph("<b>ALCANCE</b>", self.styles['TextoNormal']),
                Paragraph("<b>MONTO (DOP)</b>", self.styles['TextoNormal'])
            ]
        ]
        
        # Items
        for item in self.datos.get('items', []):
            alcance = Paragraph(item['alcance'], self.styles['TextoNormal'])
            monto = Paragraph(f"DOP {item['monto']:,.2f}", self.styles['TextoNormal'])
            data.append([alcance, monto])
        
        # Crear tabla
        tabla = Table(data, colWidths=[self.width * 0.7, self.width * 0.2])
        
        # Estilos de la tabla
        tabla.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_GRIS_CLARO),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_PRIMARIO),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Contenido
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), COLOR_PRIMARIO),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Bordes
            ('LINEBELOW', (0, 0), (-1, 0), 2, COLOR_PRIMARIO),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        self.story.append(tabla)
        self.story.append(Spacer(1, 6*mm))
    
    def _add_totales(self):
        """Agregar tabla de totales"""
        subtotal = self.datos.get('subtotal', 0)
        itbis = self.datos.get('itbis', 0)
        total = self.datos.get('total', 0)
        
        data = [
            ['SUBTOTAL', f"DOP {subtotal:,.2f}"],
            ['ITBIS (18%)', f"DOP {itbis:,.2f}"],
            ['TOTAL', f"DOP {total:,.2f}"]
        ]
        
        tabla_totales = Table(data, colWidths=[60*mm, 50*mm])
        
        tabla_totales.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
            ('FONTNAME', (0, 2), (1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_PRIMARIO),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, 2), (-1, 2), 1.5, COLOR_PRIMARIO),
        ]))
        
        # Alinear a la derecha
        tabla_container = Table([[tabla_totales]], colWidths=[self.width * 0.9])
        tabla_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ]))
        
        self.story.append(tabla_container)
    
    def _add_terminos(self):
        """Agregar términos y condiciones"""
        if not self.datos.get('terminos'):
            return
        
        self.story.append(PageBreak())
        self._add_header()
        
        titulo = Paragraph("<b>TÉRMINOS Y CONDICIONES</b>", self.styles['Subtitulo'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 4*mm))
        
        for idx, termino in enumerate(self.datos['terminos'], 1):
            termino_texto = Paragraph(
                f"<b>{idx}.</b> {termino}",
                self.styles['Termino']
            )
            self.story.append(termino_texto)
            self.story.append(Spacer(1, 3*mm))
    
    def generar(self, ruta_salida=None):
        """Generar el PDF completo"""
        # Determinar ruta final
        if ruta_salida:
            ruta_final = ruta_salida
            os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        else:
            cliente = self.datos['cliente']['nombre'].strip()
            fecha = self.datos['fecha_emision'].replace("/", "-")
            cliente_limpio = "".join(c for c in cliente if c.isalnum() or c in " -_").rstrip()
            nombre_pdf = f"COT-{self.datos['numero']} {cliente_limpio} {fecha}.pdf"
            ruta_final = os.path.join(CARPETA_POR_DEFECTO, nombre_pdf)
        
        # Crear documento
        doc = SimpleDocTemplate(
            ruta_final,
            pagesize=A4,
            topMargin=10*mm,
            bottomMargin=15*mm,
            leftMargin=15*mm,
            rightMargin=15*mm
        )
        
        # Construir contenido
        self._add_header()
        self._add_info_cotizacion()
        self._add_info_cliente_pago()
        self._add_descripcion()
        self._add_tabla_items()
        self._add_totales()
        self._add_terminos()
        
        # Generar PDF
        doc.build(self.story)
        
        print(f"✅ PDF generado: {ruta_final}")
        return ruta_final


def generar_pdf_con_datos(datos, ruta_salida=None):
    """
    Función wrapper para mantener compatibilidad con el código existente
    """
    generator = PDFGenerator(datos)
    return generator.generar(ruta_salida)