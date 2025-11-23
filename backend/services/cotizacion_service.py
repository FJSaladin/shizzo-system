from sqlalchemy.orm import Session
from models import Cotizacion, ItemCotizacion, TerminoCotizacion, Cliente
from schemas import CotizacionCreate
from datetime import datetime, timedelta, timezone

class CotizacionService:
    
    @staticmethod
    def generar_numero_cotizacion(db: Session) -> str:
        """Generar número único de cotización"""
        # Formato: EST-MMYY-XXXX
        mes = datetime.now().strftime("%m")
        anio = datetime.now().strftime("%y")
        
        # Contar cuántas cotizaciones hay este mes
        contador = db.query(Cotizacion).count() + 1
        numero = f"EST-{mes}{anio}-{str(contador).zfill(4)}"
        
        return numero
    
    @staticmethod
    def crear_cotizacion(db: Session, cotizacion_data: CotizacionCreate):
        """Crear cotización con items y términos"""
        
        # Verificar que el cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == cotizacion_data.cliente_id).first()
        if not cliente:
            raise ValueError("Cliente no encontrado")
        
        # Generar número
        numero = CotizacionService.generar_numero_cotizacion(db)
        
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
            descripcion=cotizacion_data.descripcion,
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            vigencia_dias=cotizacion_data.vigencia_dias,
            subtotal=subtotal,
            itbis=itbis,
            total=total
        )
        db.add(db_cotizacion)
        db.flush()  # Para obtener el ID sin hacer commit
        
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