from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    rnc = Column(String(50))
    correo = Column(String(100))
    telefono = Column(String(20))
    direccion = Column(String(300))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relación: Un cliente puede tener muchas cotizaciones
    cotizaciones = relationship("Cotizacion", back_populates="cliente")


class Cotizacion(Base):
    __tablename__ = "cotizaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, nullable=False)  # EST-1125-0001
    
    # Relación con cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente = relationship("Cliente", back_populates="cotizaciones")
    
    # Fechas
    fecha_emision = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_vencimiento = Column(DateTime)
    vigencia_dias = Column(Integer, default=30)
    
    # Información
    descripcion = Column(Text)
    
    # Montos
    subtotal = Column(Float, default=0.0)
    itbis = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # PDF
    pdf_path = Column(String(500))
    
    # Estado
    estado = Column(String(50), default="pendiente")  # pendiente, aprobada, rechazada
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones: Una cotización tiene muchos items y términos
    items = relationship("ItemCotizacion", back_populates="cotizacion", cascade="all, delete-orphan")
    terminos = relationship("TerminoCotizacion", back_populates="cotizacion", cascade="all, delete-orphan")


class ItemCotizacion(Base):
    __tablename__ = "items_cotizacion"
    
    id = Column(Integer, primary_key=True, index=True)
    cotizacion_id = Column(Integer, ForeignKey("cotizaciones.id"), nullable=False)
    alcance = Column(Text, nullable=False)
    monto = Column(Float, nullable=False)
    orden = Column(Integer, default=0)
    
    # Relación: Muchos items pertenecen a una cotización
    cotizacion = relationship("Cotizacion", back_populates="items")


class TerminoCotizacion(Base):
    __tablename__ = "terminos_cotizacion"
    
    id = Column(Integer, primary_key=True, index=True)
    cotizacion_id = Column(Integer, ForeignKey("cotizaciones.id"), nullable=False)
    texto = Column(Text, nullable=False)
    orden = Column(Integer, default=0)
    
    # Relación: Muchos términos pertenecen a una cotización
    cotizacion = relationship("Cotizacion", back_populates="terminos")