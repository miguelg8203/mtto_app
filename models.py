from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Area(Base):
    __tablename__ = "areas"
    id       = Column(String, primary_key=True)
    nombre   = Column(String, nullable=False)
    icono    = Column(String, default="🏭")
    color    = Column(String, default="#3b82f6")

class Equipo(Base):
    __tablename__ = "equipos"
    id             = Column(Integer, primary_key=True, index=True)
    area_id        = Column(String, ForeignKey("areas.id"), nullable=False)
    descripcion    = Column(String, nullable=False)
    codigo         = Column(String, nullable=True)
    categoria      = Column(String, nullable=False)  # ALTO, MEDIO, BAJO
    intervenciones = Column(JSON, default=[])         # [{frecuencia, dias_ciclo, ultima_fecha}]

class Tecnico(Base):
    __tablename__ = "tecnicos"
    id     = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cargo  = Column(String, nullable=False)

class Registro(Base):
    __tablename__ = "registros"
    id             = Column(Integer, primary_key=True, index=True)
    equipo_id      = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    area_id        = Column(String, ForeignKey("areas.id"), nullable=False)
    equipo_nombre  = Column(String)
    frecuencia     = Column(String)
    fecha          = Column(String)
    tecnico        = Column(String)
    obs            = Column(Text)
    fotos          = Column(JSON, default=[])
    registrado     = Column(DateTime, server_default=func.now())

class Config(Base):
    __tablename__ = "config"
    id      = Column(Integer, primary_key=True)
    empresa = Column(String, default="Planta de Beneficio")
    year    = Column(String, default="2026")
    passwd  = Column(String, default="")
