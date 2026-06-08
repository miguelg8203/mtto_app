# Mantenimiento Preventivo App

## Stack
- Backend: FastAPI + Python
- Base de datos: PostgreSQL (Railway)
- Frontend: HTML/CSS/JS en /static/index.html

## Deploy en Railway
1. Conectar repo a Railway
2. Agregar PostgreSQL plugin
3. Railway agrega DATABASE_URL automáticamente
4. Deploy automático en cada push

## Desarrollo local
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
