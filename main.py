from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import json, os

from database import engine, get_db, Base
import models

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mantenimiento Preventivo API")

# ── Servir frontend ──────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

# ══════════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════
class AreaIn(BaseModel):
    id:     str
    nombre: str
    icono:  Optional[str] = "🏭"
    color:  Optional[str] = "#3b82f6"

class EquipoIn(BaseModel):
    area_id:        str
    descripcion:    str
    codigo:         Optional[str] = ""
    categoria:      str
    intervenciones: Optional[list] = []

class TecnicoIn(BaseModel):
    nombre: str
    cargo:  str

class RegistroIn(BaseModel):
    equipo_id:     int
    area_id:       str
    equipo_nombre: Optional[str] = ""
    frecuencia:    str
    fecha:         str
    tecnico:       Optional[str] = ""
    obs:           Optional[str] = ""
    fotos:         Optional[list] = []

class ConfigIn(BaseModel):
    empresa: Optional[str] = "Planta de Beneficio"
    year:    Optional[str] = "2026"
    passwd:  Optional[str] = ""

class LoginIn(BaseModel):
    usuario: str
    passwd:  str

# ══════════════════════════════════════════════════════════════════════════════
# INIT — seed áreas y LB equipos al arrancar si BD está vacía
# ══════════════════════════════════════════════════════════════════════════════
def seed_inicial(db: Session):
    if db.query(models.Area).count() == 0:
        areas_default = [
            models.Area(id="LB",   nombre="Línea de Beneficio", icono="🏭", color="#3b82f6"),
            models.Area(id="DS",   nombre="Desposte",            icono="🔪", color="#8b5cf6"),
            models.Area(id="CO",   nombre="Corrales",            icono="🐄", color="#10b981"),
            models.Area(id="PTAR", nombre="PTAR",                icono="💧", color="#06b6d4"),
            models.Area(id="PTAP", nombre="PTAP",                icono="🚰", color="#f59e0b"),
        ]
        db.add_all(areas_default)
        db.commit()

    if db.query(models.Config).count() == 0:
        db.add(models.Config(empresa="Planta de Beneficio", year="2026", passwd=""))
        db.commit()

@app.on_event("startup")
async def startup():
    db = next(get_db())
    seed_inicial(db)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════
@app.post("/api/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    if not data.usuario.strip():
        raise HTTPException(status_code=400, detail="Usuario requerido")
    cfg = db.query(models.Config).first()
    if cfg and cfg.passwd and data.passwd != cfg.passwd:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    return {"ok": True, "usuario": data.usuario}

# ══════════════════════════════════════════════════════════════════════════════
# ÁREAS
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/api/areas")
def get_areas(db: Session = Depends(get_db)):
    return db.query(models.Area).all()

@app.post("/api/areas")
def create_area(data: AreaIn, db: Session = Depends(get_db)):
    area = models.Area(**data.dict())
    db.add(area); db.commit(); db.refresh(area)
    return area

@app.put("/api/areas/{area_id}")
def update_area(area_id: str, data: AreaIn, db: Session = Depends(get_db)):
    area = db.query(models.Area).filter(models.Area.id == area_id).first()
    if not area: raise HTTPException(404, "Área no encontrada")
    for k, v in data.dict().items(): setattr(area, k, v)
    db.commit(); return area

@app.delete("/api/areas/{area_id}")
def delete_area(area_id: str, db: Session = Depends(get_db)):
    if area_id == "LB": raise HTTPException(400, "No se puede eliminar el área base")
    db.query(models.Equipo).filter(models.Equipo.area_id == area_id).delete()
    db.query(models.Area).filter(models.Area.id == area_id).delete()
    db.commit(); return {"ok": True}

# ══════════════════════════════════════════════════════════════════════════════
# EQUIPOS
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/api/equipos/{area_id}")
def get_equipos(area_id: str, db: Session = Depends(get_db)):
    return db.query(models.Equipo).filter(models.Equipo.area_id == area_id).all()

@app.post("/api/equipos")
def create_equipo(data: EquipoIn, db: Session = Depends(get_db)):
    eq = models.Equipo(**data.dict())
    db.add(eq); db.commit(); db.refresh(eq)
    return eq

@app.put("/api/equipos/{eq_id}")
def update_equipo(eq_id: int, data: EquipoIn, db: Session = Depends(get_db)):
    eq = db.query(models.Equipo).filter(models.Equipo.id == eq_id).first()
    if not eq: raise HTTPException(404, "Equipo no encontrado")
    for k, v in data.dict().items(): setattr(eq, k, v)
    db.commit(); return eq

@app.delete("/api/equipos/{eq_id}")
def delete_equipo(eq_id: int, db: Session = Depends(get_db)):
    db.query(models.Equipo).filter(models.Equipo.id == eq_id).delete()
    db.commit(); return {"ok": True}

# ══════════════════════════════════════════════════════════════════════════════
# TÉCNICOS
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/api/tecnicos")
def get_tecnicos(db: Session = Depends(get_db)):
    return db.query(models.Tecnico).all()

@app.post("/api/tecnicos")
def create_tecnico(data: TecnicoIn, db: Session = Depends(get_db)):
    tec = models.Tecnico(**data.dict())
    db.add(tec); db.commit(); db.refresh(tec)
    return tec

@app.delete("/api/tecnicos/{tec_id}")
def delete_tecnico(tec_id: int, db: Session = Depends(get_db)):
    db.query(models.Tecnico).filter(models.Tecnico.id == tec_id).delete()
    db.commit(); return {"ok": True}

# ══════════════════════════════════════════════════════════════════════════════
# REGISTROS
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/api/registros")
def get_registros(db: Session = Depends(get_db)):
    return db.query(models.Registro).order_by(models.Registro.id.desc()).all()

@app.get("/api/registros/{area_id}")
def get_registros_area(area_id: str, db: Session = Depends(get_db)):
    return db.query(models.Registro).filter(models.Registro.area_id == area_id).order_by(models.Registro.id.desc()).all()

@app.post("/api/registros")
def create_registro(data: RegistroIn, db: Session = Depends(get_db)):
    reg = models.Registro(**data.dict())
    db.add(reg); db.commit(); db.refresh(reg)
    # Actualizar ultima_fecha del equipo para esa frecuencia
    eq = db.query(models.Equipo).filter(models.Equipo.id == data.equipo_id).first()
    if eq:
        intervs = eq.intervenciones or []
        updated = False
        for iv in intervs:
            if iv.get("frecuencia") == data.frecuencia:
                iv["ultima_fecha"] = data.fecha
                updated = True
        if not updated:
            from datetime import date
            FREQ_DIAS = {"MENSUAL":30,"BIMENSUAL":60,"TRIMESTRAL":90,"CUATRIMESTRAL":120,"SEMESTRAL":180,"ANUAL":365,"BIANUAL":730}
            intervs.append({"frecuencia": data.frecuencia, "dias_ciclo": FREQ_DIAS.get(data.frecuencia, 30), "ultima_fecha": data.fecha})
        eq.intervenciones = intervs
        db.commit()
    return reg

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/api/config")
def get_config(db: Session = Depends(get_db)):
    cfg = db.query(models.Config).first()
    return {"empresa": cfg.empresa, "year": cfg.year, "pass": cfg.passwd}

@app.put("/api/config")
def update_config(data: ConfigIn, db: Session = Depends(get_db)):
    cfg = db.query(models.Config).first()
    if not cfg:
        cfg = models.Config(); db.add(cfg)
    cfg.empresa = data.empresa
    cfg.year    = data.year
    if data.passwd: cfg.passwd = data.passwd
    db.commit()
    return {"ok": True}

# ══════════════════════════════════════════════════════════════════════════════
# SEED LB EQUIPOS (endpoint para cargar los 136 desde el frontend)
# ══════════════════════════════════════════════════════════════════════════════
@app.post("/api/seed/lb")
def seed_lb(equipos: List[EquipoIn], db: Session = Depends(get_db)):
    if db.query(models.Equipo).filter(models.Equipo.area_id == "LB").count() > 0:
        return {"ok": True, "msg": "LB ya tiene equipos"}
    for e in equipos:
        db.add(models.Equipo(**e.dict()))
    db.commit()
    return {"ok": True, "insertados": len(equipos)}
