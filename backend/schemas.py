from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Schema base (campos comunes)
class ClienteBase(BaseModel):
    nombre: str
    rnc: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

# Schema para CREAR un cliente (lo que el usuario envía)
class ClienteCreate(ClienteBase):
    pass

# Schema para RESPONDER con un cliente (lo que devuelve la API)
class ClienteResponse(ClienteBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: datetime  
    
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
    items: List[ItemResponse]
    terminos: List[TerminoResponse]
    
    class Config:
        from_attributes = True