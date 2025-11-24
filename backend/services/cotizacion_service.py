from sqlalchemy.orm import Session
from models import Cotizacion, ItemCotizacion, TerminoCotizacion, Cliente
from schemas import CotizacionCreate
from datetime import datetime, timedelta, timezone
from services.pdf_generator_reportlab import generar_pdf_con_datos

class CotizacionService:
    
    @staticmethod
    def generar_numero_cotizacion(db: Session) -> str:
        """Generar número único de cotización"""
        mes = datetime.now().strftime("%m")
        anio = datetime.now().strftime("%y")
        contador = db.query(Cotizacion).count() + 1
        numero = f"EST-{mes}{anio}-{str(contador).zfill(4)}"
        return numero
    
    @staticmethod
    def crear_cotizacion(db: Session, cotizacion_data: CotizacionCreate):
        """Crear cotización con items, términos y PDF"""
        
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
        
        # === GENERAR PDF ===
        try:
            datos_pdf = {
                "numero": numero,
                "fecha_emision": fecha_emision.strftime("%d/%m/%Y"),
                "fecha_vencimiento": fecha_vencimiento.strftime("%d/%m/%Y"),
                "vigencia_dias": cotizacion_data.vigencia_dias,
                "cliente": {
                    "nombre": cliente.nombre,
                    "rnc": cliente.rnc or "",
                    "correo": cliente.correo or "",
                    "telefono": cliente.telefono or "",
                    "direccion": cliente.direccion or ""
                },
                "descripcion": cotizacion_data.descripcion or "",
                "items": [{"alcance": item.alcance, "monto": item.monto} for item in cotizacion_data.items],
                "terminos": [termino.texto for termino in (cotizacion_data.terminos or [])],
                "subtotal": subtotal,
                "itbis": itbis,
                "total": total
            }
            
            # Generar PDF
            
            pdf_path = generar_pdf_con_datos(datos_pdf)
            db_cotizacion.pdf_path = pdf_path
            db.commit()
            
        except Exception as e:
            print(f"❌ Error generando PDF: {e}")
        
        return db_cotizacion