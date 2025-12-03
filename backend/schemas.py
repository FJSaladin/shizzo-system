from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ====================== CLIENTES ======================

class ClienteBase(BaseModel):
    nombre: str
    rnc: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: datetime  
    
    class Config:
        from_attributes = True


# ====================== TIPOS DE COTIZACIÓN ======================

class TipoCotizacionBase(BaseModel):
    nombre: str
    codigo: str
    descripcion: Optional[str] = None

class TipoCotizacionCreate(TipoCotizacionBase):
    pass

class TipoCotizacionResponse(TipoCotizacionBase):
    id: int
    activo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ====================== ITEMS ======================

class ItemCreate(BaseModel):
    alcance: str
    monto: float

class ItemResponse(ItemCreate):
    id: int
    orden: int
    
    class Config:
        from_attributes = True


# ====================== TÉRMINOS ======================

class TerminoCreate(BaseModel):
    texto: str

class TerminoResponse(TerminoCreate):
    id: int
    orden: int
    
    class Config:
        from_attributes = True


# ====================== COTIZACIONES ======================

class CotizacionBase(BaseModel):
    cliente_id: int
    tipo_id: int  # ← NUEVO
    descripcion: Optional[str] = None
    vigencia_dias: Optional[int] = 30

class CotizacionCreate(CotizacionBase):
    items: List[ItemCreate]
    terminos: Optional[List[TerminoCreate]] = []

class CotizacionResponse(CotizacionBase):
    id: int
    numero: str
    fecha_emision: datetime
    fecha_vencimiento: datetime
    subtotal: float
    itbis: float
    total: float
    estado: str
    pdf_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    cliente: ClienteResponse
    tipo: TipoCotizacionResponse  # ← NUEVO
    items: List[ItemResponse]
    terminos: List[TerminoResponse]
    
    class Config:
        from_attributes = True