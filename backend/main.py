from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import uvicorn
from database import engine, get_db, Base
from models import Cliente, Cotizacion, TipoCotizacion
from schemas import (
    ClienteCreate, ClienteResponse,
    CotizacionCreate, CotizacionResponse,
    TipoCotizacionCreate, TipoCotizacionResponse
)
from services.cotizacion_service import CotizacionService
import os
from pydantic import BaseModel

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación
app = FastAPI(title="SHIZZO API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== RUTAS DE PRUEBA ======================

@app.get("/")
def home():
    return {"mensaje": "¡Bienvenido a SHIZZO API! 🚀"}

# ====================== CLIENTES ======================

@app.post("/api/clientes", response_model=ClienteResponse)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Crear un nuevo cliente"""
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.get("/api/clientes", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    """Obtener todos los clientes activos"""
    clientes = db.query(Cliente).filter(Cliente.activo == True).all()
    return clientes

@app.get("/api/clientes/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente por ID"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.put("/api/clientes/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(cliente_id: int, cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Actualizar un cliente"""
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    for key, value in cliente.model_dump().items():
        setattr(db_cliente, key, value)
    
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.delete("/api/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Eliminar (desactivar) un cliente"""
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db_cliente.activo = False
    db.commit()
    return {"mensaje": "Cliente eliminado exitosamente"}

# ====================== TIPOS DE COTIZACIÓN ======================

@app.post("/api/tipos-cotizacion", response_model=TipoCotizacionResponse)
def crear_tipo(tipo: TipoCotizacionCreate, db: Session = Depends(get_db)):
    """Crear un nuevo tipo de cotización"""
    # Verificar que el código no exista
    existe = db.query(TipoCotizacion).filter(TipoCotizacion.codigo == tipo.codigo.upper()).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe un tipo con ese código")
    
    db_tipo = TipoCotizacion(**tipo.model_dump())
    db_tipo.codigo = db_tipo.codigo.upper()  # Siempre en mayúsculas
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

@app.get("/api/tipos-cotizacion", response_model=List[TipoCotizacionResponse])
def listar_tipos(db: Session = Depends(get_db)):
    """Obtener todos los tipos activos"""
    tipos = db.query(TipoCotizacion).filter(TipoCotizacion.activo == True).all()
    return tipos

@app.get("/api/tipos-cotizacion/{tipo_id}", response_model=TipoCotizacionResponse)
def obtener_tipo(tipo_id: int, db: Session = Depends(get_db)):
    """Obtener un tipo por ID"""
    tipo = db.query(TipoCotizacion).filter(TipoCotizacion.id == tipo_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")
    return tipo

# ====================== COTIZACIONES ======================

@app.post("/api/cotizaciones", response_model=CotizacionResponse)
def crear_cotizacion(cotizacion: CotizacionCreate, db: Session = Depends(get_db)):
    """Crear una nueva cotización (sin generar PDF)"""
    try:
        return CotizacionService.crear_cotizacion(db, cotizacion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/cotizaciones", response_model=List[CotizacionResponse])
def listar_cotizaciones(db: Session = Depends(get_db)):
    """Obtener todas las cotizaciones"""
    cotizaciones = CotizacionService.listar(db)
    return cotizaciones

@app.get("/api/cotizaciones/{cotizacion_id}", response_model=CotizacionResponse)
def obtener_cotizacion(cotizacion_id: int, db: Session = Depends(get_db)):
    """Obtener una cotización por ID"""
    cotizacion = CotizacionService.obtener_por_id(db, cotizacion_id)
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return cotizacion

@app.post("/api/cotizaciones/{cotizacion_id}/generar-pdf")
def generar_pdf_cotizacion(cotizacion_id: int, db: Session = Depends(get_db)):
    """Generar PDF de una cotización existente"""
    try:
        pdf_path = CotizacionService.generar_pdf_cotizacion(db, cotizacion_id)
        return {
            "message": "PDF generado exitosamente",
            "pdf_path": pdf_path,
            "cotizacion_id": cotizacion_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")

@app.get("/api/cotizaciones/{cotizacion_id}/pdf")
def descargar_pdf(cotizacion_id: int, db: Session = Depends(get_db)):
    """Descargar PDF de una cotización"""
    cotizacion = CotizacionService.obtener_por_id(db, cotizacion_id)
    
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    if not cotizacion.pdf_path or not os.path.exists(cotizacion.pdf_path):
        try:
            CotizacionService.generar_pdf_cotizacion(db, cotizacion_id)
            db.refresh(cotizacion)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")
    
    return FileResponse(
        cotizacion.pdf_path, 
        media_type='application/pdf',
        filename=os.path.basename(cotizacion.pdf_path)
    )
# Agregar este endpoint en backend/main.py después de los otros endpoints de cotizaciones



class CambiarEstadoRequest(BaseModel):
    estado: str  # "pendiente", "aprobada", "rechazada"

@app.patch("/api/cotizaciones/{cotizacion_id}/estado")
def cambiar_estado_cotizacion(
    cotizacion_id: int, 
    request: CambiarEstadoRequest,
    db: Session = Depends(get_db)
):
    """Cambiar el estado de una cotización"""
    cotizacion = db.query(Cotizacion).filter(Cotizacion.id == cotizacion_id).first()
    
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    # Validar estado
    estados_validos = ["pendiente", "aprobada", "rechazada"]
    if request.estado not in estados_validos:
        raise HTTPException(
            status_code=400, 
            detail=f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"
        )
    
    cotizacion.estado = request.estado
    db.commit()
    db.refresh(cotizacion)
    
    return {
        "mensaje": f"Estado actualizado a '{request.estado}'",
        "cotizacion": cotizacion
    }

# Para correr el servidor
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)