from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener ruta absoluta del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent  # shizzo-system/
DB_DIR = BASE_DIR / "database"

# Crear carpeta database si no existe
DB_DIR.mkdir(exist_ok=True)

# Ruta completa a la base de datos
DB_PATH = DB_DIR / "shizzo.db"

# Crear engine
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session local para hacer consultas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para crear modelos
Base = declarative_base()

# Función para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()