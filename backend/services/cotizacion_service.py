from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from models import Cotizacion, ItemCotizacion, TerminoCotizacion, Cliente, TipoCotizacion
from schemas import CotizacionCreate
from datetime import datetime, timedelta, timezone

class CotizacionService:
    
    @staticmethod
    def generar_numero_cotizacion(db: Session, tipo_id: int) -> str:
        """Generar número único de cotización basado en el tipo"""
        # Obtener el tipo
        tipo = db.query(TipoCotizacion).filter(TipoCotizacion.id == tipo_id).first()
        if not tipo:
            raise ValueError("Tipo de cotización no encontrado")
        
        # Obtener mes y año actual
        mes = datetime.now().strftime("%m")
        anio = datetime.now().strftime("%y")
        
        # Contar cotizaciones del mismo tipo
        contador = db.query(Cotizacion).filter(
            Cotizacion.tipo_id == tipo_id
        ).count() + 1
        
        # Formato: CODIGO-MMYY-0001
        numero = f"{tipo.codigo}-{mes}{anio}-{str(contador).zfill(4)}"
        return numero
    
    @staticmethod
    def crear_cotizacion(db: Session, cotizacion_data: CotizacionCreate):
        """Crear cotización SIN generar PDF"""
        
        # Verificar que el cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == cotizacion_data.cliente_id).first()
        if not cliente:
            raise ValueError("Cliente no encontrado")
        
        # Verificar que el tipo existe
        tipo = db.query(TipoCotizacion).filter(TipoCotizacion.id == cotizacion_data.tipo_id).first()
        if not tipo:
            raise ValueError("Tipo de cotización no encontrado")
        
        # Generar número basado en el tipo
        numero = CotizacionService.generar_numero_cotizacion(db, cotizacion_data.tipo_id)
        
        # Calcular fechas
        fecha_emision = datetime.now(timezone.utc)
        fecha_vencimiento = fecha_emision + timedelta(days=cotizacion_data.vigencia_dias)
        
        # Calcular totales
        subtotal = sum(item.monto for item in cotizacion_data.items)
        itbis = subtotal * 0.18
        total = subtotal + itbis
        
        # Crear cotización
        db_cotizacion = Cotizacion(
            numero=numero,
            cliente_id=cotizacion_data.cliente_id,
            tipo_id=cotizacion_data.tipo_id,
            descripcion=cotizacion_data.descripcion,
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            vigencia_dias=cotizacion_data.vigencia_dias,
            subtotal=subtotal,
            itbis=itbis,
            total=total,
            pdf_path=None
        )
        db.add(db_cotizacion)
        db.flush()
        
        # Crear items
        for idx, item in enumerate(cotizacion_data.items):
            db_item = ItemCotizacion(
                cotizacion_id=db_cotizacion.id,
                alcance=item.alcance,
                monto=item.monto,
                orden=idx
            )
            db.add(db_item)
        
        # Crear términos
        for idx, termino in enumerate(cotizacion_data.terminos or []):
            db_termino = TerminoCotizacion(
                cotizacion_id=db_cotizacion.id,
                texto=termino.texto,
                orden=idx
            )
            db.add(db_termino)
        
        db.commit()
        db.refresh(db_cotizacion)
        
        return db_cotizacion
    
    @staticmethod
    def generar_pdf_cotizacion(db: Session, cotizacion_id: int):
        """Generar PDF de una cotización existente"""
        from services.pdf_generator_reportlab import generar_pdf_con_datos
        
        # Obtener cotización completa
        cotizacion = db.query(Cotizacion).filter(Cotizacion.id == cotizacion_id).first()
        if not cotizacion:
            raise ValueError("Cotización no encontrada")
        
        # Preparar datos para el PDF
        datos_pdf = {
            "numero": cotizacion.numero,
            "fecha_emision": cotizacion.fecha_emision.strftime("%d/%m/%Y"),
            "fecha_vencimiento": cotizacion.fecha_vencimiento.strftime("%d/%m/%Y"),
            "vigencia_dias": cotizacion.vigencia_dias,
            "cliente": {
                "nombre": cotizacion.cliente.nombre,
                "rnc": cotizacion.cliente.rnc or "",
                "correo": cotizacion.cliente.correo or "",
                "telefono": cotizacion.cliente.telefono or "",
                "direccion": cotizacion.cliente.direccion or ""
            },
            "descripcion": cotizacion.descripcion or "",
            "items": [{"alcance": item.alcance, "monto": item.monto} for item in cotizacion.items],
            "terminos": [termino.texto for termino in cotizacion.terminos],
            "subtotal": cotizacion.subtotal,
            "itbis": cotizacion.itbis,
            "total": cotizacion.total
        }
        
        # Generar PDF
        pdf_path = generar_pdf_con_datos(datos_pdf)
        
        # Actualizar ruta del PDF en la BD
        cotizacion.pdf_path = pdf_path
        db.commit()
        
        return pdf_path
    
    @staticmethod
    def listar(db: Session, skip: int = 0, limit: int = 100):
        """Listar cotizaciones"""
        return db.query(Cotizacion).order_by(Cotizacion.fecha_emision.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_por_id(db: Session, cotizacion_id: int):
        """Obtener cotización por ID"""
        return db.query(Cotizacion).filter(Cotizacion.id == cotizacion_id).first()
    
    @staticmethod
    def contar_total(db: Session) -> int:
        """Contar total de cotizaciones"""
        return db.query(Cotizacion).count()
    
    @staticmethod
    def contar_mes_actual(db: Session) -> int:
        """Contar cotizaciones del mes actual"""
        mes_actual = datetime.now().month
        anio_actual = datetime.now().year
        return db.query(Cotizacion).filter(
            extract('month', Cotizacion.fecha_emision) == mes_actual,
            extract('year', Cotizacion.fecha_emision) == anio_actual
        ).count()
    
    @staticmethod
    def monto_total_mes(db: Session) -> float:
        """Monto total cotizado en el mes"""
        mes_actual = datetime.now().month
        anio_actual = datetime.now().year
        resultado = db.query(func.sum(Cotizacion.total)).filter(
            extract('month', Cotizacion.fecha_emision) == mes_actual,
            extract('year', Cotizacion.fecha_emision) == anio_actual
        ).scalar()
        return resultado or 0.0