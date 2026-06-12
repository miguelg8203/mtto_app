from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os, json

app = FastAPI()

# ── PostgreSQL via psycopg2 ───────────────────────────────────────────────────
import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    url = os.environ.get("DATABASE_URL","")
    if not url:
        raise Exception("DATABASE_URL no configurada en Railway")
    if url.startswith("postgres://"):
        url = url.replace("postgres://","postgresql://",1)
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

def init_db():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tecnicos (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                cargo TEXT NOT NULL
            )
        """)
        conn.commit(); cur.close(); conn.close()
    except Exception as e:
        print("DB init error:", e)

init_db()

class TecnicoIn(BaseModel):
    nombre: str
    cargo: str

@app.get("/api/tecnicos")
def get_tecnicos():
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT * FROM tecnicos ORDER BY id")
        rows = cur.fetchall(); cur.close(); conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        return []

@app.post("/api/tecnicos")
def create_tecnico(data: TecnicoIn):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO tecnicos (nombre, cargo) VALUES (%s, %s) RETURNING *",
                    (data.nombre, data.cargo))
        row = dict(cur.fetchone()); conn.commit(); cur.close(); conn.close()
        return row
    except Exception as e:
        print("ERROR crear tecnico:", str(e))
        raise HTTPException(500, detail=str(e))

@app.delete("/api/tecnicos/{tec_id}")
def delete_tecnico(tec_id: int):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("DELETE FROM tecnicos WHERE id=%s", (tec_id,))
        conn.commit(); cur.close(); conn.close()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mantenimiento Preventivo 2026</title>
<link rel="icon" type="image/png" href="data:image/png;base64,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">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
*{margin:0;padding:0;box-sizing:border-box;}
:root{
  --bg:#0a0c10;--s1:#0f1218;--s2:#151922;--s3:#1c2130;
  --bd:#1e2535;--bd2:#252d40;
  --t:#d4dded;--td:#6b7a8d;--tb:#f0f4ff;
  --red:#ef4444;--yellow:#f59e0b;--green:#10b981;--blue:#3b82f6;--purple:#8b5cf6;--cyan:#06b6d4;
  --f:'Inter',sans-serif;--mono:'JetBrains Mono',monospace;
}
html,body{height:100%;background:var(--bg);font-family:var(--f);color:var(--t);font-size:14px;font-weight:500;}
.app{display:flex;height:100vh;overflow:hidden;}

/* SIDEBAR */
.sidebar{width:250px;background:var(--s1);border-right:1px solid var(--bd);display:flex;flex-direction:column;flex-shrink:0;transition:width .2s;}
.sb-logo{padding:16px;border-bottom:1px solid var(--bd);}
.sb-logo h1{font-size:14px;font-weight:700;color:var(--tb);line-height:1.3;}
.sb-logo p{font-size:11px;color:var(--td);margin-top:2px;}
.sb-logo .year{display:inline-block;background:var(--blue);color:#fff;font-size:10px;font-weight:700;padding:2px 7px;border-radius:10px;margin-top:5px;}

/* AREA SELECTOR */
.area-selector{padding:10px 12px;border-bottom:1px solid var(--bd);}
.area-selector label{font-size:10px;font-weight:600;color:var(--td);text-transform:uppercase;letter-spacing:.5px;display:block;margin-bottom:5px;}
.area-select{width:100%;background:var(--s2);border:1px solid var(--bd);border-radius:6px;color:var(--tb);font-family:var(--f);font-size:12px;padding:6px 8px;outline:none;cursor:pointer;}
.area-select:focus{border-color:var(--blue);}
.area-select option{background:var(--s2);}

.sb-nav{flex:1;padding:8px 0;overflow-y:auto;}
.nav-item{display:flex;align-items:center;gap:10px;padding:9px 16px;cursor:pointer;font-size:13px;font-weight:600;color:var(--td);transition:all .15s;border-left:3px solid transparent;user-select:none;}
.nav-item:hover{background:var(--s2);color:var(--t);}
.nav-item.on{background:var(--s2);color:var(--tb);border-left-color:var(--blue);}
.nav-item .ico{font-size:15px;width:20px;text-align:center;}
.nav-sep{height:1px;background:var(--bd);margin:6px 12px;}
.nav-badge{margin-left:auto;font-size:10px;font-weight:700;padding:2px 6px;border-radius:8px;}
.nb-red{background:rgba(239,68,68,.2);color:var(--red);}
.nb-yellow{background:rgba(245,158,11,.2);color:var(--yellow);}
.sb-footer{padding:10px 16px;border-top:1px solid var(--bd);font-size:11px;color:var(--td);}
.sb-footer span{color:var(--green);}
.sidebar.collapsed{width:52px;}
.sidebar.collapsed .sb-logo h1,.sidebar.collapsed .sb-logo p,.sidebar.collapsed .sb-logo .year,.sidebar.collapsed #sb-empresa{display:none;}
.sidebar.collapsed .sb-logo img{display:none;}
.sidebar.collapsed .area-selector{display:none;}
.sidebar.collapsed .nav-item span:not(.ico){display:none;}
.sidebar.collapsed .nav-badge{display:none;}
.sidebar.collapsed .nav-sep{margin:4px 6px;}
.sidebar.collapsed .sb-footer{display:none;}
.sidebar.collapsed .nav-item{padding:10px;justify-content:center;}
.sidebar.collapsed .ico{width:auto;}
.sb-toggle{background:transparent;border:none;color:var(--td);cursor:pointer;font-size:13px;padding:4px 8px;border-radius:4px;transition:all .15s;margin-left:auto;}
.sb-toggle:hover{background:var(--s2);color:var(--tb);}

/* MAIN */
.main{flex:1;display:flex;flex-direction:column;overflow:hidden;}
.topbar{height:52px;border-bottom:1px solid var(--bd);display:flex;align-items:center;padding:0 20px;gap:12px;flex-shrink:0;background:var(--s1);}
.topbar h2{font-size:16px;font-weight:600;color:var(--tb);}
.topbar-sp{flex:1;}
.search-box{display:flex;align-items:center;gap:8px;background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:6px 12px;width:240px;}
.search-box input{background:none;border:none;outline:none;color:var(--tb);font-family:var(--f);font-size:13px;width:100%;}
.search-box input::placeholder{color:var(--td);}

/* NOTIF BELL */
.notif-btn{position:relative;background:transparent;border:none;color:var(--td);font-size:18px;cursor:pointer;padding:4px 8px;border-radius:6px;transition:all .15s;}
.notif-btn:hover{background:var(--s2);color:var(--t);}
.notif-dot{position:absolute;top:2px;right:4px;width:8px;height:8px;border-radius:50%;background:var(--red);border:2px solid var(--s1);display:none;}
.notif-dot.on{display:block;}

/* NOTIF PANEL */
.notif-panel{position:fixed;top:60px;right:16px;width:360px;background:var(--s1);border:1px solid var(--bd);border-radius:12px;z-index:500;display:none;box-shadow:0 8px 32px rgba(0,0,0,.5);max-height:480px;overflow:hidden;flex-direction:column;}
.notif-panel.on{display:flex;}
.notif-hdr{padding:14px 16px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between;}
.notif-hdr h4{font-size:13px;font-weight:600;color:var(--tb);}
.notif-list{flex:1;overflow-y:auto;padding:8px;}
.notif-item{padding:10px 12px;border-radius:8px;margin-bottom:6px;cursor:pointer;transition:all .15s;border-left:3px solid;}
.notif-item:hover{background:var(--s2);}
.notif-item.ni-red{border-left-color:var(--red);background:rgba(239,68,68,.05);}
.notif-item.ni-yellow{border-left-color:var(--yellow);background:rgba(245,158,11,.05);}
.notif-title{font-size:12px;font-weight:600;color:var(--tb);margin-bottom:3px;}
.notif-sub{font-size:11px;color:var(--td);}

.content{flex:1;overflow-y:auto;padding:20px;}
.content::-webkit-scrollbar{width:5px;}
.content::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:3px;}

/* PAGES */
.page{display:none;}
.page.on{display:block;}

/* STAT CARDS */
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px;}
.stat-card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px 20px;position:relative;overflow:hidden;}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;}
.stat-card.red::before{background:var(--red);}
.stat-card.yellow::before{background:var(--yellow);}
.stat-card.green::before{background:var(--green);}
.stat-card.blue::before{background:var(--blue);}
.stat-card.purple::before{background:var(--purple);}
.stat-val{font-size:32px;font-weight:800;color:var(--tb);line-height:1;margin-bottom:4px;}
.stat-lbl{font-size:12px;color:var(--td);font-weight:500;}
.stat-sub{font-size:11px;color:var(--td);margin-top:6px;}
.stat-icon{position:absolute;right:16px;top:16px;font-size:28px;opacity:.15;}

/* SECTION */
.section-title{font-size:14px;font-weight:600;color:var(--tb);margin-bottom:12px;display:flex;align-items:center;gap:8px;}
.section-title span{font-size:12px;color:var(--td);font-weight:400;}

/* FILTER BAR */
.filter-bar{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:center;}
.filt{padding:5px 12px;border-radius:6px;border:1px solid var(--bd);background:var(--s2);color:var(--td);font-size:12px;cursor:pointer;transition:all .15s;font-family:var(--f);}
.filt:hover{border-color:var(--bd2);color:var(--t);}
.filt.on{background:var(--blue);border-color:var(--blue);color:#fff;}
.filt.red.on{background:var(--red);border-color:var(--red);}
.filt.yellow.on{background:var(--yellow);border-color:var(--yellow);color:#000;}
.filt.green.on{background:var(--green);border-color:var(--green);}
select.filt{padding:5px 8px;}

/* TABLE */
.table-wrap{background:var(--s1);border:1px solid var(--bd);border-radius:10px;overflow:hidden;}
table{width:100%;border-collapse:collapse;}
thead tr{background:var(--s2);}
th{padding:10px 14px;text-align:left;font-size:11px;font-weight:600;color:var(--td);text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;}
td{padding:10px 14px;font-size:12px;font-weight:500;border-top:1px solid var(--bd);vertical-align:middle;}
tr:hover td{background:rgba(255,255,255,.02);}
.eq-name{font-weight:500;color:var(--tb);max-width:280px;}
.eq-name small{display:block;font-size:11px;color:var(--td);font-family:var(--mono);margin-top:1px;}
.cat-badge{display:inline-block;font-size:10px;font-weight:600;padding:2px 7px;border-radius:8px;}
.cat-alto{background:rgba(239,68,68,.15);color:var(--red);}
.cat-medio{background:rgba(245,158,11,.15);color:var(--yellow);}
.cat-bajo{background:rgba(16,185,129,.15);color:var(--green);}
.status-badge{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:600;padding:3px 8px;border-radius:6px;}
.st-vencido{background:rgba(239,68,68,.15);color:var(--red);}
.st-proximo{background:rgba(245,158,11,.15);color:var(--yellow);}
.st-ok{background:rgba(16,185,129,.15);color:var(--green);}
.st-sin{background:rgba(74,85,104,.2);color:var(--td);}
.freq-tag{display:inline-block;font-size:10px;padding:2px 6px;border-radius:4px;background:var(--s3);color:var(--t);font-family:var(--mono);}
.dias-num{font-family:var(--mono);font-weight:600;}
.dias-red{color:var(--red);}
.dias-yellow{color:var(--yellow);}
.dias-green{color:var(--green);}
.btn-det{background:transparent;border:1px solid var(--bd);color:var(--td);font-size:11px;padding:3px 8px;border-radius:4px;cursor:pointer;transition:all .15s;font-family:var(--f);}
.btn-det:hover{border-color:var(--blue);color:var(--blue);}
.btn-icon{background:transparent;border:1px solid var(--bd);color:var(--td);font-size:12px;padding:3px 7px;border-radius:4px;cursor:pointer;transition:all .15s;font-family:var(--f);}
.btn-icon:hover{border-color:var(--yellow);color:var(--yellow);}
.btn-icon.del:hover{border-color:var(--red);color:var(--red);}
.pagination{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-top:1px solid var(--bd);font-size:12px;color:var(--td);}
.pg-btns{display:flex;gap:4px;}
.pg-btn{padding:4px 10px;border:1px solid var(--bd);border-radius:4px;background:var(--s2);color:var(--td);cursor:pointer;font-size:12px;font-family:var(--f);}
.pg-btn:hover{border-color:var(--blue);color:var(--blue);}
.pg-btn.on{background:var(--blue);border-color:var(--blue);color:#fff;}

/* ALERT CARDS */
.alert-list{display:flex;flex-direction:column;gap:10px;}
.alert-card{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:14px 16px;border-left:4px solid var(--red);cursor:pointer;transition:all .15s;}
.alert-card:hover{background:var(--s2);}
.alert-card.yellow{border-left-color:var(--yellow);}
.alert-card.green{border-left-color:var(--green);}
.alert-header{display:flex;align-items:center;gap:10px;margin-bottom:6px;}
.alert-title{font-size:13px;font-weight:600;color:var(--tb);flex:1;}
.alert-meta{display:flex;gap:12px;font-size:11px;color:var(--td);flex-wrap:wrap;}
.alert-meta span{display:flex;align-items:center;gap:4px;}

/* CALENDAR */
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-bottom:8px;}
.cal-header{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-bottom:4px;}
.cal-day-name{text-align:center;font-size:11px;color:var(--td);font-weight:600;padding:4px;}
.cal-day{background:var(--s1);border:1px solid var(--bd);border-radius:6px;min-height:70px;padding:6px;cursor:pointer;transition:all .15s;}
.cal-day:hover{border-color:var(--bd2);}
.cal-day.other-month{opacity:.3;}
.cal-day.today{border-color:var(--blue);}
.cal-day-num{font-size:12px;font-weight:600;color:var(--tb);margin-bottom:4px;}
.cal-event{font-size:9px;padding:2px 4px;border-radius:3px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.ce-red{background:rgba(239,68,68,.2);color:var(--red);}
.ce-yellow{background:rgba(245,158,11,.2);color:var(--yellow);}
.ce-green{background:rgba(16,185,129,.2);color:var(--green);}
.cal-nav{display:flex;align-items:center;gap:12px;margin-bottom:16px;}
.cal-nav h3{font-size:15px;font-weight:600;color:var(--tb);flex:1;text-align:center;}
.cal-nav button{background:var(--s2);border:1px solid var(--bd);color:var(--t);padding:5px 12px;border-radius:6px;cursor:pointer;font-family:var(--f);}
.cal-nav button:hover{border-color:var(--blue);color:var(--blue);}

/* CHARTS */
.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:24px;}
.chart-grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:24px;}
.chart-card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px;}
.chart-title{font-size:13px;font-weight:600;color:var(--tb);margin-bottom:14px;}
.bar-chart{display:flex;flex-direction:column;gap:8px;}
.bar-row{display:flex;align-items:center;gap:10px;}
.bar-label{width:110px;font-size:11px;color:var(--td);text-align:right;flex-shrink:0;}
.bar-track{flex:1;height:20px;background:var(--s3);border-radius:4px;overflow:hidden;}
.bar-fill{height:100%;border-radius:4px;transition:width .6s ease;display:flex;align-items:center;padding:0 8px;}
.bar-fill span{font-size:10px;font-weight:700;color:#fff;white-space:nowrap;}

/* MODAL */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:1000;display:none;align-items:center;justify-content:center;}
.modal-overlay.on{display:flex;}
.modal{background:var(--s1);border:1px solid var(--bd);border-radius:12px;width:620px;max-width:92vw;max-height:88vh;overflow:hidden;display:flex;flex-direction:column;}
.modal-header{padding:16px 20px;border-bottom:1px solid var(--bd);display:flex;align-items:flex-start;gap:12px;}
.modal-title{flex:1;}
.modal-title h3{font-size:15px;font-weight:700;color:var(--tb);}
.modal-title p{font-size:11px;color:var(--td);font-family:var(--mono);margin-top:2px;}
.modal-close{background:transparent;border:none;color:var(--td);font-size:20px;cursor:pointer;padding:0 4px;}
.modal-close:hover{color:var(--red);}
.modal-body{flex:1;overflow-y:auto;padding:20px;}
.modal-body::-webkit-scrollbar{width:4px;}
.modal-body::-webkit-scrollbar-thumb{background:var(--bd2);}
.interv-row{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:12px 14px;margin-bottom:8px;display:flex;align-items:center;gap:12px;}
.interv-freq{font-size:11px;font-weight:700;color:var(--tb);width:130px;font-family:var(--mono);}
.interv-info{flex:1;}
.interv-fecha{font-size:12px;color:var(--t);}
.interv-prox{font-size:11px;color:var(--td);margin-top:2px;}
.interv-days{font-size:18px;font-weight:800;width:60px;text-align:right;}

/* FORMS */
.reg-form{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:20px;margin-bottom:20px;}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px;}
.form-row-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px;}
.form-group{display:flex;flex-direction:column;gap:5px;}
.form-group label{font-size:11px;font-weight:600;color:var(--td);text-transform:uppercase;letter-spacing:.5px;}
.form-control{background:var(--s2);border:1px solid var(--bd);border-radius:6px;padding:8px 12px;color:var(--tb);font-family:var(--f);font-size:13px;outline:none;}
.form-control:focus{border-color:var(--blue);}
select.form-control option{background:var(--s2);}
textarea.form-control{resize:vertical;}

/* FOTO UPLOAD */
.foto-upload{background:var(--s2);border:2px dashed var(--bd);border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:all .15s;}
.foto-upload:hover{border-color:var(--blue);}
.foto-upload input{display:none;}
.foto-preview{display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:8px;margin-top:10px;}
.foto-thumb{position:relative;width:80px;height:80px;border-radius:6px;overflow:hidden;border:1px solid var(--bd);}
.foto-thumb img{width:100%;height:100%;object-fit:cover;}
.foto-del{position:absolute;top:2px;right:2px;background:rgba(239,68,68,.8);border:none;color:#fff;font-size:10px;cursor:pointer;border-radius:3px;padding:1px 4px;}

/* BUTTONS */
.btn-primary{padding:9px 20px;background:var(--blue);border:none;border-radius:6px;color:#fff;font-size:13px;font-weight:600;cursor:pointer;font-family:var(--f);transition:all .15s;}
.btn-primary:hover{background:#2563eb;}
.btn-secondary{padding:9px 20px;background:var(--s2);border:1px solid var(--bd);border-radius:6px;color:var(--t);font-size:13px;cursor:pointer;font-family:var(--f);transition:all .15s;}
.btn-secondary:hover{border-color:var(--bd2);}
.btn-danger{padding:9px 20px;background:transparent;border:1px solid var(--red);border-radius:6px;color:var(--red);font-size:13px;cursor:pointer;font-family:var(--f);transition:all .15s;}
.btn-danger:hover{background:rgba(239,68,68,.1);}
.btn-green{padding:9px 20px;background:var(--green);border:none;border-radius:6px;color:#fff;font-size:13px;font-weight:600;cursor:pointer;font-family:var(--f);transition:all .15s;}
.btn-green:hover{background:#059669;}

/* REGISTRO HISTORY */
.reg-history{background:var(--s1);border:1px solid var(--bd);border-radius:10px;overflow:hidden;}

/* EMPTY */
.empty{text-align:center;padding:40px;color:var(--td);}
.empty-icon{font-size:40px;margin-bottom:10px;}

/* TAGS */
.tag{font-size:10px;padding:2px 7px;border-radius:8px;background:var(--s3);color:var(--td);}
.area-tag{font-size:10px;padding:2px 8px;border-radius:8px;font-weight:600;}

/* AREAS PAGE */
.areas-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;margin-bottom:24px;}
.area-card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px;cursor:pointer;transition:all .2s;position:relative;}
.area-card:hover{border-color:var(--bd2);transform:translateY(-1px);}
.area-card.active-area{border-color:var(--blue);}
.area-card-icon{font-size:28px;margin-bottom:10px;}
.area-card-name{font-size:14px;font-weight:600;color:var(--tb);margin-bottom:4px;}
.area-card-count{font-size:11px;color:var(--td);}
.area-card-actions{position:absolute;top:10px;right:10px;display:flex;gap:4px;opacity:0;transition:opacity .15s;}
.area-card:hover .area-card-actions{opacity:1;}

/* EQUIPO CRUD MODAL */
.eq-form-section{margin-bottom:16px;}
.freq-list{display:flex;flex-direction:column;gap:8px;}
.freq-item{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;}
.freq-item .freq-tarea-wrap{flex-basis:100%;}
.freq-item .form-group{flex:1;}
.add-freq-btn{background:transparent;border:1px dashed var(--bd);color:var(--td);border-radius:6px;padding:8px;width:100%;cursor:pointer;font-family:var(--f);font-size:12px;transition:all .15s;margin-top:6px;}
.add-freq-btn:hover{border-color:var(--blue);color:var(--blue);}

/* CONFIG PAGE */
.config-section{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:20px;margin-bottom:16px;}
.config-section h3{font-size:13px;font-weight:600;color:var(--tb);margin-bottom:14px;display:flex;align-items:center;gap:8px;}

/* PRINT */
.login-overlay{position:fixed;inset:0;background:#0a0c10;z-index:9999;display:flex;align-items:center;justify-content:center;}
.login-overlay.hidden{display:none;}
.login-box{width:340px;display:flex;flex-direction:column;align-items:center;}
.login-logo{width:120px;height:120px;object-fit:contain;margin-bottom:16px;}
.login-title{font-size:18px;font-weight:700;color:#e8edf8;text-align:center;line-height:1.3;}
.login-year{font-size:13px;color:#3b82f6;font-weight:600;margin-top:4px;}
.login-empresa{font-size:11px;color:#4a5568;margin:4px 0 24px;}
.login-card{width:100%;background:#0f1218;border:1px solid #1e2535;border-radius:12px;padding:24px;}
.login-card .form-group{margin-bottom:14px;}
.login-card label{font-size:11px;font-weight:600;color:#4a5568;text-transform:uppercase;letter-spacing:.5px;display:block;margin-bottom:5px;}
.login-card input{width:100%;background:#151922;border:1px solid #1e2535;border-radius:6px;padding:9px 12px;color:#e8edf8;font-size:13px;outline:none;font-family:var(--f);box-sizing:border-box;}
.login-card input:focus{border-color:#3b82f6;}
.login-btn{width:100%;padding:10px;background:#3b82f6;border:none;border-radius:6px;color:#fff;font-size:13px;font-weight:600;cursor:pointer;font-family:var(--f);margin-top:4px;}
.login-btn:hover{background:#2563eb;}
.login-error{font-size:12px;color:#ef4444;text-align:center;margin-top:8px;min-height:18px;}
.login-footer{margin-top:24px;text-align:center;}
.login-footer p{font-size:10px;color:#252d40;margin:0;}
.login-footer span{font-size:11px;color:#4a5568;font-weight:600;}
@media print{
  .sidebar,.topbar,.filter-bar,.btn-primary,.btn-secondary,.btn-danger,.notif-btn,.search-box{display:none!important;}
  .app{display:block;}
  .main{overflow:visible;}
  .content{overflow:visible;padding:10px;}
  .page{display:block!important;}
  .page:not(.on){display:none!important;}
  body{background:#fff;color:#000;}
  .table-wrap,.stat-card,.chart-card,.reg-form{border:1px solid #ccc;background:#fff;}
  th,td{color:#000;border-color:#ccc;}
  .modal-overlay{display:none!important;}
}

/* TENDENCIAS */
.trend-canvas-wrap{width:100%;height:180px;position:relative;}
.trend-svg{width:100%;height:100%;}

/* CUMPLIMIENTO */
.cumpl-bar-wrap{display:flex;flex-direction:column;gap:6px;}
.cumpl-row{display:flex;align-items:center;gap:10px;}
.cumpl-label{width:90px;font-size:11px;color:var(--td);text-align:right;flex-shrink:0;}
.cumpl-track{flex:1;height:24px;background:var(--s3);border-radius:4px;overflow:hidden;position:relative;}
.cumpl-fill{height:100%;border-radius:4px;transition:width .6s ease;display:flex;align-items:center;justify-content:flex-end;padding:0 8px;}
.cumpl-fill span{font-size:10px;font-weight:700;color:#fff;}

/* AREA INDICATOR */
.area-indicator{display:flex;align-items:center;gap:8px;padding:6px 12px;background:var(--s2);border:1px solid var(--bd);border-radius:8px;font-size:12px;color:var(--t);}
.area-dot{width:8px;height:8px;border-radius:50%;}
</style>
</head>
<body>
<div class="app">

<!-- SIDEBAR -->
<div class="sidebar">
  <div class="sb-logo" style="display:flex;align-items:flex-start;gap:6px;">
    <img src="data:image/png;base64,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" style="width:38px;height:38px;object-fit:contain;border-radius:6px;flex-shrink:0;" alt="Logo">
    <div style="flex:1;">
      <h1 style="font-size:12px;line-height:1.4;">Mantenimiento Preventivo <span id="sb-year" style="color:var(--blue);">2026</span></h1>
      <p id="sb-empresa" style="font-size:10px;color:var(--td);margin-top:2px;">Planta de Beneficio</p>
    </div>
    <button class="sb-toggle" onclick="toggleSidebar()" id="sb-toggle-btn" title="Colapsar menú">&#10094;</button>
  </div>
  <div class="area-selector">
    <label>&#127970; Área activa</label>
    <select class="area-select" id="area-select" onchange="cambiarArea(this.value)"></select>
  </div>
  <div class="sb-nav">
    <div class="nav-item on" onclick="goPage('dashboard',this)"><span class="ico">&#128202;</span> Dashboard</div>
    <div class="nav-item" onclick="goPage('alertas',this)"><span class="ico">&#128276;</span> Alertas <span class="nav-badge nb-red" id="nb-alertas">0</span></div>
    <div class="nav-item" onclick="goPage('equipos',this)"><span class="ico">&#9881;</span> Equipos</div>
    <div class="nav-item" onclick="goPage('calendario',this)"><span class="ico">&#128197;</span> Calendario</div>
    <div class="nav-item" onclick="goPage('registro',this)"><span class="ico">&#128221;</span> Registrar</div>
    <div class="nav-sep"></div>
    <div class="nav-item" onclick="goPage('graficas',this)"><span class="ico">&#128200;</span> Gráficas</div>
    <div class="nav-item" onclick="goPage('reportes',this)"><span class="ico">&#128196;</span> Reportes</div>
    <div class="nav-sep"></div>
    <div class="nav-item" onclick="goPage('areas',this)"><span class="ico">&#127970;</span> Áreas</div>
    <div class="nav-item" onclick="goPage('tecnicos',this)"><span class="ico">&#128100;</span> Técnicos</div>
    <div class="nav-item" onclick="goPage('config',this)"><span class="ico">&#9881;</span> Config</div>
  </div>
  <div class="sb-footer">
    <span id="sf-total">0</span> equipos &bull; <span id="sf-fecha">--</span>
  </div>
</div>

<!-- MAIN -->
<div class="main">
  <div class="topbar">
    <h2 id="page-title">Dashboard</h2>
    <div class="topbar-sp"></div>
    <div class="area-indicator" id="topbar-area">
      <div class="area-dot" id="topbar-area-dot" style="background:var(--blue)"></div>
      <span id="topbar-area-name">Línea de Beneficio</span>
    </div>

    <button class="notif-btn" onclick="toggleNotif()" id="notif-btn">
      &#128276;
      <div class="notif-dot" id="notif-dot"></div>
    </button>
  </div>

  <!-- NOTIF PANEL -->
  <div class="notif-panel" id="notif-panel">
    <div class="notif-hdr">
      <h4>&#128276; Alertas de vencimiento</h4>
      <button class="modal-close" onclick="toggleNotif()">&#10005;</button>
    </div>
    <div class="notif-list" id="notif-list"></div>
  </div>

  <div class="content">

    <!-- DASHBOARD -->
    <div class="page on" id="page-dashboard">
      <div class="stat-grid">
        <div class="stat-card red">
          <div class="stat-val" id="st-vencidos">0</div>
          <div class="stat-lbl">Vencidas</div>
          <div class="stat-sub" id="st-vencidos-sub"></div>
          <div class="stat-icon">&#128308;</div>
        </div>
        <div class="stat-card yellow">
          <div class="stat-val" id="st-proximos">0</div>
          <div class="stat-lbl">Próximas (≤30 días)</div>
          <div class="stat-sub" id="st-proximos-sub"></div>
          <div class="stat-icon">&#9888;</div>
        </div>
        <div class="stat-card green">
          <div class="stat-val" id="st-ok">0</div>
          <div class="stat-lbl">En Orden</div>
          <div class="stat-sub" id="st-ok-sub"></div>
          <div class="stat-icon">&#9989;</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-val" id="st-total">0</div>
          <div class="stat-lbl">Total Equipos</div>
          <div class="stat-sub" id="st-total-sub"></div>
          <div class="stat-icon">&#9881;</div>
        </div>
      </div>
      <div class="chart-grid">
        <div class="chart-card">
          <div class="chart-title">Estado por Categoría</div>
          <div class="bar-chart" id="chart-cat"></div>
        </div>
        <div class="chart-card">
          <div class="chart-title">Intervenciones por Frecuencia</div>
          <div class="bar-chart" id="chart-freq"></div>
        </div>
      </div>
      <div class="section-title">&#128308; Urgentes — Vencidos <span>más críticos primero</span></div>
      <div class="alert-list" id="dash-urgent"></div>
    </div>

    <!-- ALERTAS -->
    <div class="page" id="page-alertas">
      <div class="filter-bar">
        <button class="filt red on" onclick="filtAlerta('VENCIDO',this)">&#128308; Vencidos</button>
        <button class="filt yellow" onclick="filtAlerta('PROXIMO',this)">&#9888; Próximos</button>
        <button class="filt" onclick="filtAlerta('TODOS',this)">Todos</button>
        <select class="filt" id="alerta-cat" onchange="renderAlertas()">
          <option value="">Todas las categorías</option>
          <option value="ALTO">Alto Impacto</option>
          <option value="MEDIO">Medio Impacto</option>
          <option value="BAJO">Bajo Impacto</option>
        </select>
      </div>
      <div class="alert-list" id="alert-list"></div>
    </div>

    <!-- EQUIPOS -->
    <div class="page" id="page-equipos">
      <div class="filter-bar">
        <button class="filt on" onclick="filtEq('TODOS',this)">Todos</button>
        <button class="filt red" onclick="filtEq('ALTO',this)">&#128308; Alto</button>
        <button class="filt yellow" onclick="filtEq('MEDIO',this)">&#9888; Medio</button>
        <button class="filt green" onclick="filtEq('BAJO',this)">&#9989; Bajo</button>
        <select class="filt" id="eq-freq" onchange="renderEquipos()">
          <option value="">Toda frecuencia</option>
          <option value="MENSUAL">Mensual</option>
          <option value="BIMENSUAL">Bimensual</option>
          <option value="TRIMESTRAL">Trimestral</option>
          <option value="CUATRIMESTRAL">Cuatrimestral</option>
          <option value="SEMESTRAL">Semestral</option>
          <option value="ANUAL">Anual</option>
          <option value="BIANUAL">Bianual</option>
        </select>
        <select class="filt" id="eq-estado" onchange="renderEquipos()">
          <option value="">Todo estado</option>
          <option value="VENCIDO">Vencido</option>
          <option value="PROXIMO">Próximo</option>
          <option value="OK">OK</option>
        </select>
        <button class="btn-primary" style="margin-left:auto;font-size:12px;padding:5px 14px;" onclick="openEqModal()">+ Nuevo Equipo</button>
        <div class="search-box" style="width:200px;">
          <span>&#128269;</span>
          <input type="text" id="search-input" placeholder="Buscar equipo..." oninput="doSearch(this.value)">
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>Equipo</th><th>Categoría</th><th>Frecuencia</th>
            <th>Última Interv.</th><th>Próxima</th><th>Días</th><th>Estado</th><th></th>
          </tr></thead>
          <tbody id="eq-tbody"></tbody>
        </table>
        <div class="pagination">
          <span id="eq-info">0 equipos</span>
          <div class="pg-btns" id="eq-pages"></div>
        </div>
      </div>
    </div>

    <!-- CALENDARIO -->
    <div class="page" id="page-calendario">
      <div class="cal-nav">
        <button onclick="calPrev()">&#8592; Anterior</button>
        <h3 id="cal-title">Junio 2026</h3>
        <button onclick="calNext()">Siguiente &#8594;</button>
      </div>
      <div class="filter-bar">
        <button class="filt red on" id="cal-f-vencido" onclick="calFilt('VENCIDO')">&#128308; Vencidos</button>
        <button class="filt yellow on" id="cal-f-proximo" onclick="calFilt('PROXIMO')">&#9888; Próximos</button>
        <button class="filt green on" id="cal-f-ok" onclick="calFilt('OK')">&#9989; OK</button>
      </div>
      <div class="cal-header" id="cal-header"></div>
      <div class="cal-grid" id="cal-grid"></div>
      <div id="cal-day-detail" style="margin-top:16px;"></div>
    </div>

    <!-- REGISTRO -->
    <div class="page" id="page-registro">
      <div class="reg-form">
        <div class="section-title" style="margin-bottom:16px;">&#128221; Registrar Intervención</div>
        <div class="form-row">
          <div class="form-group">
            <label>Área</label>
            <select class="form-control" id="reg-area" onchange="populateRegEquipos()"></select>
          </div>
          <div class="form-group">
            <label>Equipo *</label>
            <select class="form-control" id="reg-equipo">
              <option value="">-- Seleccionar equipo --</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Frecuencia *</label>
            <select class="form-control" id="reg-freq" onchange="mostrarTareaFreq()">
              <option value="">-- Seleccionar --</option>
              <option value="MENSUAL">Mensual (30 días)</option>
              <option value="BIMENSUAL">Bimensual (60 días)</option>
              <option value="TRIMESTRAL">Trimestral (90 días)</option>
              <option value="CUATRIMESTRAL">Cuatrimestral (120 días)</option>
              <option value="SEMESTRAL">Semestral (180 días)</option>
              <option value="ANUAL">Anual (365 días)</option>
              <option value="BIANUAL">Bianual (730 días)</option>
            </select>
            <div id="reg-tarea-hint" style="font-size:11px;color:var(--blue);margin-top:4px;display:none;"></div>
          </div>
          <div class="form-group">
            <label>Fecha de Intervención *</label>
            <input type="date" class="form-control" id="reg-fecha">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Técnico Responsable</label>
            <select class="form-control" id="reg-tecnico">
              <option value="">-- Seleccionar técnico --</option>
            </select>
          </div>
          <div class="form-group">
            <label>Observaciones</label>
            <input type="text" class="form-control" id="reg-obs" placeholder="Descripción breve del trabajo...">
          </div>
        </div>
        <!-- FOTOS -->
        <div class="form-group" style="margin-bottom:14px;">
          <label>&#128247; Evidencia Fotográfica</label>
          <div class="foto-upload" onclick="document.getElementById('foto-input').click()">
            <div>&#128247; Clic para agregar fotos</div>
            <div style="font-size:11px;color:var(--td);margin-top:4px;">JPG, PNG — máx. 3 fotos</div>
            <input type="file" id="foto-input" accept="image/*" multiple onchange="handleFotos(this)">
          </div>
          <div class="foto-preview" id="foto-preview"></div>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn-primary" onclick="guardarRegistro()">&#128190; Guardar Registro</button>
          <button class="btn-secondary" onclick="limpiarForm()">&#10005; Limpiar</button>
        </div>
      </div>
      <div class="section-title">&#128203; Historial de Registros <span id="hist-area-label"></span></div>
      <div class="reg-history">
        <table style="width:100%;border-collapse:collapse;">
          <thead><tr style="background:var(--s2);">
            <th style="padding:10px 14px;font-size:11px;color:var(--td);text-align:left;">Fecha</th>
            <th style="padding:10px 14px;font-size:11px;color:var(--td);text-align:left;">Equipo</th>
            <th style="padding:10px 14px;font-size:11px;color:var(--td);text-align:left;">Frec.</th>
            <th style="padding:10px 14px;font-size:11px;color:var(--td);text-align:left;">Técnico</th>
            <th style="padding:10px 14px;font-size:11px;color:var(--td);text-align:left;">Obs.</th>
            <th style="padding:10px 14px;font-size:11px;color:var(--td);text-align:left;">Fotos</th>
            <th style="padding:10px 14px;font-size:11px;color:var(--td);text-align:left;"></th>
          </tr></thead>
          <tbody id="reg-tbody"></tbody>
        </table>
      </div>
    </div>

    <!-- GRAFICAS -->
    <div class="page" id="page-graficas">
      <div class="filter-bar">
        <select class="filt" id="graf-area" onchange="renderGraficas()">
          <option value="">Todas las áreas</option>
        </select>
      </div>
      <div class="chart-grid">
        <div class="chart-card">
          <div class="chart-title">&#128308; Estado Global por Área</div>
          <div id="chart-areas"></div>
        </div>
        <div class="chart-card">
          <div class="chart-title">&#128200; Cumplimiento por Categoría</div>
          <div class="cumpl-bar-wrap" id="chart-cumpl"></div>
        </div>
      </div>
      <div class="chart-grid">
        <div class="chart-card">
          <div class="chart-title">&#128197; Intervenciones por Mes (registradas)</div>
          <div class="bar-chart" id="chart-meses"></div>
        </div>
        <div class="chart-card">
          <div class="chart-title">&#128338; Próximas 30 días</div>
          <div class="bar-chart" id="chart-proximas30"></div>
        </div>
      </div>
      <div class="chart-card" style="margin-bottom:20px;">
        <div class="chart-title">&#128203; Resumen por Área</div>
        <div id="chart-tabla-areas"></div>
      </div>
    </div>

    <!-- REPORTES -->
    <div class="page" id="page-reportes">
      <div class="stat-grid">
        <div class="stat-card blue"><div class="stat-val" id="rp-total-eq">0</div><div class="stat-lbl">Total Equipos</div></div>
        <div class="stat-card red"><div class="stat-val" id="rp-vencidos">0</div><div class="stat-lbl">Vencidos</div></div>
        <div class="stat-card yellow"><div class="stat-val" id="rp-proximos">0</div><div class="stat-lbl">Próximos</div></div>
        <div class="stat-card green"><div class="stat-val" id="rp-ok">0</div><div class="stat-lbl">OK</div></div>
      </div>
      <div style="display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap;">
        <button class="btn-primary" onclick="exportCSV()">&#128196; Exportar CSV</button>
        <button class="btn-secondary" onclick="exportPDF()">&#128203; Imprimir / PDF</button>
      </div>
      <div class="section-title">Equipos sin intervención registrada</div>
      <div class="table-wrap" id="rp-sin-tabla"></div>
    </div>

    <!-- AREAS -->
    <div class="page" id="page-areas">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
        <div class="section-title" style="margin-bottom:0;">&#127970; Gestión de Áreas</div>
        <button class="btn-primary" style="font-size:12px;padding:5px 14px;margin-left:auto;" onclick="openAreaModal()">+ Nueva Área</button>
      </div>
      <div class="areas-grid" id="areas-grid"></div>
    </div>

    <!-- TECNICOS -->
    <div class="page" id="page-tecnicos">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
        <div class="section-title" style="margin-bottom:0;">&#128100; Técnicos</div>
      </div>
      <div class="config-section">
        <h3>&#128100; Agregar Técnico</h3>
        <p style="font-size:12px;color:var(--td);margin-bottom:12px;">Gestiona el personal que realiza las intervenciones.</p>
        <div style="display:flex;gap:8px;margin-bottom:14px;">
          <input type="text" class="form-control" id="tec-nombre" placeholder="Nombre completo" style="flex:2;">
          <input type="text" class="form-control" id="tec-cargo" placeholder="Cargo (ej: Técnico, Supervisor...)" style="flex:1;">
          <button class="btn-primary" onclick="agregarTecnico()" style="white-space:nowrap;">+ Agregar</button>
        </div>
        <div id="tec-lista"></div>
      </div>
    </div>

    <!-- CONFIG -->
    <div class="page" id="page-config">
      <div class="config-section">
        <h3>&#127970; Información de la Empresa</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Nombre de la empresa</label>
            <input type="text" class="form-control" id="cfg-empresa" placeholder="Nombre de la planta...">
          </div>
          <div class="form-group">
            <label>Año del plan</label>
            <input type="text" class="form-control" id="cfg-year" value="2026">
          </div>
        </div>
        <button class="btn-primary" onclick="guardarConfig()">&#128190; Guardar</button>
      </div>
      <div class="config-section">
        <h3>&#128274; Contraseña de Supervisor</h3>
        <p style="font-size:12px;color:var(--td);margin-bottom:12px;">Esta contraseña protegerá acciones críticas como eliminar áreas o equipos.</p>
        <div class="form-row">
          <div class="form-group">
            <label>Contraseña actual</label>
            <input type="password" class="form-control" id="cfg-pass-actual" placeholder="Dejar vacío si no está configurada">
          </div>
          <div class="form-group">
            <label>Nueva contraseña</label>
            <input type="password" class="form-control" id="cfg-pass-nueva" placeholder="Mínimo 4 caracteres">
          </div>
        </div>
        <div class="form-group" style="margin-bottom:14px;max-width:300px;">
          <label>Confirmar contraseña</label>
          <input type="password" class="form-control" id="cfg-pass-confirm" placeholder="Repetir nueva contraseña">
        </div>
        <button class="btn-primary" onclick="cambiarPassword()">&#128274; Actualizar Contraseña</button>
      </div>

      <div class="config-section">
        <h3>&#128190; Datos y Respaldo</h3>
        <p style="font-size:12px;color:var(--td);margin-bottom:12px;">Exporta todos los datos de la app o impórtalos desde un respaldo.</p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <button class="btn-secondary" onclick="exportarDatos()">&#128229; Exportar datos (JSON)</button>
          <button class="btn-secondary" onclick="document.getElementById('import-file').click()">&#128228; Importar datos</button>
          <input type="file" id="import-file" accept=".json" style="display:none" onchange="importarDatos(this)">
        </div>
      </div>
    </div>

  </div><!-- /content -->
</div><!-- /main -->
</div><!-- /app -->

<!-- LOGIN -->
<div class="login-overlay" id="login-overlay">
  <div class="login-box">
    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAAB4CAYAAAA5ZDbSAAABCGlDQ1BJQ0MgUHJvZmlsZQAAeJxjYGA8wQAELAYMDLl5JUVB7k4KEZFRCuwPGBiBEAwSk4sLGHADoKpv1yBqL+viUYcLcKakFicD6Q9ArFIEtBxopAiQLZIOYWuA2EkQtg2IXV5SUAJkB4DYRSFBzkB2CpCtkY7ETkJiJxcUgdT3ANk2uTmlyQh3M/Ck5oUGA2kOIJZhKGYIYnBncAL5H6IkfxEDg8VXBgbmCQixpJkMDNtbGRgkbiHEVBYwMPC3MDBsO48QQ4RJQWJRIliIBYiZ0tIYGD4tZ2DgjWRgEL7AwMAVDQsIHG5TALvNnSEfCNMZchhSgSKeDHkMyQx6QJYRgwGDIYMZAKbWPz9HbOBQAAAyoUlEQVR42u29d3xVVdb4vfY+5fb0m5BCQkuCoQvSFQIqiihjSXCwMKCAY0NFxYIm0XEUG6MzoqCoYE9QEJEOAQGpoSchIb3nJrfXU/ZZvz9IfNBnnnmc9wVHfe73r/O52Tl3n732WnvttdbZFyBMmDBhwoQJEyZMmDBhwoQJEyZMmDBhwoQJEyZMmDBhwoQJEyZMmDBhwoQJEyZMmN895P/CQ+bk5HBZWVk/etaysjIsKipi4SkQJqzBv1by8vJoQUGB9uSTT2YjpcP9Pp+mqipERUfYAt5A9RtvvLEfEQkhBH+vY8D/xs0uFhQUIAD8SwEFQ8FXjCbTcJ1OBJ2oA40R0FCrQsQMQv7nOY6IBABoUVER5ObmsrAG/1JamZ+P8GOtI91CRkSSm5tLo6Oj6R//+Efs6Ogw7d773VmmsmjGGAPkCKFARYGXY2NiLpk4cWJLZWUliY6O1nJycrRubf6pZncJmxBCtLCAL6LWdjtGCxcuvAkJvU0KBua99dZb9nnz5gmJiYmsoKDgRwLIGjo0a/KEK45HRlg4S4SFEqTg9XrB7fVoZWcqxm3fvPnAT7SWlpSUcCNGjFCWLVsW3T8r6/VQIPDV1KlTvwEAKCws5H5L2vyb0+DHHnvsUqaR5zXUpnI8B4qi7IqOsEwpKCiQuwQQuWvXriHt7e2Dpk2bNmj8+HHXJiUlpVICAQAIMA2AUqIHQLPP56/Zv//A7gOHDpSkpKacHjF0xOlRo0bZAQA++OADfc/Unht0BsPkkD8AgiBsEATh2XHjxh27gNZI3LVrl7Z79271Nyvg4uJivqOjgxYVFRmsVivLzMxUBg8ezLKzs3/2QyEimT9/Pm8yRbyiofYApZSGQpJGCKhGo1FkKvuEMbZZ1Oly3R7nZUaDPmHe3HkkPb0vaEA/8brZBxUVlU2U+n2BQADizCliakZmsk6nzhZFnONwOGDDxo0gCEJnfEJ8CQH6GaFwnUFvyHE6nTIi8iaTiWqapiKBfyQnJC4aMGCA8v/VOSssLOQeeeQRsampKdj1Ee1aYvC3JmByXqc5ADjftJlmzZrFVq1aFfo56y4AgMvtPUYpHSxJkkwIEQkhoGmaJggCFQQBvF4v9OiRAI8++giYTebVXoBHT+57XBgwYMJf9XocoddTk6bJRJL9ftVffvLAuhcWjrwFQ5GR8LqiyLM2bt4MqqpCTEwMKIoCsixrlFKKiKBpmqLT6QSNac3WuLjeS5Ys0YqKirR/QygEALCwsFDMzc2VAYBnjL1UV1fX77777psxatQo5afLy4WAXiTB0ry8PB4AsLGx8Ra/3/8eIr6HiB/5fL63bDZb7sJXXoFVq1aFrrnmmggAIIhIuhyZf3q/goICDTV1Hc/zQAih57zfc34PAIDb7YKU1CR/3rOLwWwyz/vwHX1e3dEbpsREZd0YFRUxSy/vHgAdn/aiHZ+kGbybsyyRJ24dN2HQZXWVf87On0keRRTnTL/+BjCbLbLT6QRN06DLqQJKKXAcR0wGI+pEsXDEiBFKVlYW929qHN57773m3NxcuaSkJA0Rv/V4vQsPHysRN2/eLOfn5/+2TPQNN9xgcbvdyscffzw6Pj7+c1EUExpbmsBsNIEoiGDQ6097fb7noqKiiubNm2dcsWJF4J95r93OFQBAcnLyECDcYUVRuvqOxGAwQCgkBQx6/dGXlrwwXlK4P7U1P7qrR4/Bp5njywoHG/JkamqvTfLBRzSeubkum6JRA5D9p43TBl11+xtCJI2pO7lzZOaoipEA8HnRV19+bzaZBkRGRkS6XG4ghCClVDMajFRVlOzOzs69OTk5QAj5uc4WmTBhgmn37t2+1tbWaVar9b3TZeUJh0qOsOho87icP+QcvFjO28XSYFi/fr03MzOT9ezZc9eOHTsynE7nV3qdHqqqq+XyijNqbX3dwIiIiEJEXLhixYrAypUrrwQAAyEEf6rJWVlZpKioiHGcmAAAGgAAx1FiMOrlVlu7bcv2bccfXHBfX0q4t1auuHFDcsr0kwa+3Kw1bTQ21x6NQtXNUUMETwVKqcBTqqM8aHoIuWIjOzavNetCjXG9syYcfyifbJEleHvMyMvSn3762fLjx0/WxsXFhXQ6HUHscrEpTcvNzWW7du36WcqRl5dH8/LydJWVlVooFHowNjb2m+3FxQkHDh1STUbjyVum33Koa2t3UTzzixroWLFihVJYWMhNnTrVAwA3h0KhvP6Z/fMbmxrB4XQyj/cEDhsy9NVQKFRWX1/fUlpa+v2mTZtuyM/Pb+4SNOTl5fEFBQXqo48+ejvTtPdVVaWCKFBAcB05fNxVW1ujPfzIgz1TknsCIWSBz7tnjyjURzCXAwVdaq8433GdGhgpU8EoYlAD4AgQghBSmcxTSML2zqT6z7arabffEPHM7Vd/o9OXTEIcfstdc/6U9MJfXmKTJ0+qmjt3jlWvExMCgRCLiLCs2rd/X/S4MePeKC4u5s93FnNyckSXyyU4HA65pKREOe/vWt7SPL0gCM8dOHwETpSWBdP79jWosrKcEILFxcU8AFwUT/qCaXCXGSWISM83/bm5uaxrfaV6vb6AoXpjQo8ebkEQutthbW3t25mZmSd69+5tzMnJua2srIzMnj3bMm/ePKGgoEBdtOjJPwPhPpIliRdFkfoCgbat27d3CAIfmz1pQq+ZM//YEwAWV9d/Pclk9o8JVaxWQZ8Aer1gkDpbBob8NpnTGQHxnF0HCsDx6OZkXx+zmQLzSKTpy+1qrL5i/IkNo8eEGBTMnDkjdep1U5IaGpp6PvTQwvZ2W0dzZFQk5/X5mNFo+tvOnTufys7OVo8cOSIUFxfziEiKiorkbdu2+bt3D9nZ2erzzz+fVlBQMG7i0Ik8pVTncDpZfEK8wefzNfEE1yAimThx4kXbV18oAZPS0lIOALAr0oNdgoYuTwVXrFjBISLvcXoOiYJAJEmClKRkauvowF179qT97W9/GyiK4jsxMTE3FxUVsQ8++MC7YsUKZdGTi/7MNG1ZIBBQRb0ObZ2d9j3f7e0cPGhwUlZWJg4dPPi1qMgoX1HRro3x8ZEPQsd6DW0lgJpXI6oN9AbIALk1AIII/+UUIWgaUY2Al4DGgNcDuOo80LSrTevXM+6+T7dCodlkCg4cmLVi6NCB0C+9X78nnnjGXVdXXxUTHUNcLpcSa417Yd++ffNGjBihZGdnq4QQrK2t7d/Y2Jg+bdo0zM7O5nbs2JEzY8aM70aPHl06duzYx7w+n661rY0TOO6zHrExo2666SZ79/j8qgVcXFzMlZWVqTabbYbdbl/Z1WkNEbnuNt9++62eEKJardaVwWAwQtM01Wq1kh07ijVJVjDzksyrOY7bSCkdNmfO3R9NnjxlQk7OrdfJMlsWDAaZXq/nbR22jgOHDnWMGTVyYFpqUueZ6vKxCxYsOKbISntubraDsLbRrGY71YIeTvO2E5ACYNJzA1RfM/eD+iISIADtDp3V41FHagigaYSqQOmpAwqVXeqEu6YSpyxrbQseWHC8prpqXN++vRxjRo/MXLw4z11dU9sYEREhuN1ujRP4d4qLi2/dt2/ffWcqK3dX1VSffv+DD/YWFBTgke+PDJg0aVJhenr6vaNHj+4niuLjGzdvJZIUevn23NyZV199dcsvkei4IAIuKirSA4BmMpmGx8TEzJEleVNVVVU8IYQtXLjQNGfOHMv69eslj8fzB47nrzlz5oyS3i9dOHHypFZy7BgkJyWR3r37TCOEVBiNxqb09PQct9ezq6PTvkEKyRov8pzd5ew4dPhI8xXjxvaLi4sp8Xl9Y7d8s6W03dZ6JaJQ+ul7hjgTnooLuVo0oiia2noCQNOAarRX0GczAfMAECDdiwePmi5Wr1pkBholoMkKaE4HasQtJ2xabrQi6I+7XI6J33zzTamj0355bGxU/aiRlw189pm8Trvd3mY0GKgsyxCfEP9ZbFzsP44dPXrFmjVfkbZ2W/y8efOXDB8z/ItAILAiNzd3W0RExPp93++H+ob67++fP/+JvLw8Pg+R/hJZrAvqRRuNRtLR0cH8wcA1aWlpB1tbW0e99tprAVmWDe3t7aLACW/W1tVqJrNZ8Hg9NR2dHVTUibzD6WARFsu406dPmwFgzfTp17NAIOimlEOe56gkSf4DBw/ZRo0c1TcmOrJSkeUr33rrrZbCwkJzdFTMtRwnnF3rDjoDbbttJipRo4VwRukMBWRgNTPRSlr0mrcRKCVAiAZAAOIMMsQZJTAIQGNMwGkq4UWeo84OzvbOXwPBYEg9azKZphw5Uh25fPnyOnunfXJCD6u3f//MtBdeWNJIKeePjIyEs1XV7L33P1Q3bd7KeI6nTocz8Kc/zV4IAGgymeYXFhZuaG5tid37/feB1KTEuwkhOGDAACz4hZIWF2QfjIg8IUQN+oPPSaq0+HRpqZSWlqa3xsYFQqHQI1FRUcsdDsdSJPBQU1MTAGLxtq3bHpt+441jOjrsecePH4u78spJkJyY8uempoatGRkZVTP+eHtLS1tb8uhRlynf7d1bERcTF9O/f3q02+8fvHLZsioAAK/Xu9ZoNKe+ub5u8tWR2VNCHtWELjkzKdZ/id4oX2LglQREMAoCcIQD0CgwwoGGHEVfmxCyn0QfEKHD7eXqjlZw9ZxOdyZpIE+zrhDVs7hi3RXDszcpSqDDZLJcAwB4zz33jLZERu7ds29/w2UjRviyLskYdODAYeR5gZiMBnA6nWz8+LGBeXPn6uvq6lITrNY7DCbTy8tWrACmKI88eP/9S7t3Bb+pZMPDDz9sWLp0qdTW1jbJEhGxrfxMuSbLspqRkSEKHL/W6XQujImJqayqqaaiqGutO316xO7Dx0armnr5lKsmF6em9X64w26bNDArqyY2JrYvIm7euXPnmOdffEmXkpLccbq03J89cUJmwOe+e/nby1ciIrHb7UkREeamhjbdoIgGLs/aV3eL2qyoAc3UQix9WkPmSQRkNc7e3pacGKuKKmjE6eNbU+LkGp+7inHM3ers1OToaElmqFGTgSTUbJf7OeukvuNv57mQpqwt0SlPjuwvnalvaEz/+OOPawoKCrR777//CUGvf3Hb1u0Hhg8d0jc6OtqqMURJlojJZPIuff1Vi9/vn93S0nIoPT29tGjdOqiprtn59OOPTV78zDN8QUEBuxgx54tqopcuXSoVFhaS8vLyXaqqHLJarVTU6TgCYH/9wQdnxlpj33Q4XbzRYKaKqj7z2cavk3QGYVxcTNye3d99l/3F55/+0WQ0lgo6XR+73T7D3tr6yKRJkyLGjhpVffDgEa1v376pmsL2Ln97+cq8vDyREIIcxyUQQpWvm6BadmonPaVU5gXgI3qnplr6jx5lTfSNtPaQ+vQfmsBHJiawSHNI7a3b10Pn3D4uDs5cEa1vntGnb9sd0Vb7XXHx7tmGkGdqPA1l9OpFOU8nCdjaxZbxQ0iFrCh+TdMyCwoKtOXLlwvL/tH+CmFQ1j+zf/+GptZOjuc1DTUSCPgDDz/0oAUA1prN5g/T09M3Hj12As+Un/ENHDJ4LjsX+tR+SeFeyECHlpOTwxFC1KVLly6ZdOWVnw4fOkzX3Nw858FXXs8WBd20js5OCAaCZ99f+e72jL79b9MQS0JS8Fqvx7P6gQf+PDguPrHv3r172cQrrnjNGBubIsty4V13zblqxcoPgw11jQZQ2DMAAK2trYiI5OzZs41ms9k5f6D364YQztqyKGP90KGeG6Oja8cbLDVDTBEQZ4kBABNyQFTgmQyg7zJajABIAoATwOek4Gqjmuyl9aqentL3sRQf81i/re17rCMYDK2mlIqyLNcgIsnPzycARay1feajbW22je22dtK/f4bP5/GY/3jrrZCamtpGCLklFAx+5PF60rbv2gnxcfFPTLvqqppf2jRfjFg0ycvLIwUFBYZp10/fOG/+3Jbrr7vuHm/AX1lfVxfLNI0cPlTSLGnqPc319WZAmEA5uqu+pubIW8uWrSmvqLj0wP6D7I47buOMev3zc+fOXfLRRx+1/eXFl/1vvvHm6Y725iu7LI7WXWvV0NDQLzExcTfP43ZCxFn/9Tgo7ni67whTZKifUe9NEwxijyDRxWqqFqFJKhMY+BlRbSaV1vtVsabTr6tpvWtCxezeq0PdCuZxdT5rMEU+2d7ePjklJeV7POf1at1FBz0S077xBf0DLx8/Nnj55WOTnnx8UWRjY+NIg2hIj0uI+2T5eyvB4/MUP/noY5M+++wz7rda8vPfTD4hBC699NLhAGA9efLkVMYY1jc24JYd2+Wn8wtwydKluGHzxueKiopG3ZiTc1UgELjN6fHgG28tl+994KGmz4vWuBARQ6FQutPpvBkR8ZmCgqu64rr8eY6dAADg93k+DSn47tlNC3JOb3lqKGIxX1GxZeiP5/DPm8dYCFzV3rwRpV/NWez1KgVuj2tntxPZfbPuOPm6detuq6ioOOnxeBAR0eXxPFNYWGhFRGnT1i1qwV//6tuwYUOf85Ml/xGBXOD7aYhIjh49WoKI9leXvnnr/Pn3VhAgTrPRJHAcDwF/EOobmp4xmMwb31+5Mo1p7Pnjx4/jmYoz1Vs3bZE3fbtpZ1VNtUcQhG+io6O/DIVCa/OefvoNAODy8/PPT0QgIlJFlVtkhFSj7Ey3ap53SK6VxtOq751nlnx47NiLvc7Lo5P6Pc/Pqi3O648I3Om8LBHzgMdC4DAPKGIOR3KBRUnBt+M4KUbj+QwKUFdYWMh1Z7m6tJhzuVyrr7/++lUZGRnHLRbLbL/f/+Y7y5a9eXNOzrazVVXCoZKjXFxM3KPTpk2reeedd8YUFRWxf5EK/W2V7HQn51NSUvoEFKX8bFUt7Wxv//ae+XM8TrcHz1ZUOewdHV5er9cPHzbsqsTEhME+n1d+5dW/1WZlZfUN+H31cbHRh59++qlbOcp9pNfr75RluVNV1XVGo/FuRBQIIQoicoQQZm9rGxMRF7f71PaVE5PZ8XUl/pSJl18W+anZ1zJEsgWcPkXdpgJfr0ccF9nDPLbGRa7vm/2XDcV5eXx215qImEcJKdAav3tllFlt33bcljB29B8ePOSwt9+YnJy6pTsiRwhhTqfzC4PBMKmysnKU3+/XaYT0GTd69LeImNDc3Hxi7YYNCV6vd89Tjz12RVNT04sAYExJSVnQvZX8PZjpH4T8znvvjVn27nsnl69alfo/tX1y8TObzlRW4OeFhXvuvGtu8InF+Tjz9llH/rFs2S5ERI/Hc8+JEydSEBFtNttd55vM7ni33+8rlVT8auu7Uy8p2/16orvxvc14cKGK6+cgfvcA4p4FiDvvQzy2CL9bPW/2ufDqj8w9QUTS8P1rg1Y8fskAj1/+JBDwV3QnTxCRQ0TidruvVxRF3rp1a5LL5XpKZQzfX/0RLnpqcc3TT+ddmZU1wfz6m29sfvr553u7XK6+iIh79uyZ1/Ud3O/BRAMAQFfpCbnn7rv3r1/y0mWD0tPF1tbWLS6Xq8Hlcu1obm7+Q3dbu619zo4dxe1/mH5D3549UzZ7vR5MSk4eVrxrt+PLtWvLLBbL2ykpKanNzc3TrVbre9XV1ZcTQtSuFBsgInEHQzlEk6ddfsdXeXziww6VwFmIjqJMA0XzyioEZLXDq7Y1tEsrg4pSBgCkY1nZT7crhBvzSPUtiw8t1PHaTcFg6CbEH5pwhBAUBCFbUZQzV199dYuiKBlfFK4JHDt+EpDQ3lQUtl33h8tvfeTBBdf8ZfHiZoPBsM3r9X50+eWXf5yTk2PuSsLQ34WAf/BZCgu5zVVVUmVlpdHj8bxZXV39gqIocmxs7JpAIPDNhg0bolesWNF6+OCBmVu37Uxc+NBDvfwez/eU42lKz7SrPv286Gjx7l2OmJiYbWazeY/X630mOTn5u5qamrTs7Gy1qKiI5Ofnk6S4uLKysvJMkedm9OoFl7W6nGshzkoQgBBCeVCRizbwCWaep6mpyQFEhJzCIu0nzqEWK0nZEUb97Pr6hvTY2NjSH2qCCJGXL19uJISM4Hk+5dixY1FWq/XuJxc9lhJhNhbxlIIUkrUjh0veHXzpyGe7c7uIqAOAwJo1a3wAgCkpKbp+/frp4HfG+es8BwAQDAZ7S5JULklSzenTp3sAAMy79/6Ck6WleOrUqe23zryz4tnnX8D5993fOPPOO9eeLC1liHim638/CgQCnRs2bIg+31wXFxdHybKsNba1PAwAnKfl3Uo8ughx3d2KtPFedO9YWBY6/Ozu05ueeqawsJDDrmXk/HvUNzY+pCiKct4SIAAA7Nu3Ly0QCNTIsnwWERMBAF5+9dWNL7z88t8BAF588eUbb591d1tG1hAcffkk7Jc5eA4ipjPGcN26dcMyMrImXXfdddEAwPXp0yfyYpdL/VIa/MP45eXl0cLCQu7222/X5+XlGfv379969dVXD2KMdfbp0+e71atXm5a/9ffnP/zww+8ioiInT5ky+UxDfV1zj6TEFJETk1aufH9na7stExF3G+40/EkUxfKJEyd+/9prrxkAgBUWFpqHjxhxVOC4AykWVoSIWqON3hGM6REEk8hxwJgSkuNVv0/sYVGnpMccu4IUFGiIPwiZISJNTUlZRyk5zDTtcHl5uYUQotTX1w+/9NJLywCg+u+LFg3eumPHTVu379wXY016VgrJgRdeevlMfHzs3o9XfTzSaDSeAkLBZDb1A4AqAAhs3rJ1E0PcoWl0GAAwo9Go/72Y6B+tybm5uaxv377BgoKCwA033HDVkKGXvm80GkdyHCfefPPNRYQQVQoE5n726efOadddd1VSjx47O2w2R8/eaSMDPr/r/ZUf7D98pOSKWebZCz/66KOrTCZTaMGCBd8QQoQrr776fYvZrFw96/E/GJ/bPAwA6IChdx08VuO53m+xME4vcARBdaG40cmEPw678sViRCCEnCtTJfn5JB8AyIwXekyc+ujNHEBEYmLiss7OzkuSk5N3EEI+MRqNU0bNmPGNw+7Ir6quroyKMm8eMmzIgaDP/0RrW3vJux++E6WPsUwUOK74RMn+9wDgT5RSPLB///p+/foFkpOTEgAALrnkks7uif+7EXA3ZWVlBADA5/M5jWbLHXPmzHtDFMUBOp1uSltb21NvvfVWZWXZ2Xt37d7NHnpowfiOdtsxpii2ltaWHmu/+nL9Z18U1jY2tdw6e/bsDI/HcysiTvT6fE3RkZE5ULXzpm1jb/2LcejlKwgh7NDXi56KcniqGt1ktBeExpg4PiGZCz5nVaQXnMc+iMrPzyOIXWYyPx8KCNFihoxavcc87CmgNDsyMvL22NjYMkmSjuv1+gdXrlq91ev3T1775drF5adPfsFUNdZh6/x7fHx8hsvrmddYUzfowNatjj3FWyZt3LixWZblZYyx59o67HuyLsk0BgIBAgBgs9nI706D/zsCeFwuNaFHwoMzZ97+EMdxUxISEl44efLk8PdXvfv512u/fru8rCzu2cVPx3/60SeHD+w/kFlScvhoXV3d8zNyb4mtqa39UtDpzkgqa9Xp9bu8dnuO4akvvCZT/FyZREZCXrMxU+dPykjTHbC1+xx5xyCz3c8/IzP6LaIW5YWQ6ZynjwDn1mJMee3dfiFzjzRRb7ybpE3z+ny+2zwe705Vw0tdHm9wylVXTq6vqt64a9eO/YOGDl8ry/I7u3Zuz1I0tkQOhTKfey7/k5MnTyZ0dnbOGTt+bBHHUefll1/+4ZSrrlwSCkmgaZr8uwh0/BweuOYBndJL6QU8nyxSIevNN5f+Q1GUVZIkXWE2m/vedtttCR6f7+Ebrr9h6vqvvzlrNhu+ffnVV8eYzebcqIiIEFPYHo4E37YIlm2+rnsmfH0213M6+DmhlMjJZJES/ee10GNsZdAXsp1lwrVDrnzl6D/tzBEUYARRolfu/8TXZJqpVdWDSe641fPFnC/OOVqbY0AePx1E0wwNYJzDbjeXlZVJX65ZM8jl891LkIihgO/1/v37186fP/+2xMTE1YqitBCB/CnRmnj65tzckQGvtzIUCtUVFRUF4f8iiEhPnz5tliTJ43A4lnR9POyuuXNXnDx1SkFEyRcM1aEqzcVXBpvORVMKJxk/O/NO1C5PY68lq2bErTzxtPj4ESSzNykRn9d74bInYv1b7/8rnliE3q0PBCu+eXgqAAAemSf8EDZcfkQAALC+/ME1pk+aNXLH1xKZv1vT3br6Oev1eTcZ52ypEh7fVAB5HwwFAMCafWnI2AsKYpPH48W169bVDxo06IruQIbX613n9XrX/1q3ML94tKt7TS4sLARCCGtubp4ZFRX1N5PJlBIIBB4QRfEV4LijnNuxmETFboabHumvz529QDQmTJMjrCkaBeDONIPp7JoMCTOe9/vMM9DRFhRGjTIY+pIT7j+kDnXsfOwpI0j5OrMgtNjZon3e5tdycrKQzE/iYMV8Jeq1lUOUPtcdkfbXcayxUUFLnCgEO7+xtO5d5Em7rowadGCcPAiYhZwJum0r1Zsz30UAv+R13y+YIx5XJMnY0dFxV8+ePb90Op1NjLHFcXFxH3aFVNWcnBz6c19U/10J+Kf9KC4u5iZOnKitXLmyZ25u7ltGo/E6v9//UGRk5Btw918zom+6/WUmGaYrHgpyYgxQh5vBwRNIGuqDfbY+0bv22hc2y+aUSwnPU97Z6BbHDgsKCbpK58yMCWd2P9/bGOy8w6AXx5Uq9NGJK4aXkaJcZr7xpdF42cSdmj9UplS1DVYtsQIyReNY6GzfAy+Mr73s0XKFGKIEi4mQYYM4wSCCYPBLmj70jmda+tMIIDtd7n9ER0bM8/l8f9m+ffvK2NhYf1tbm6O0tBQvxstk/6mE/88xwyQ/P58MGDCAlJaWknPOa77WXUfd/YaA1+tdJep0WQFn+yWR1uQz1sJjL0i6tKcCZ52glJSowDQmDOhH1bN1qKk8FUyWM4O8La5KTmcheiPVOeuK+fYj870P39lgemLjp9a/bKnsP2HzEIA3njuXuivkoCiXGaYtvZZZEovokdKFga/uejty+isTgwL9UDEmpBHZk6ooPAe8vgxEyzjV62Ww4zumaKiR6ChBGJaxIOpb++zY9pKnHVGR8zs6Or6Ni4v7eurUqRadTvfQT5efXbt2UQCAjo4OzMnJQThXP/6LbJUuhoBJdwz3/LLQrmv8yf4Yukx0DABEXnvttW8KojjybHNzn4HXL8W4l4qP+719h2hffeVDmTNDbCpPiMorFW0AnB64qGig9qq2QkTNeHthJu+sKx732W3XbiEgdaX2bobbP34xcubg6kHwxPg7JvRubJmXw6zTX7wzYOnxFmdvutn77aNbhh9BoWQE2ZV2Wc7o9v4528AcNzAQ0csgBDwdYE7kNE3l0BhxzuBpGrDvTkHIIOv4q675e8LS70dZrdY77R7P+BiLZa/X6zXu27fvdaPRaN+xY4e9awJr/9vkv1gCv+gmeuPGjTpKqcnpdEYTQqyBQCBB07REo9GYEpLlXgLPR2iapjMZjbrJkyfzDo/nib5paXuTbnt1jltIm4ZOV7vJfuJjLabn2FBEalD1uSQgiEpIZhzPaUrQfwi2P1HODb7renZy5TYACJ03cudeRBr9zAQ4te8M+He2AwDAkHuHijExQbn4LxU/tJ2Qx8PuAhUg0wJT786CjY8dtYx9rA9Lzuit6qIF3me3UoOg52R/IolKFPRV35d4IjLGCH0zBvb0nPr89PsL3m9u65hu1Asvl5eXy16Ph2ia5qOUdiBikyAI9TJj9SpjrUow2G6xWGyKovimTp0q/VbWYJKXl0eampqioqKiek+cOJELBoORer1eHwgEIhhjIAiCFAwGNVmWQ6qqNpeXlzu3b9/umD9/vrJgwYJ/60G5rs4riNySJUsSFy1a5AYAS2lpqadXr15mk8kklpaWthUUlLHCwsusAL24oqKijqSkpJ7jxo1zA4Bj//7jiWPGDOVOnTrlHTJ4sBMBycqVb8bNmfOgAwAIJUSl8OO31n8u7733niU6OjpSFMUoAIiLiY8xe53eGMbQKBp0GiGarNebvHIw6LPZbL7NmzfbPvzww6r/hCP2/zsv/M8IBoO9AoHAmM7OzqvWr19vBADYu3fv1FAolOf1enMAkXiC0twOh3PD9u3F97e2dayxO13lQVkpdXu8jZ0Op6vibPX9KmONXq83GAgEERGxqqpqvtPp3IeIksPheOpcvjhgVxRFampq6hkIBE4pqqoePnxsXHV1dTEiSi6XqxgA4OTJkwl2h6M9JMkOVVUftjmdwxxOV0dFVc03H6/ZkNbWbit1eX17PP7AFrvDUeTxh/6wdceeXL/f/6Lb7Z6GiFxHR8fwxtbWSQcPHuzxwQcfRCGi4d/ZLv5a97EEAGDr1q1JNpttbigUerq+vv5qAIC1a9dGeTyercFgsL6iomJlYWEhV11dPR7Po6amZhQAwNmzZz9DRAwEAt68vDweET9GRDx48OA7nZ2dzu72jDH0+/1tDQ0N9yGihoiaLMuNkiQ1lZSU3O5yuY513adyy5YtJkRs0jQN/X5/MiKeQERsaWkZ3tnZuRkRUVEU+eTJk9E2m23qed+RL8vyZV31YQfWrFnTB39CMBhcWlJS8gYiot/v7wAAIsvyR10T7R92u71YVVVFkqRG77lgxyGbzfYmAEB5eXm22+1+CRFftNlsD1ZWVmadP5a/NgFzAACbNm3K6X54l8u1FwCgqanpyu7Pzp49+xUAQGtr611dgxhERLW9vX0WAEBVVdV7iKggIjY0NFyDiC8xxtTjx48/+/XXX/fzeDz/QES1ra3tvVmzZukR8TLGmObxeGrO647Y2dlZyxjTNE3Dlvb2mxhjpYwxDRGTGWMnuibFIET8rOsam5ubZzocjlcYYxpjTFNVdbEsyyO6rr9bvXp1b7/fzxBR8Xq9E48fPz4+GAz29ng8z3b3ubKyckIwGFyCiKyhoeGN+vr6FaqqNpw/Kdxu99GKiorrGGM/miySJKl+v/+BC63JF9QkMMbkrmS3bDQahy1fvtxosVjGdy1jmqZpKgCATqfLAAB0OByNiMgJgjAAzjXgEZAHALRYLH+WZdlAKeU4jmPTp0+vsphMDgDgjEZjYNWqVSFFUSillOhE0aQoys2hUGiq1WoVBUHQKKWEEAJRFss8SilHKSUAAJRS6NI00vX8BADAYrHMNZvNUyilpKst7WpPOI4jLpcLCCEUALiWlpbA0KFD9xsMhlqLxaJ17UbQarXeY7fbdYhIjUajLi0tbZ6maTcCgMYY83m93vFVVVW5kZGRcyilqChKfW1t7UPBYHCbKIocz/NLT58+nUoI0f7V8vYf2yZ1zTweACRBEIzjx4+/mRByeXeiv3v7JIpifwAgPp9va1xcXLrBZMgCACAcwa7X/4jZYpmoKMpZAACO47i8vDwqa5rAA4AsyxwiEkVRSDAYBJWxeItOt0aWZRgyZEiay+PRAsEAypLsMBqN2S63G0RRlGJjYqjD4QBeEECv04HT7SYEEZim1VFKJnp9PlRVpdNsMscRjmPIzrlXHMeB2+3WQlKIiaLI9UvvdzAYDIJer49WGJMF7lxNntlsnuL3+48TQsBoNFJCCAiCQACAchzHEUKqhg8f3l5TU6NHREIpPdOnT583Ojs7yw0Gw5Ucx3GSJCUDQMOAAQPIr07AmZmZjh/SRQDQq1evRTqdLlmSJE2n01GO4+QuB6ufqqoaAGxobmm5R5KlQQAAzU3NiiCIIElSpSzL/QKBwKXR0dHQ2NhICwoKtFmzZ6FeZ4DGhgaMi4vD1s5WtLV2gMvlcrtczpWRlsj2QYMG+Wpra3jGGDJF/SIqOurekCSBTqcLxsbEQG1DPZjNZkhOTYP6hjpARNCJ+s9cLucTAODwBwIHevfqNa2hodHSKzWVUIEDn9fHL1682Hns5AkvAYgSeOFIdEwUuJ1uLiI6AjWGoCpKrca0NEVVhnfaOwHIueOXFEXpPpLJsH379p6I2FFVVUUIIcBxHN9VPcIBAOE4Dk0m0wWtvLygAuZ5HhERQpLkC4WCCgAZYOuwKYi4i+f5SZIitSAiOXzkcBoiuASe9/iDAb9ep0+qrKzUVZytCBFCIBgMrZNl+QYAyJQkCWT5XKZN0zTgBR7gnJkFAQQ0GU3g9/s7p18/fWF3P3JvnUEMBgO1tbUXinr9NTqDvjfBc9sPvU4HBr0eQJZBr9czs9kMAuV3BIOBWykhjT6f/2h0dPS0M2cqomw2G01J7dl9W03geWCMQc+UlGsiIyPtAAC19fWiqBPB6/Ws9bg90ynH9ZVkGURBAACATrcb2luawe/3gwIKEEK00tJSW2NTE8iKgv369FFdLhfyPA9ACAkGg+RXJ+CioiIAADBEGKSz1VXg9XrtZrNpjSQrj7pcrvLUninbKc9N4jjB09LSEivqdEZN00wGg2EfFTjQi3qQZbmvKOqlmJgYUFWlLhTiCg1G0zOKLGuCToddE0gTBEH90YGgBFSDXh9RVVW1KDIyEg4fPrybcpzXYrGw73btbuiZ2vOLiMjIRR63RwYA4AVBE0WRiaKIlBDNaDAywoNNr9d9CkDbpGBQr9frVaPBoPj9fuR5XtUb9AoAoCiKDDVkHo9n8NatWyvMZrNT5HkWGRGBmqZWEsJ9ZjDoF8uyDBx3bhIqgQAIvACCIIBwzrABz/NBRVXA5/MRRKRNTU3U5XGDIsvA1Av7hgu9wBqsISIIgmBJ6pH0gcgLEBsTu0sn6JqiIqNQJwiy3W5Pi46O1gReaFUk+SsKtCwmJkZFxP6UgqzT6YBSanA5XO9TABIfH091wrkDNijlTVERkbzI8+autVxMsMbzSYlJ1h49erwUFxf3UkJCwhU6nheSevTgEhPjLEwNvM9RQg16MSoUcnHAWER0ZCRnt7fpBI5aYqKiOcq0xLLTRS8dPvjFe5mZ6TqTwcjrdGKEx+MRE+ITeEVRe7a0tBj0en1EVHQUJ6vKzsFDhjTpdLpXO+z2gNFgJPZOezwv0eWMMWYwGFSBExgAgNvtRo7nmE4UNaFLq0W9njOZzWg06lVCiKbX6wMmsxl0ej0aDIZfr4AFEEAQBBRFUW+xWCoAcTVP6SYqUDQajIQXRQSOuyQ1pSfHUbpx8ODBNws8v8YaF8dzHDeW4ziBoxQYU0zjxo2rR00tYopUo6r+eiwG3mwkR0Ihb6Hfa9+LOcB5GyobpGBwQSgQuLfsdNldxTu+u7upurMoJWHALB4MUxoa/nh24MDhVXt2VlxResIx2WCIr6uoIDfu2109+ZtvUk/4/T0XhUIwJTIy9kBuboFv9uyCkADmDcDgz4DwoahpjY0Nde967B2bWkt2gRzyfS2H/N/LocBJo0FsIKDKIlFVSQqC1+1OzxiS0cRU9UDP5BReEAQTAEBnZycfFRXFxcXEUbPZTM/tNhRJEASCGmSWlpYOs9lsEwkAEwWRBIMXtibggicbTEYTQUQ9AMRs3br1QYfDEbjvvj8/oMgSEpQlkdMifF73UZ7XivF0nniws3W9wxHb1N5uP1XfYaqTCX17hiO9CQCgd+9+uT++e/InAPDJD3OzaEQDALx5fotrKvvplrxe1XnVDGD3PNLHcucjw6LjYOKx19ZB9IdFUYMb3f0D3haoMVui+5e0Ox3SQNgbAWDaW5+ZdOwYQB+lZznwcOK8W8477zrnv0d6RXh3e+hLEa9QAQAa2uHO5CR5XCgUsmEe0KKmarsnKWELoVySTqdKxcUTeGTyBz6P505rvLVXIBA4yhgDo9EILqer1efzVXYFOy5IqvGCLOjdx/C5OjpG+BV5c0iSKvr06j2NEOIEAKh3YTTKoO8VL7T+q/O+ti2CSKcM5skThaj6luikvhaTTtIcCe4AlxBnFE0Sk5IjI4ne52M9IgwiuL2yNcLADIQAH1Ag1mzkUGUocLwqCnzX+FANgKMAlAAwBtAdQ0Dt3DUhAIoGyAAUBNCooPCEU/w+RdPx6FCRYxroHUiYDwg6EVnA6xX9JiPfzhmk9hDT7DJ6mk0mcNS2JKqxgda23g+D638bM3sAe/qc7Q8Efe5xClOjoqKiqnyB4HOX9OtX0v2q6q8um7Rx40adwWAwZGdnuwAArrnmGt11VyjmgYk7hFC7KTYiJjaBBcQkyrF4QVMTrMZgBKUQTzRdrKqySIEyPVMg1iwoKKlM5DRAQASLQXPzBJCihogMCAGVqYwBgKIwShXgKAJhjBGiAWiInKaqCCoSQI0CAQCeQ8Z+eL+eAgUASoEhgKaomkgoUp5H4KlGeKqBTgSNIqM8QUIJ5TUEnnLAEcIRIBQYEs4RxBjkKaKOYyIHQVXigOh0AV6kHbZOQjkh1MqJfIfFbG6vd4QUSaIOUeRaZTA4z9Y2Nq95xVu3GUCCn5xYfyFP37kocc/u/OboISlJt+VkJFw9tlNw12KMx++HgFPhYy3E7wsGpTHpzOmRFFbVAlpFs1WyGkV/zWk3aae9pUNuQdm928cAjio/7i6eM8+zVD2c/VqA76f7AC70cUQUAA4JAJ+JEBtPIfpxGao46dx3nz9kN3MANgLgIw9cY6UxCa2GPokSd+ctKeqnaypj06P9QkoccrooIz3ZSKJEXtAho1y9C3SiIVJK7R3t2FkVX/3kk586u8K9eKF/MoBcJOFe0Bmond9PBHgkd7Te1GdMhjckDedFXarGtD6yLPdWNRJFEXkATQWgEiFEAkBGCMVzUUdKDpUcY6GgRIAgnjuWGHggRCRIdIQSngDyCCREKanXC/zxCJPpWJRFLJMbbbVZBw5I+eel8ygA/tpzexf9QPC8PCD5+QBFRV3fVQSQkwWYDwD5+f8k90n+6eW/HMf7nrgvVggJvTWAAYzBSCBkEGpskKgTowRBBEQEpiEwxuDQoSMgKwpQygEggqYxQI11EICThJCDHM8d54A7JcdaGko2bAj83PHD/62n+efaFg34r3EozQIsKICLWoz3m/3dpO5g/P9U2PbGG2/ompub+6kqDmVMu0zV5LEaYvrRY6cUWZZLBYHbS4Ae1vFieXb2uNr/4YCU7nNH/iMVkf+nBfzPBFE2YADJOlfQp/0zwT/44IMJDQ0N6rp16+z//RY53IQJNhIfH49FRUXdAv3N/2DW7/mXz0heXt4Pab+faCiZMGECd06YWQhQ8LsQ5v95un/cKjwSYcKECRMmTJgwYcKECRMmTJgwYcKECRMmTJgwYcKECRMmTJgwYcKECRMmTJgwYcKECRMmTJgwYcKECRMmTJgwYcKECRMmTJgwYf4N/h98tjSfsXz5cgAAAABJRU5ErkJggg==" class="login-logo" alt="Logo Mantenimiento">
    <div class="login-title">Mantenimiento Preventivo</div>
    <div class="login-year" id="login-year">2026</div>
    <div class="login-empresa" id="login-empresa">Planta de Beneficio</div>
    <div class="login-card">
      <div class="form-group">
        <label>Usuario</label>
        <input type="text" id="login-user" placeholder="Nombre de usuario" autocomplete="off">
      </div>
      <div class="form-group">
        <label>Contraseña</label>
        <input type="password" id="login-pass" placeholder="Contraseña" onkeydown="if(event.key==='Enter')doLogin()">
      </div>
      <button class="login-btn" onclick="doLogin()">🔐 Ingresar</button>
      <div class="login-error" id="login-error"></div>
    </div>
    <div class="login-footer">
      <p>Desarrollado por</p>
      <span>Miguel Gutiérrez</span>
    </div>
  </div>
</div>

<!-- MODAL DETALLE EQUIPO -->
<div class="modal-overlay" id="modal-overlay" onclick="closeModal(event)">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-title">
        <h3 id="modal-title">Equipo</h3>
        <p id="modal-code"></p>
      </div>
      <button class="modal-close" onclick="closeModal()">&#10005;</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>

<!-- MODAL EQUIPO CRUD -->
<div class="modal-overlay" id="eq-modal-overlay" onclick="closeEqModal(event)">
  <div class="modal" style="width:680px;">
    <div class="modal-header">
      <div class="modal-title">
        <h3 id="eq-modal-title">Nuevo Equipo</h3>
        <p id="eq-modal-sub">Completa los datos del equipo</p>
      </div>
      <button class="modal-close" onclick="closeEqModal()">&#10005;</button>
    </div>
    <div class="modal-body">
      <div class="form-row">
        <div class="form-group" style="grid-column:1/-1;">
          <label>Descripción del equipo *</label>
          <input type="text" class="form-control" id="eq-desc" placeholder="Nombre completo del equipo...">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Código</label>
          <input type="text" class="form-control" id="eq-codigo" placeholder="LI-BOM-01">
        </div>
        <div class="form-group">
          <label>Categoría *</label>
          <select class="form-control" id="eq-cat">
            <option value="ALTO">ALTO — Impacto crítico</option>
            <option value="MEDIO">MEDIO — Impacto moderado</option>
            <option value="BAJO">BAJO — Impacto leve</option>
          </select>
        </div>
      </div>
      <div class="form-group" style="margin-bottom:14px;">
        <label>Área *</label>
        <select class="form-control" id="eq-area-sel"></select>
      </div>
      <div style="font-size:11px;font-weight:600;color:var(--td);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;">Plan de mantenimiento</div>
      <div class="freq-list" id="eq-freq-list"></div>
      <button class="add-freq-btn" onclick="addFreqRow()">+ Agregar frecuencia</button>
      <input type="hidden" id="eq-edit-id" value="">
      <div style="display:flex;gap:8px;margin-top:16px;">
        <button class="btn-primary" onclick="guardarEquipo()">&#128190; Guardar Equipo</button>
        <button class="btn-secondary" onclick="closeEqModal()">Cancelar</button>
        <button class="btn-danger" id="eq-delete-btn" style="margin-left:auto;display:none;" onclick="eliminarEquipo()">&#128465; Eliminar</button>
      </div>
    </div>
  </div>
</div>

<!-- MODAL AREA CRUD -->
<div class="modal-overlay" id="area-modal-overlay" onclick="closeAreaModal(event)">
  <div class="modal" style="width:460px;">
    <div class="modal-header">
      <div class="modal-title"><h3 id="area-modal-title">Nueva Área</h3></div>
      <button class="modal-close" onclick="closeAreaModal()">&#10005;</button>
    </div>
    <div class="modal-body">
      <div class="form-group" style="margin-bottom:14px;">
        <label>Nombre del área *</label>
        <input type="text" class="form-control" id="area-nombre" placeholder="Ej: Sala de Proceso">
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Ícono (emoji)</label>
          <input type="text" class="form-control" id="area-icono" placeholder="🏭" maxlength="4">
        </div>
        <div class="form-group">
          <label>Color</label>
          <input type="color" class="form-control" id="area-color" value="#3b82f6" style="padding:4px;height:38px;">
        </div>
      </div>
      <input type="hidden" id="area-edit-id" value="">
      <div style="display:flex;gap:8px;margin-top:16px;">
        <button class="btn-primary" onclick="guardarArea()">&#128190; Guardar</button>
        <button class="btn-secondary" onclick="closeAreaModal()">Cancelar</button>
        <button class="btn-danger" id="area-delete-btn" style="margin-left:auto;display:none;" onclick="eliminarArea()">&#128465; Eliminar</button>
      </div>
    </div>
  </div>
</div>

<!-- MODAL EDITAR REGISTRO -->
<div class="modal-overlay" id="reg-edit-overlay" onclick="closeRegEdit(event)">
  <div class="modal" style="width:520px;">
    <div class="modal-header">
      <div class="modal-title"><h3>✏️ Editar Registro</h3></div>
      <button class="modal-close" onclick="closeRegEdit()">&#10005;</button>
    </div>
    <div class="modal-body">
      <input type="hidden" id="reg-edit-id">
      <div class="form-row">
        <div class="form-group">
          <label>Fecha *</label>
          <input type="date" class="form-control" id="reg-edit-fecha">
        </div>
        <div class="form-group">
          <label>Frecuencia *</label>
          <select class="form-control" id="reg-edit-freq">
            <option value="MENSUAL">Mensual</option>
            <option value="BIMENSUAL">Bimensual</option>
            <option value="TRIMESTRAL">Trimestral</option>
            <option value="CUATRIMESTRAL">Cuatrimestral</option>
            <option value="SEMESTRAL">Semestral</option>
            <option value="ANUAL">Anual</option>
            <option value="BIANUAL">Bianual</option>
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Técnico</label>
          <input type="text" class="form-control" id="reg-edit-tecnico" placeholder="Nombre del técnico">
        </div>
        <div class="form-group">
          <label>Observaciones</label>
          <input type="text" class="form-control" id="reg-edit-obs" placeholder="Descripción del trabajo...">
        </div>
      </div>
      <div style="display:flex;gap:8px;margin-top:8px;">
        <button class="btn-primary" onclick="guardarEditReg()">&#128190; Guardar</button>
        <button class="btn-secondary" onclick="closeRegEdit()">Cancelar</button>
        <button class="btn-danger" style="margin-left:auto;" onclick="eliminarRegistro()">&#128465; Eliminar</button>
      </div>
    </div>
  </div>
</div>

<!-- MODAL FOTO VIEWER -->
<div class="modal-overlay" id="foto-modal-overlay" onclick="closeFotoModal(event)" style="z-index:2000;">
  <div style="max-width:90vw;max-height:90vh;position:relative;">
    <button class="modal-close" onclick="closeFotoModal()" style="position:absolute;top:-30px;right:0;color:#fff;font-size:24px;">&#10005;</button>
    <img id="foto-modal-img" style="max-width:90vw;max-height:85vh;border-radius:8px;" src="">
  </div>
</div>


<script>
const LB_DATA = [{"id":1,"categoria":"ALTO","descripcion":"AFILADOR DE CUCHILLAS JARVIS 102901 115 V [LI-AFI-01]","codigo":"LI-AFI-01","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-01-25"}]},{"id":2,"categoria":"ALTO","descripcion":"BOMBA MULTIETAPAS VSE 5 16-50 BARNES [LI-BOM-05]","codigo":"LI-BOM-05","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-02-24"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-02-26"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-06-05"}]},{"id":3,"categoria":"ALTO","descripcion":"BOMBA SANGRE NEUMATICA 002 HUSKY [LI-BOM-04]","codigo":"LI-BOM-04","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-03-12"}]},{"id":4,"categoria":"ALTO","descripcion":"CAJON DE NOQUEO MIXTO BOX GS INGENIERIA [LI-NOQ-01]","codigo":"LI-NOQ-01","intervenciones":[]},{"id":5,"categoria":"ALTO","descripcion":"CALDERA 1 TERMO VAPOR 005-12 / 150 BHP [LI-CAL-01]","codigo":"LI-CAL-01","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-04-02"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-06-09"}]},{"id":6,"categoria":"ALTO","descripcion":"COMPRESOR KAESER 1 AS20 125 PSI [LI-COM-01]","codigo":"LI-COM-01","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-15"}]},{"id":7,"categoria":"ALTO","descripcion":"COMPRESOR KAESER 2 AS20 125 PSI [LI-COM-02]","codigo":"LI-COM-02","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-15"}]},{"id":8,"categoria":"ALTO","descripcion":"COMPRESOR Y SECADOR KAESER SMT10 T [LI-COM-04]","codigo":"LI-COM-04","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-02-25"}]},{"id":9,"categoria":"ALTO","descripcion":"CORTA PATAS 1 JARVIS 102879 [LI-COP-01]","codigo":"LI-COP-01","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-10-03"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-10-03"}]},{"id":10,"categoria":"ALTO","descripcion":"CORTA PATAS 2 JARVIS 102877 [LI-COP-02]","codigo":"LI-COP-02","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-10-04"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-10-04"}]},{"id":11,"categoria":"ALTO","descripcion":"CUCHILLO NEUMATICO 10 JARVIS 161984 [LI-CUN-10]","codigo":"LI-CUN-10","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-13"},{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-03-07"}]},{"id":12,"categoria":"ALTO","descripcion":"CUCHILLO NEUMATICO 9 JARVIS 161947 [LI-CUN-09]","codigo":"LI-CUN-09","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-13"},{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-03-16"}]},{"id":13,"categoria":"ALTO","descripcion":"DESCENSOR DE CABEZAS [LI-DEC-01]","codigo":"LI-DEC-01","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-02-03"}]},{"id":14,"categoria":"ALTO","descripcion":"DESCENSOR DE GRILLETES 1 [LI-DEC-02]","codigo":"LI-DEC-02","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-02"}]},{"id":15,"categoria":"ALTO","descripcion":"DESCORNADORA JARVIS [LI-DES-01]","codigo":"LI-DES-01","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-11-18"}]},{"id":16,"categoria":"ALTO","descripcion":"DESOLLADORA [LI-MDE-01]","codigo":"LI-MDE-01","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-22"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-01-24"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2026-04-04"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-08-25"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-11-19"}]},{"id":17,"categoria":"ALTO","descripcion":"DESPERNANCADOR [B2SCA-DES-01]","codigo":"B2SCA-DES-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-01-01"}]},{"id":18,"categoria":"ALTO","descripcion":"DESPEZUNADORA ELECTRICA ASERAGRO [DS-DES-03]","codigo":"DS-DES-03","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2025-04-01"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-04-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-04-01"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2025-04-01"}]},{"id":19,"categoria":"ALTO","descripcion":"DIFERENCIAL ELECTRICA DE CONTINGENCIA 2 TON [LI-DIF-03]","codigo":"LI-DIF-03","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-02-01"}]},{"id":20,"categoria":"ALTO","descripcion":"ELEVADOR DE POLEAS PLATAFORMA 01 [LI-ELP-01]","codigo":"LI-ELP-01","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2013-01-01"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-04-22"}]},{"id":21,"categoria":"ALTO","descripcion":"ELEVADOR DE POLEAS PLATAFORMA 02 [LI-ELP-02]","codigo":"LI-ELP-02","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2013-01-01"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-04-23"}]},{"id":22,"categoria":"ALTO","descripcion":"FRENOS AUTOMATICOS DE RIEL [FA-LBE-01]","codigo":"FA-LBE-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-12-23"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-09-24"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-05-09"}]},{"id":23,"categoria":"ALTO","descripcion":"INTERCAMBIADOR DE CALOR 02 ALFA LAVAL [LI-INT-02]","codigo":"LI-INT-02","intervenciones":[{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2026-05-17"}]},{"id":24,"categoria":"ALTO","descripcion":"IZADO DE BOVINOS MOTOREDUCTOR SEW 9.2 KW [LI-IZA-01]","codigo":"LI-IZA-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-04-22"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-04-02"}]},{"id":25,"categoria":"ALTO","descripcion":"IZADO EMERGENCIA [EM-IZA-01]","codigo":"EM-IZA-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-24"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-03-24"}]},{"id":26,"categoria":"ALTO","descripcion":"MAQUINA CORTA CABEZAS [LI-CAB-01]","codigo":"LI-CAB-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-06-10"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-03-18"}]},{"id":27,"categoria":"ALTO","descripcion":"MAQUINA LAVA LIBROS 02 CUAJOS ASERAGRO [VB-MLV-05]","codigo":"VB-MLV-05","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-04-17"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-03"}]},{"id":28,"categoria":"ALTO","descripcion":"MAQUINA LAVA LIBROS 01 FRINOX [VB-MLV-02]","codigo":"VB-MLV-02","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-04-17"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-03"}]},{"id":29,"categoria":"ALTO","descripcion":"MAQUINA LAVA OREJAS GUALDRON [VB-MLV-03]","codigo":"VB-MLV-03","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-06-06"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-06"}]},{"id":30,"categoria":"ALTO","descripcion":"MAQUINA LAVAPANZAS 01 FRINOX [VB-MLV-01]","codigo":"VB-MLV-01","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-04-17"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-03"}]},{"id":31,"categoria":"ALTO","descripcion":"MAQUINA LAVAPANZAS 02 FRIGOTEC [VB-MLV-04]","codigo":"VB-MLV-04","intervenciones":[]},{"id":32,"categoria":"ALTO","descripcion":"MULTIPLICADOR BOOSTER REGULADOR SMC 230PSI [LI-MUL-02]","codigo":"LI-MUL-02","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-07-04"}]},{"id":33,"categoria":"ALTO","descripcion":"PELADORA DE PATAS 1 FROGOTEC [PA-PEL-01]","codigo":"PA-PEL-01","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-04-17"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-03"}]},{"id":34,"categoria":"ALTO","descripcion":"PELADORA DE PATAS 3 FRIGOTEC [PA-PEL-03]","codigo":"PA-PEL-03","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-04-02"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-02"}]},{"id":35,"categoria":"ALTO","descripcion":"PISTOLA ATURDIDORA 01 ACCLES Y SHELVOKE [LI-PIA-01]","codigo":"LI-PIA-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-06-01"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-06-01"}]},{"id":36,"categoria":"ALTO","descripcion":"PISTOLA ATURDIDORA CORRALES ACCLES Y SHELVOKE [CO-PIA-02]","codigo":"CO-PIA-02","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-26"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-03-26"}]},{"id":37,"categoria":"ALTO","descripcion":"PISTOLA DE NOQUEO 002 JARVIS USSS-1 [LI-PIS-04]","codigo":"LI-PIS-04","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-17"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-08-22"}]},{"id":38,"categoria":"ALTO","descripcion":"PLANTA ELECTRICA DE EMERGENCIA 1 DAEWOO 750KVA [SU-PDE-01]","codigo":"SU-PDE-01","intervenciones":[]},{"id":39,"categoria":"ALTO","descripcion":"PLATAFORMA EMERGENCIA 01 SIERRA CANAL [EM-PLA-01]","codigo":"EM-PLA-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-01-10"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2025-03-10"}]},{"id":40,"categoria":"ALTO","descripcion":"PLATAFORMA EMERGENCIA 02 SIERRA PECHO [EM-PLA-02]","codigo":"EM-PLA-02","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-20"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2026-03-20"}]},{"id":41,"categoria":"ALTO","descripcion":"PLATAFORMA NO.04 CUCHILLOS NEUMATICOS [LI-PLA-04]","codigo":"LI-PLA-04","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"}]},{"id":42,"categoria":"ALTO","descripcion":"PLATAFORMA NO.05 LA VUELTA [LI-PLA-05]","codigo":"LI-PLA-05","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"}]},{"id":43,"categoria":"ALTO","descripcion":"PLATAFORMA NO.06 ANUDADO O MARCACION DE CANALES [LI-PLA-06]","codigo":"LI-PLA-06","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"}]},{"id":44,"categoria":"ALTO","descripcion":"PLATAFORMA NO.08-01 DESOLLADORA [LI-PLA-08]","codigo":"LI-PLA-08","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"}]},{"id":45,"categoria":"ALTO","descripcion":"PLATAFORMA NO.08-02 DESOLLADORA [LI-PLA-08B]","codigo":"LI-PLA-08B","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"}]},{"id":46,"categoria":"ALTO","descripcion":"PLATAFORMA NO.09 SIERRA PECHO [LI-PLA-09]","codigo":"LI-PLA-09","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"}]},{"id":47,"categoria":"ALTO","descripcion":"PLATAFORMA NO.10 VISCERAS BLANCAS [LI-PLA-10]","codigo":"LI-PLA-10","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"}]},{"id":48,"categoria":"ALTO","descripcion":"PLATAFORMA NO.11 INSPECCION DE CALCULO [LI-PLA-11]","codigo":"LI-PLA-11","intervenciones":[]},{"id":49,"categoria":"ALTO","descripcion":"PLATAFORMA NO.12 VISCERAS ROJAS [LI-PLA-12]","codigo":"LI-PLA-12","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"}]},{"id":50,"categoria":"ALTO","descripcion":"PLATAFORMA NO.13 SIERRA CANAL [LI-PLA-13]","codigo":"LI-PLA-13","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2013-01-01"}]},{"id":51,"categoria":"ALTO","descripcion":"POLIPASTO LAVADO DE POLEAS KAIXUN [LI-PLP-02]","codigo":"LI-PLP-02","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-10-10"}]},{"id":52,"categoria":"ALTO","descripcion":"POLIPASTO PATAS BISONTE 500/1000KG [PA-PLP-04]","codigo":"PA-PLP-04","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-05-28"}]},{"id":53,"categoria":"ALTO","descripcion":"POLIPASTO RECIBO EMERGENCIA BISONTE [EM-PLP-02]","codigo":"EM-PLP-02","intervenciones":[]},{"id":54,"categoria":"ALTO","descripcion":"SECADORA DE AIRE COMPRIMIDO KAESER [LI-SAC-01]","codigo":"LI-SAC-01","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-15"}]},{"id":55,"categoria":"ALTO","descripcion":"SECADORA INDUSTRIAL BYC TECHNOLOGIES [LI-SEC-01]","codigo":"LI-SEC-01","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-04-01"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-04-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-29"}]},{"id":56,"categoria":"ALTO","descripcion":"SECADORA INDUSTRIAL DANUBE [LI-SEC-02]","codigo":"LI-SEC-02","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2025-01-01"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-01-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-01-01"}]},{"id":57,"categoria":"ALTO","descripcion":"SIERRA DE CANALES 001 JARVIS 121203 [LI-SIE-04]","codigo":"LI-SIE-04","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-20"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-05-20"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-03-11"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-05-20"}]},{"id":58,"categoria":"ALTO","descripcion":"SIERRA PECHO 001 JARVIS 102712 [LI-SIE-03]","codigo":"LI-SIE-03","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-12-12"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-12-12"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-12-12"}]},{"id":59,"categoria":"ALTO","descripcion":"SIERRA PECHO 4 KENTMASTER 11041 [EM-SIE-01]","codigo":"EM-SIE-01","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-12-01"}]},{"id":60,"categoria":"ALTO","descripcion":"TANQUE CANON CONTENIDO RUMINAL 1 [VB-TAN-01]","codigo":"VB-TAN-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2024-01-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-01-01"}]},{"id":61,"categoria":"ALTO","descripcion":"TANQUE CANON CONTENIDO RUMINAL 2 [VB-TAN-02]","codigo":"VB-TAN-02","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2024-01-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-01-01"}]},{"id":62,"categoria":"ALTO","descripcion":"TANQUE CANON PIELES [LI-TPI-01]","codigo":"LI-TPI-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-04-26"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-26"}]},{"id":63,"categoria":"ALTO","descripcion":"TRANSFERENCIA MECANICA 1 MOTOREDUCTOR SEW-EURODRIVE [LI-TRA-01]","codigo":"LI-TRA-01","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-22"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-02-24"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2013-01-01"}]},{"id":64,"categoria":"ALTO","descripcion":"TRANSFERENCIA MECANICA 2 MOTOREDUCTOR SEW-EURODRIVE [LI-TRA-02]","codigo":"LI-TRA-02","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-22"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-02-24"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2013-01-01"}]},{"id":65,"categoria":"ALTO","descripcion":"UNIDAD POTENCIA 1 HIDRAULICA DESOLLADO [LI-UPO-01]","codigo":"LI-UPO-01","intervenciones":[{"frecuencia":"CUATRIMESTRAL","dias_ciclo":120,"ultima_fecha":"2026-04-08"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-04-08"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-08"}]},{"id":66,"categoria":"ALTO","descripcion":"UNIDAD POTENCIA 2 HIDRAULICA TIJERAS CORTAPATAS [LI-UPO-02]","codigo":"LI-UPO-02","intervenciones":[{"frecuencia":"CUATRIMESTRAL","dias_ciclo":120,"ultima_fecha":"2025-12-22"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-12-10"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-12-23"}]},{"id":67,"categoria":"ALTO","descripcion":"UNIDAD POTENCIA 3 HIDRAULICA DESCORNADORA [LI-UPO-03]","codigo":"LI-UPO-03","intervenciones":[{"frecuencia":"CUATRIMESTRAL","dias_ciclo":120,"ultima_fecha":"2026-02-17"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-02-17"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-02-17"}]},{"id":68,"categoria":"ALTO","descripcion":"UNIDAD POTENCIA 5 HIDRAULICA MAQUINA CORTA CABEZAS [LI-UPO-05]","codigo":"LI-UPO-05","intervenciones":[{"frecuencia":"CUATRIMESTRAL","dias_ciclo":120,"ultima_fecha":"2025-11-23"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-11-26"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-11-23"}]},{"id":69,"categoria":"MEDIO","descripcion":"DESCORNADORA KENTMASTER 24243 [LI-DES-02]","codigo":"LI-DES-02","intervenciones":[]},{"id":70,"categoria":"MEDIO","descripcion":"ESMERIL DE AFILADO DEWALT 2 HP [LI-ESA-01]","codigo":"LI-ESA-01","intervenciones":[]},{"id":71,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 1 AIRMAX 1.5 HP [LI-EXT-01]","codigo":"LI-EXT-01","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-06-27"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-22"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2023-04-27"}]},{"id":72,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 10 DE PATAS AIRMAX [PA-EXT-10]","codigo":"PA-EXT-10","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-06-28"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-23"}]},{"id":73,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 11 DE CABEZAS AIRMAX [CA-EXT-11]","codigo":"CA-EXT-11","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-06-29"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-24"}]},{"id":74,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 12 VISERAS B. AIRMAX [VB-EXT-12]","codigo":"VB-EXT-12","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-06-30"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-25"}]},{"id":75,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 13 VISERAS R. AIRMAX [VR-EXT-13]","codigo":"VR-EXT-13","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-26"}]},{"id":76,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 14 PASILLO AIRMAX [VR-INY-14]","codigo":"VR-INY-14","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-02"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-27"}]},{"id":77,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 15 VISCERAS BL. AIRMAX [VB-EXT-15]","codigo":"VB-EXT-15","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-03"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-28"}]},{"id":78,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 2 AIRMAX 1.5 HP [LI-EXT-02]","codigo":"LI-EXT-02","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-04"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-01"}]},{"id":79,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 3 AIRMAX 1.5 HP [LI-EXT-03]","codigo":"LI-EXT-03","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-05"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-02"}]},{"id":80,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 4 AIRMAX 1.5 [LI-EXT-04]","codigo":"LI-EXT-04","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-06"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-03"}]},{"id":81,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 5 LATERAL AIRMAX 1.5 [LI-EXT-05]","codigo":"LI-EXT-05","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-07"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-04"}]},{"id":82,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 6 LATERAL AIRMAX 1.5 [LI-EXT-06]","codigo":"LI-EXT-06","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-08"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-05"}]},{"id":83,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 7 SALON MULTIPLE AIRMAX [LI-EXT-07]","codigo":"LI-EXT-07","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-09"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-06"}]},{"id":84,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 8 BANO HOMBRES AIRMAX [LI-EXT-08]","codigo":"LI-EXT-08","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-10"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-07"}]},{"id":85,"categoria":"MEDIO","descripcion":"EXTRACTOR DE AIRE 9 BANO MUJERES AIRMAX [LI-EXT-09]","codigo":"LI-EXT-09","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-07-11"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-08"}]},{"id":86,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 1 FIN DE LINEA VAXA 3 HP [LI-INY-01]","codigo":"LI-INY-01","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-03"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-09"}]},{"id":87,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 10 DE CABEZAS VAXA [CA-INY-10]","codigo":"CA-INY-10","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-04"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-10"}]},{"id":88,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 11 VISERAS B. VAXA [VB-INY-11]","codigo":"VB-INY-11","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-05"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-11"}]},{"id":89,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 12 VISERAS R. VAXA [VR-INY-12]","codigo":"VR-INY-12","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-06"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-12"}]},{"id":90,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 2 FIN DE LINEA VAXA [LI-INY-02]","codigo":"LI-INY-02","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-07"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-13"}]},{"id":91,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 3 FIN DE LINEA VAXA [LI-INY-03]","codigo":"LI-INY-03","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-08"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-14"}]},{"id":92,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 4 FIN DE LINEA VAXA [LI-INY-04]","codigo":"LI-INY-04","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-09"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-15"}]},{"id":93,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 5 LATERAL VAXA [LI-INY-05]","codigo":"LI-INY-05","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-10"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-16"}]},{"id":94,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 6 LATERAL VAXA [LI-INY-06]","codigo":"LI-INY-06","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-11"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-17"}]},{"id":95,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 7 VAXA [LI-INY-07]","codigo":"LI-INY-07","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-12"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-18"}]},{"id":96,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 8 VAXA [LI-INY-08]","codigo":"LI-INY-08","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-13"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-19"}]},{"id":97,"categoria":"MEDIO","descripcion":"INYECTOR DE AIRE 9 DE PATAS VAXA [PA-INY-09]","codigo":"PA-INY-09","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-02-14"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-03-20"}]},{"id":98,"categoria":"BAJO","descripcion":"BOMBA CENTRIGUGA CALDERA 01 WEG [ZDC-BOM-01]","codigo":"ZDC-BOM-01","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-22"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-06-09"}]},{"id":99,"categoria":"BAJO","descripcion":"BOMBA CENTRIGUGA CALDERA 02 WEG [ZDC-BOM-02]","codigo":"ZDC-BOM-02","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-22"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-05-18"}]},{"id":100,"categoria":"BAJO","descripcion":"BOMBA SANGRE NEUMATICA 001 HUSKY [LI-BOM-02]","codigo":"LI-BOM-02","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-03-12"}]},{"id":101,"categoria":"BAJO","descripcion":"CALDERA 2 TERMO VAPOR 100 BHP [LI-CAL-02]","codigo":"LI-CAL-02","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-04-25"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-25"}]},{"id":102,"categoria":"BAJO","descripcion":"CORTA PATAS KENMASTER 24469 [LI-COP-04]","codigo":"LI-COP-04","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-01-22"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-01-22"}]},{"id":103,"categoria":"BAJO","descripcion":"CUCHILLO NEUMATICO 11 KENMASTER [LI-CUN-11]","codigo":"LI-CUN-11","intervenciones":[{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-03-06"}]},{"id":104,"categoria":"BAJO","descripcion":"CUCHILLO NEUMATICO 7 JARVIS [LI-CUN-07]","codigo":"LI-CUN-07","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-04-13"},{"frecuencia":"BIMENSUAL","dias_ciclo":60,"ultima_fecha":"2026-03-07"}]},{"id":105,"categoria":"BAJO","descripcion":"IZADO DE BOVINOS SEW 9.2 KW [LI-IZA-O2]","codigo":"LI-IZA-O2","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-04-22"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-04-02"}]},{"id":106,"categoria":"BAJO","descripcion":"LAVABOTAS 1 5 PUESTOS [LI-LVB-01]","codigo":"LI-LVB-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2024-04-22"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-04-02"}]},{"id":107,"categoria":"BAJO","descripcion":"LAVABOTAS 2 5 PUESTOS [VS-LVB-02]","codigo":"VS-LVB-02","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2024-04-22"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-04-02"}]},{"id":108,"categoria":"BAJO","descripcion":"LAVADORA INDUSTRIAL DANUBE 25 KG [LI-LAV-02]","codigo":"LI-LAV-02","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-01-01"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-01-01"}]},{"id":109,"categoria":"BAJO","descripcion":"PISTOLA ATURDIDORA 02 ACCLES Y SHELVOKE [LI-PIA-02]","codigo":"LI-PIA-02","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-04-06"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-01-06"}]},{"id":110,"categoria":"BAJO","descripcion":"PISTOLA DE NOQUEO 001 JARVIS USSS-1 [LI-PIS-01]","codigo":"LI-PIS-01","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-04-22"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-08-22"}]},{"id":111,"categoria":"BAJO","descripcion":"PISTOLA DE NOQUEO 003 JARVIS USSS-21 [LI-PIS-03]","codigo":"LI-PIS-03","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-03-23"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2023-08-23"}]},{"id":112,"categoria":"BAJO","descripcion":"PLATAFORMA NO.01 SANGRIA 6 PUESTOS [LI-PLA-01]","codigo":"LI-PLA-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"}]},{"id":113,"categoria":"BAJO","descripcion":"PLATAFORMA NO.02 PRIMERA PATA [LI-PLA-02]","codigo":"LI-PLA-02","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-02"}]},{"id":114,"categoria":"BAJO","descripcion":"PLATAFORMA NO.03 SEGUNDA PATA [LI-PLA-03]","codigo":"LI-PLA-03","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-03"}]},{"id":115,"categoria":"BAJO","descripcion":"PLATAFORMA NO.07 DESPEJE FIJA DE CADERA [LI-PLA-07]","codigo":"LI-PLA-07","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-04"}]},{"id":116,"categoria":"BAJO","descripcion":"PLATAFORMA NO.14 EXTRACCION MEDULAR [LI-PLA-14]","codigo":"LI-PLA-14","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"}]},{"id":117,"categoria":"BAJO","descripcion":"PLATAFORMA NO.15 INSPECCION VETERINARIA [LI-PLA-15]","codigo":"LI-PLA-15","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-03-24"},{"frecuencia":"BIANUAL","dias_ciclo":730,"ultima_fecha":"2026-03-24"}]},{"id":118,"categoria":"BAJO","descripcion":"PLATAFORMA NO.16 CONTROL CERO SUPERIOR [LI-PLA-16]","codigo":"LI-PLA-16","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-02"}]},{"id":119,"categoria":"BAJO","descripcion":"PLATAFORMA NO.17 CONTROL CERO INFERIOR [LI-PLA-17]","codigo":"LI-PLA-17","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-02"}]},{"id":120,"categoria":"BAJO","descripcion":"PLATAFORMA NO.18 DOBLE LAVADO SUPERIOR [LI-PLA-18]","codigo":"LI-PLA-18","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-02-02"}]},{"id":121,"categoria":"BAJO","descripcion":"PLATAFORMA NO.19 APLICACION ACIDO LACTICO [LI-PLA-19]","codigo":"LI-PLA-19","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-03-02"}]},{"id":122,"categoria":"BAJO","descripcion":"PLATAFORMA NO.20 DECOMISO [LI-PLA-20]","codigo":"LI-PLA-20","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2013-01-01"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2013-01-01"}]},{"id":123,"categoria":"BAJO","descripcion":"POLIPASTO PATAS KAIXUN 999 LB [PA-PLP-03]","codigo":"PA-PLP-03","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-01-25"}]},{"id":124,"categoria":"BAJO","descripcion":"POLIPASTO RECIBO EMERGENCIA KAIXUN [EM-PLP-01]","codigo":"EM-PLP-01","intervenciones":[{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-01-25"}]},{"id":125,"categoria":"BAJO","descripcion":"SECADOR BOTAS N0.01 [LI-SCB-01]","codigo":"LI-SCB-01","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2024-01-06"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-01-26"}]},{"id":126,"categoria":"BAJO","descripcion":"SECADOR BOTAS N0.02 [LI-SCB-02]","codigo":"LI-SCB-02","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2024-01-07"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-01-27"}]},{"id":127,"categoria":"BAJO","descripcion":"SECADOR BOTAS N0.03 [LI-SCB-03]","codigo":"LI-SCB-03","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2024-01-08"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-01-28"}]},{"id":128,"categoria":"BAJO","descripcion":"SECADOR BOTAS N0.04 [LI-SCB-04]","codigo":"LI-SCB-04","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2024-01-09"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-01-29"}]},{"id":129,"categoria":"BAJO","descripcion":"SECADOR BOTAS N0.05 [LI-SCB-05]","codigo":"LI-SCB-05","intervenciones":[{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2024-01-10"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2024-01-30"}]},{"id":130,"categoria":"BAJO","descripcion":"SIERRA DE CANALES 002 JARVIS 121201 [LI-SIE-05]","codigo":"LI-SIE-05","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-20"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-05-20"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-03-11"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-05-20"}]},{"id":131,"categoria":"BAJO","descripcion":"SIERRA DE CANALES 003 JARVIS 121281 [EM-SIE-2]","codigo":"EM-SIE-2","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-20"},{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2026-05-20"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-03-11"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2026-05-20"}]},{"id":132,"categoria":"BAJO","descripcion":"SIERRA PECHO 002 JARVIS 103051 [LI-SIE-02]","codigo":"LI-SIE-02","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-08-04"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-08-04"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-08-04"}]},{"id":133,"categoria":"BAJO","descripcion":"SIERRA PECHO 003 JARVIS [LI-SIE-10]","codigo":"LI-SIE-10","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-08-02"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-08-02"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-08-02"}]},{"id":134,"categoria":"BAJO","descripcion":"SIERRA PECHO 3 JARVIS 102819 [LI-SIE-01]","codigo":"LI-SIE-01","intervenciones":[{"frecuencia":"TRIMESTRAL","dias_ciclo":90,"ultima_fecha":"2025-12-12"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-12-12"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-12-12"}]},{"id":135,"categoria":"BAJO","descripcion":"TANQUE PULMON KAESER 11 BAR [LI-TAN-01]","codigo":"LI-TAN-01","intervenciones":[{"frecuencia":"MENSUAL","dias_ciclo":30,"ultima_fecha":"2026-05-20"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2026-05-20"}]},{"id":136,"categoria":"BAJO","descripcion":"UNIDAD POTENCIA 4 HIDRAULICA CONTINGENCIA [LI-UPO-04]","codigo":"LI-UPO-04","intervenciones":[{"frecuencia":"CUATRIMESTRAL","dias_ciclo":120,"ultima_fecha":"2025-12-22"},{"frecuencia":"SEMESTRAL","dias_ciclo":180,"ultima_fecha":"2025-12-10"},{"frecuencia":"ANUAL","dias_ciclo":365,"ultima_fecha":"2025-12-23"}]}];

const TODAY = (function(){ const d=new Date(); d.setHours(0,0,0,0); return d; })();
const FREQ_DIAS = {MENSUAL:30,BIMENSUAL:60,TRIMESTRAL:90,CUATRIMESTRAL:120,SEMESTRAL:180,ANUAL:365,BIANUAL:730};

function ls(k){ try{ return JSON.parse(localStorage.getItem(k)); }catch(e){ return null; } }
function lsSet(k,v){ try{ localStorage.setItem(k,JSON.stringify(v)); }catch(e){} }

function getAreas(){
  let a=ls('mtto_areas');
  if(!a){
    a=[{id:'LB',nombre:'Línea de Beneficio',icono:'🏭',color:'#3b82f6'},
       {id:'DS',nombre:'Desposte',icono:'🔪',color:'#8b5cf6'},
       {id:'CO',nombre:'Corrales',icono:'🐄',color:'#10b981'},
       {id:'PTAR',nombre:'PTAR',icono:'💧',color:'#06b6d4'},
       {id:'PTAP',nombre:'PTAP',icono:'🚰',color:'#f59e0b'}];
    lsSet('mtto_areas',a);
  }
  return a;
}

function getEquipos(areaId){
  const deleted=ls('mtto_deleted_LB')||[];
  if(areaId==='LB'){
    const custom=ls('mtto_equipos_LB')||[];
    const overrides={};
    custom.forEach(e=>overrides[e.id]=e);
    const base=LB_DATA.filter(e=>!deleted.includes(e.id)).map(e=>overrides[e.id]||e);
    const extras=custom.filter(e=>!LB_DATA.find(b=>b.id===e.id));
    return [...base,...extras];
  }
  return (ls('mtto_equipos_'+areaId)||[]);
}

function saveEquipo(areaId,eq){
  let list=ls('mtto_equipos_'+areaId)||[];
  const idx=list.findIndex(e=>e.id===eq.id);
  if(idx>=0) list[idx]=eq; else list.push(eq);
  lsSet('mtto_equipos_'+areaId,list);
}

function deleteEquipo(areaId,eqId){
  if(areaId==='LB'){
    let d=ls('mtto_deleted_LB')||[];
    if(!d.includes(eqId)) d.push(eqId);
    lsSet('mtto_deleted_LB',d);
    let custom=ls('mtto_equipos_LB')||[];
    lsSet('mtto_equipos_LB',custom.filter(e=>e.id!==eqId));
  } else {
    let list=ls('mtto_equipos_'+areaId)||[];
    lsSet('mtto_equipos_'+areaId,list.filter(e=>e.id!==eqId));
  }
}

function getRegistros(){ return ls('mtto_registros')||[]; }
function getConfig(){ return ls('mtto_config')||{empresa:'Planta de Beneficio',year:'2026',pass:''}; }

let currentArea='LB', DATA=[], eqFilter='TODOS', alertFilter='VENCIDO';
let eqPage=1; const PER_PAGE=20;
let calYear=2026, calMonth=6;
let calFilters={VENCIDO:true,PROXIMO:true,OK:true};
let searchQ='', fotosPendientes=[];

(function init(){
  const cfg=getConfig();
  document.getElementById('sb-empresa').textContent=cfg.empresa;
  document.getElementById('cfg-empresa').value=cfg.empresa;
  document.getElementById('cfg-year').value=cfg.year||'2026';
  document.getElementById('sf-fecha').textContent=TODAY.toLocaleDateString('es-CO',{day:'2-digit',month:'short'});
  document.getElementById('sb-year').textContent=cfg.year||'2026';
  buildAreaSelectors();
  cambiarArea('LB');
  renderAreas();
  document.getElementById('reg-fecha').value='2026-06-06';
  renderTecLista().then(()=>populateTecnicoSelect());
  checkLogin();
})();

function buildAreaSelectors(){
  const areas=getAreas();
  ['area-select','reg-area'].forEach(id=>{
    const s=document.getElementById(id);
    s.innerHTML='';
    areas.forEach(a=>{ const o=document.createElement('option'); o.value=a.id; o.textContent=a.icono+' '+a.nombre; s.appendChild(o); });
  });
  const gs=document.getElementById('graf-area');
  gs.innerHTML='<option value="">Todas las áreas</option>';
  areas.forEach(a=>{ const o=document.createElement('option'); o.value=a.id; o.textContent=a.icono+' '+a.nombre; gs.appendChild(o); });
  document.getElementById('area-select').value=currentArea;
  document.getElementById('reg-area').value=currentArea;
}

function cambiarArea(areaId){
  currentArea=areaId;
  DATA=getEquipos(areaId);
  const area=getAreas().find(a=>a.id===areaId);
  if(area){
    document.getElementById('topbar-area-name').textContent=area.icono+' '+area.nombre;
    document.getElementById('topbar-area-dot').style.background=area.color;
  }
  document.getElementById('sf-total').textContent=DATA.length;
  document.getElementById('area-select').value=areaId;
  eqPage=1; searchQ='';
  document.getElementById('search-input').value='';
  renderAll();
}

function renderAll(){
  renderDashboard(); renderAlertas(); renderEquipos();
  renderCalendar(); renderReportes(); renderRegistros(); renderNotifs();
  populateRegEquipos();
}

function goPage(id,el){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('on'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('on'));
  document.getElementById('page-'+id).classList.add('on');
  const titles={dashboard:'Dashboard',alertas:'Alertas',equipos:'Equipos',calendario:'Calendario',registro:'Registrar Intervención',graficas:'Gráficas',reportes:'Reportes',areas:'Áreas',tecnicos:'Técnicos',config:'Configuración'};
  document.getElementById('page-title').textContent=titles[id]||id;
  if(el) el.classList.add('on');
  if(id==='graficas') renderGraficas();
  if(id==='areas') renderAreas();
  if(id==='reportes') renderReportes();
  if(id==='config'){ }
  if(id==='tecnicos'){ renderTecLista(); populateTecnicoSelect(); }
}

function doSearch(q){ searchQ=q.toLowerCase(); renderEquipos(); }

function fmtDate(d){
  if(!d) return '--';
  const dt=new Date(d+'T00:00:00');
  return dt.toLocaleDateString('es-CO',{day:'2-digit',month:'short',year:'numeric'});
}

function calcIntervenciones(plans){
  return (plans||[]).map(iv=>{
    if(!iv.ultima_fecha) return {...iv,dias_para_proxima:null,proxima_fecha:null,estado:'SIN'};
    const ultima=new Date(iv.ultima_fecha+'T00:00:00');
    const ciclo=FREQ_DIAS[iv.frecuencia]||iv.dias_ciclo||30;
    const proxima=new Date(ultima); proxima.setDate(proxima.getDate()+ciclo);
    const dias=Math.round((proxima-TODAY)/(864e5));
    const estado=dias<0?'VENCIDO':dias<=30?'PROXIMO':'OK';
    return {...iv,dias_ciclo:ciclo,proxima_fecha:proxima.toISOString().split('T')[0],dias_para_proxima:dias,estado};
  });
}

function countVencidos(d){ let n=0; (d||DATA).forEach(e=>calcIntervenciones(e.intervenciones).forEach(i=>{ if(i.estado==='VENCIDO')n++; })); return n; }

function toggleNotif(){
  document.getElementById('notif-panel').classList.toggle('on');
}
document.addEventListener('click',e=>{
  const p=document.getElementById('notif-panel'),b=document.getElementById('notif-btn');
  if(p.classList.contains('on')&&!p.contains(e.target)&&!b.contains(e.target)) p.classList.remove('on');
});

function renderNotifs(){
  let items=[];
  DATA.forEach(e=>calcIntervenciones(e.intervenciones).forEach(iv=>{
    if(iv.estado==='VENCIDO'||iv.estado==='PROXIMO') items.push({eq:e,iv});
  }));
  items.sort((a,b)=>a.iv.dias_para_proxima-b.iv.dias_para_proxima);
  document.getElementById('notif-dot').classList.toggle('on',items.length>0);
  document.getElementById('nb-alertas').textContent=items.filter(i=>i.iv.estado==='VENCIDO').length;
  const html=items.slice(0,15).map(({eq,iv})=>`
    <div class="notif-item ${iv.estado==='VENCIDO'?'ni-red':'ni-yellow'}" onclick="showModal_area('${currentArea}',${eq.id});toggleNotif();">
      <div class="notif-title">${eq.descripcion.substring(0,52)}${eq.descripcion.length>52?'...':''}</div>
      <div class="notif-sub">${iv.frecuencia} · ${iv.estado==='VENCIDO'?Math.abs(iv.dias_para_proxima)+'d VENCIDO':iv.dias_para_proxima+'d restantes'}</div>
    </div>`).join('');
  document.getElementById('notif-list').innerHTML=html||'<div style="padding:16px;text-align:center;color:var(--td);font-size:12px;">Sin alertas ✅</div>';
}

function renderDashboard(){
  let venc=0,prox=0,ok=0;
  const recalc=DATA.map(e=>({...e,intervenciones:calcIntervenciones(e.intervenciones)}));
  recalc.forEach(e=>e.intervenciones.forEach(i=>{
    if(i.estado==='VENCIDO')venc++;else if(i.estado==='PROXIMO')prox++;else if(i.estado==='OK')ok++;
  }));
  document.getElementById('st-vencidos').textContent=venc;
  document.getElementById('st-proximos').textContent=prox;
  document.getElementById('st-ok').textContent=ok;
  document.getElementById('st-total').textContent=DATA.length;
  const alto=DATA.filter(e=>e.categoria==='ALTO').length, medio=DATA.filter(e=>e.categoria==='MEDIO').length, bajo=DATA.filter(e=>e.categoria==='BAJO').length;
  document.getElementById('st-vencidos-sub').textContent=`Alto:${alto} Medio:${medio} Bajo:${bajo}`;
  document.getElementById('st-total-sub').textContent=`Alto:${alto} | Medio:${medio} | Bajo:${bajo}`;
  const cats=['ALTO','MEDIO','BAJO'], catColors={ALTO:'var(--red)',MEDIO:'var(--yellow)',BAJO:'var(--green)'};
  document.getElementById('chart-cat').innerHTML=cats.map(c=>{
    const eqs=recalc.filter(e=>e.categoria===c);
    const v=eqs.reduce((a,e)=>a+e.intervenciones.filter(i=>i.estado==='VENCIDO').length,0);
    const tot=eqs.reduce((a,e)=>a+e.intervenciones.length,0);
    const pct=tot>0?Math.round(v/tot*100):0;
    return `<div class="bar-row"><div class="bar-label">${c}</div><div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${catColors[c]};"><span>${v}v</span></div></div><span style="font-size:11px;color:var(--td);width:28px;">${tot}</span></div>`;
  }).join('');
  const freqs=['MENSUAL','BIMENSUAL','TRIMESTRAL','CUATRIMESTRAL','SEMESTRAL','ANUAL'];
  const fColors=['#ef4444','#f59e0b','#8b5cf6','#3b82f6','#10b981','#06b6d4'];
  const fCnts=freqs.map(f=>recalc.reduce((a,e)=>a+e.intervenciones.filter(i=>i.frecuencia===f).length,0));
  const maxF=Math.max(...fCnts,1);
  document.getElementById('chart-freq').innerHTML=freqs.map((f,i)=>`<div class="bar-row"><div class="bar-label" style="font-size:10px;">${f}</div><div class="bar-track"><div class="bar-fill" style="width:${Math.round(fCnts[i]/maxF*100)}%;background:${fColors[i]};"><span>${fCnts[i]}</span></div></div></div>`).join('');
  let urg=[];
  recalc.forEach(e=>e.intervenciones.forEach(i=>{ if(i.estado==='VENCIDO') urg.push({eq:e,iv:i}); }));
  urg.sort((a,b)=>a.iv.dias_para_proxima-b.iv.dias_para_proxima);
  document.getElementById('dash-urgent').innerHTML=urg.slice(0,8).map(({eq,iv})=>`
    <div class="alert-card" onclick="showModal_area('${currentArea}',${eq.id})">
      <div class="alert-header"><span class="cat-badge cat-${eq.categoria.toLowerCase()}">${eq.categoria}</span>
      <div class="alert-title">${eq.descripcion.substring(0,68)}${eq.descripcion.length>68?'...':''}</div>
      <span class="dias-num dias-red">${Math.abs(iv.dias_para_proxima)}d vencido</span></div>
      <div class="alert-meta"><span>⏱ ${iv.frecuencia}</span><span>📅 ${fmtDate(iv.ultima_fecha)}</span><span>⚠ ${fmtDate(iv.proxima_fecha)}</span></div>
    </div>`).join('')||'<div class="empty"><div class="empty-icon">🎉</div>Sin vencidos críticos</div>';
}

function filtAlerta(f,el){ alertFilter=f; document.querySelectorAll('#page-alertas .filt').forEach(b=>b.classList.remove('on')); if(el)el.classList.add('on'); renderAlertas(); }
function renderAlertas(){
  const cat=document.getElementById('alerta-cat').value;
  let items=[];
  DATA.forEach(e=>{
    if(cat&&e.categoria!==cat) return;
    calcIntervenciones(e.intervenciones).forEach(i=>{
      if(alertFilter==='TODOS'||i.estado===alertFilter) items.push({eq:e,iv:i});
    });
  });
  // No searchQ filter in alertas
  items.sort((a,b)=>a.iv.dias_para_proxima-b.iv.dias_para_proxima);
  const colors={VENCIDO:'',PROXIMO:'yellow',OK:'green'};
  document.getElementById('alert-list').innerHTML=items.map(({eq,iv})=>`
    <div class="alert-card ${colors[iv.estado]||''}" onclick="showModal_area('${currentArea}',${eq.id})">
      <div class="alert-header"><span class="cat-badge cat-${eq.categoria.toLowerCase()}">${eq.categoria}</span>
      <div class="alert-title">${eq.descripcion.substring(0,62)}${eq.descripcion.length>62?'...':''}</div>
      <span class="status-badge st-${iv.estado.toLowerCase()}">${iv.estado}</span></div>
      <div class="alert-meta"><span>⏱ ${iv.frecuencia}</span><span>📅 ${fmtDate(iv.ultima_fecha)}</span><span>→ ${fmtDate(iv.proxima_fecha)}</span>
      <span class="dias-num ${iv.dias_para_proxima<0?'dias-red':iv.dias_para_proxima<=30?'dias-yellow':'dias-green'}">${iv.dias_para_proxima<0?Math.abs(iv.dias_para_proxima)+'d VENCIDO':iv.dias_para_proxima+'d'}</span></div>
    </div>`).join('')||'<div class="empty"><div class="empty-icon">✅</div>Sin alertas</div>';
}

function filtEq(f,el){ eqFilter=f; eqPage=1; document.querySelectorAll('#page-equipos .filt[onclick*="filtEq"]').forEach(b=>b.classList.remove('on')); if(el)el.classList.add('on'); renderEquipos(); }
function renderEquipos(){
  const freqF=document.getElementById('eq-freq').value, estadoF=document.getElementById('eq-estado').value;
  let rows=[];
  DATA.forEach(e=>{
    if(eqFilter!=='TODOS'&&e.categoria!==eqFilter) return;
    if(searchQ&&!e.descripcion.toLowerCase().includes(searchQ)&&!(e.codigo||'').toLowerCase().includes(searchQ)) return;
    const intervs=calcIntervenciones(e.intervenciones);
    if(!intervs.length){ if(!estadoF) rows.push({eq:e,iv:null}); return; }
    intervs.forEach(iv=>{ if(freqF&&iv.frecuencia!==freqF) return; if(estadoF&&iv.estado!==estadoF) return; rows.push({eq:e,iv}); });
  });
  const total=rows.length, pages=Math.ceil(total/PER_PAGE)||1;
  const slice=rows.slice((eqPage-1)*PER_PAGE,eqPage*PER_PAGE);
  document.getElementById('eq-tbody').innerHTML=slice.map(({eq,iv})=>{
    const st=iv?iv.estado:'SIN';
    const stC={VENCIDO:'st-vencido',PROXIMO:'st-proximo',OK:'st-ok',SIN:'st-sin'}[st];
    const stL={VENCIDO:'🔴 Vencido',PROXIMO:'⚠ Próximo',OK:'✅ OK',SIN:'Sin datos'}[st];
    const dias=iv?(iv.dias_para_proxima<0?`<span class="dias-num dias-red">${Math.abs(iv.dias_para_proxima)}d</span>`:`<span class="dias-num ${iv.dias_para_proxima<=30?'dias-yellow':'dias-green'}">${iv.dias_para_proxima}d</span>`):'--';
    return `<tr><td><div class="eq-name">${eq.descripcion.substring(0,48)}${eq.descripcion.length>48?'...':''}<small>${eq.codigo||''}</small></div></td>
      <td><span class="cat-badge cat-${eq.categoria.toLowerCase()}">${eq.categoria}</span></td>
      <td>${iv?`<span class="freq-tag">${iv.frecuencia}</span>`:'--'}</td>
      <td style="font-size:11px;">${iv?fmtDate(iv.ultima_fecha):'--'}</td>
      <td style="font-size:11px;">${iv?fmtDate(iv.proxima_fecha):'--'}</td>
      <td>${dias}</td><td><span class="status-badge ${stC}">${stL}</span></td>
      <td style="white-space:nowrap;"><button class="btn-det" onclick="showModal_area('${currentArea}',${eq.id})">Ver</button> <button class="btn-icon" onclick="openEqModal(${eq.id})" title="Editar">✏️</button></td>
    </tr>`;
  }).join('')||'<tr><td colspan="8" class="empty">Sin resultados</td></tr>';
  document.getElementById('eq-info').textContent=`${total} registros (pág ${eqPage}/${pages})`;
  let pg='';
  if(eqPage>1) pg+=`<button class="pg-btn" onclick="eqPage=${eqPage-1};renderEquipos()">←</button>`;
  for(let p=Math.max(1,eqPage-2);p<=Math.min(pages,eqPage+2);p++) pg+=`<button class="pg-btn ${p===eqPage?'on':''}" onclick="eqPage=${p};renderEquipos()">${p}</button>`;
  if(eqPage<pages) pg+=`<button class="pg-btn" onclick="eqPage=${eqPage+1};renderEquipos()">→</button>`;
  document.getElementById('eq-pages').innerHTML=pg;
}

function calFilt(f){ calFilters[f]=!calFilters[f]; document.getElementById('cal-f-'+f.toLowerCase()).classList.toggle('on',calFilters[f]); renderCalendar(); }
function calPrev(){ calMonth--; if(calMonth<1){calMonth=12;calYear--;} renderCalendar(); }
function calNext(){ calMonth++; if(calMonth>12){calMonth=1;calYear++;} renderCalendar(); }
function renderCalendar(){
  const months=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
  document.getElementById('cal-title').textContent=`${months[calMonth-1]} ${calYear}`;
  const events={};
  DATA.forEach(e=>calcIntervenciones(e.intervenciones).forEach(iv=>{
    if(!calFilters[iv.estado]||!iv.proxima_fecha) return;
    const d=new Date(iv.proxima_fecha+'T00:00:00');
    if(d.getFullYear()===calYear&&d.getMonth()===calMonth-1){
      const k=d.getDate(); if(!events[k]) events[k]={VENCIDO:[],PROXIMO:[],OK:[]};
      events[k][iv.estado].push({eq:e,iv});
    }
  }));
  document.getElementById('cal-header').innerHTML=['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'].map(d=>`<div class="cal-day-name">${d}</div>`).join('');
  const firstDay=new Date(calYear,calMonth-1,1).getDay(), dIM=new Date(calYear,calMonth,0).getDate(), dPrev=new Date(calYear,calMonth-1,0).getDate();
  let cells=[];
  for(let i=firstDay-1;i>=0;i--) cells.push({day:dPrev-i,other:true});
  for(let i=1;i<=dIM;i++) cells.push({day:i,other:false});
  while(cells.length%7!==0) cells.push({day:cells.length-dIM-firstDay+1,other:true});
  document.getElementById('cal-grid').innerHTML=cells.map(c=>{
    const ev=!c.other&&events[c.day]; let evH='';
    if(ev){ if(ev.VENCIDO.length) evH+=`<div class="cal-event ce-red">🔴 ${ev.VENCIDO.length}</div>`; if(ev.PROXIMO.length) evH+=`<div class="cal-event ce-yellow">⚠ ${ev.PROXIMO.length}</div>`; if(ev.OK.length) evH+=`<div class="cal-event ce-green">✅ ${ev.OK.length}</div>`; }
    const isToday=c.day===6&&calMonth===6&&calYear===2026&&!c.other;
    return `<div class="cal-day ${c.other?'other-month':''} ${isToday?'today':''}" onclick="${!c.other?`showCalDay(${c.day},${calMonth},${calYear})`:''}"><div class="cal-day-num">${c.day}</div>${evH}</div>`;
  }).join('');
  document.getElementById('cal-day-detail').innerHTML='';
}
function showCalDay(day,month,year){
  const items=[]; DATA.forEach(e=>calcIntervenciones(e.intervenciones).forEach(iv=>{
    if(!iv.proxima_fecha) return; const d=new Date(iv.proxima_fecha+'T00:00:00');
    if(d.getDate()===day&&d.getMonth()===month-1&&d.getFullYear()===year&&calFilters[iv.estado]) items.push({eq:e,iv});
  }));
  if(!items.length) return;
  const ms=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
  document.getElementById('cal-day-detail').innerHTML=`<div class="section-title">📅 ${day} ${ms[month-1]} ${year} — ${items.length} intervención${items.length>1?'es':''}</div>
  <div class="alert-list">${items.map(({eq,iv})=>`<div class="alert-card ${iv.estado==='PROXIMO'?'yellow':iv.estado==='OK'?'green':''}" onclick="showModal_area('${currentArea}',${eq.id})">
    <div class="alert-header"><span class="cat-badge cat-${eq.categoria.toLowerCase()}">${eq.categoria}</span><div class="alert-title">${eq.descripcion.substring(0,58)}</div><span class="status-badge st-${iv.estado.toLowerCase()}">${iv.estado}</span></div>
    <div class="alert-meta"><span>⏱ ${iv.frecuencia}</span><span>📅 ${fmtDate(iv.ultima_fecha)}</span></div></div>`).join('')}</div>`;
}

function showModal_area(areaId,eqId){
  const eq=getEquipos(areaId).find(e=>e.id===eqId); if(!eq) return;
  const eqR={...eq,intervenciones:calcIntervenciones(eq.intervenciones)};
  document.getElementById('modal-title').textContent=eqR.descripcion;
  document.getElementById('modal-code').textContent=eqR.codigo||'Sin código';
  const catC={ALTO:'cat-alto',MEDIO:'cat-medio',BAJO:'cat-bajo'}[eqR.categoria];
  let html=`<div style="display:flex;gap:8px;margin-bottom:16px;"><span class="cat-badge ${catC}">${eqR.categoria} IMPACTO</span>${eqR.codigo?`<span class="tag">${eqR.codigo}</span>`:''}</div>`;
  if(!eqR.intervenciones.length){ html+='<div class="empty"><div class="empty-icon">📅</div>Sin intervenciones registradas</div>'; }
  else {
    html+='<div style="font-size:12px;font-weight:600;color:var(--td);margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px;">Plan de Mantenimiento</div>';
    eqR.intervenciones.forEach(iv=>{
      const stC={VENCIDO:'st-vencido',PROXIMO:'st-proximo',OK:'st-ok',SIN:'st-sin'}[iv.estado];
      const dC=iv.dias_para_proxima<0?'dias-red':iv.dias_para_proxima<=30?'dias-yellow':'dias-green';
      html+=`<div class="interv-row"><div class="interv-freq">${iv.frecuencia}</div><div class="interv-info"><div class="interv-fecha">Última: <b>${fmtDate(iv.ultima_fecha)}</b></div><div class="interv-prox">Próxima: ${fmtDate(iv.proxima_fecha)} · Ciclo: ${iv.dias_ciclo}d</div>${iv.tarea?`<div style="font-size:11px;color:var(--blue);margin-top:3px;">📋 ${iv.tarea}</div>`:''}</div><span class="status-badge ${stC}" style="margin-right:8px;">${iv.estado}</span><div class="interv-days ${dC}">${iv.dias_para_proxima<0?'-'+Math.abs(iv.dias_para_proxima):'+'+iv.dias_para_proxima}d</div></div>`;
    });
  }
  const regs=getRegistros().filter(r=>r.equipo_id==eqId&&r.area_id===areaId);
  if(regs.length){
    html+=`<div style="font-size:12px;font-weight:600;color:var(--td);margin:16px 0 8px;text-transform:uppercase;letter-spacing:.5px;">Historial (${regs.length})</div>`;
    html+=regs.slice(-3).reverse().map(r=>`<div style="background:var(--s3);border-radius:6px;padding:10px 12px;margin-bottom:6px;font-size:12px;">
      <b style="color:var(--tb);">${fmtDate(r.fecha)}</b> · <span class="freq-tag">${r.frecuencia}</span> · ${r.tecnico||'Sin técnico'}
      ${r.obs?`<div style="color:var(--td);margin-top:4px;">${r.obs}</div>`:''}
      ${r.fotos&&r.fotos.length?`<div style="margin-top:6px;display:flex;gap:4px;flex-wrap:wrap;">${r.fotos.map(f=>`<img src="${f}" style="width:44px;height:44px;object-fit:cover;border-radius:4px;cursor:pointer;border:1px solid var(--bd);" onclick="openFotoModal('${f}')">`).join('')}</div>`:''}
    </div>`).join('');
  }
  html+=`<div style="margin-top:16px;display:flex;gap:8px;">
    <button class="btn-primary" onclick="irRegistrar('${areaId}',${eqId})">📝 Registrar</button>
    <button class="btn-secondary" onclick="openEqModal(${eqId})">✏️ Editar</button>
  </div>`;
  document.getElementById('modal-body').innerHTML=html;
  document.getElementById('modal-overlay').classList.add('on');
}
function closeModal(e){ if(!e||e.target===document.getElementById('modal-overlay')) document.getElementById('modal-overlay').classList.remove('on'); }
function openFotoModal(src){ document.getElementById('foto-modal-img').src=src; document.getElementById('foto-modal-overlay').classList.add('on'); }
function closeFotoModal(e){ if(!e||e.target===document.getElementById('foto-modal-overlay')) document.getElementById('foto-modal-overlay').classList.remove('on'); }
function irRegistrar(areaId,eqId){ closeModal(); document.getElementById('reg-area').value=areaId; populateRegEquipos(); setTimeout(()=>document.getElementById('reg-equipo').value=eqId,80); document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('on')); goPage('registro',document.querySelectorAll('.nav-item')[4]); }

function cargarEquiposReg(){
  const aId = document.getElementById('reg-area').value || currentArea;
  _equiposReg = getEquipos(aId);
  // Mostrar todos al hacer foco si el campo está vacío
  const q = document.getElementById('reg-equipo-search').value;
  if(!q) filtrarEquipos('');
}

function populateRegEquipos(){
  populateTecnicoSelect();
  const aId=document.getElementById('reg-area').value||currentArea;
  const s=document.getElementById('reg-equipo'); s.innerHTML='<option value="">-- Seleccionar equipo --</option>';
  getEquipos(aId).forEach(e=>{ const o=document.createElement('option'); o.value=e.id; o.textContent=e.codigo?`[${e.codigo}] ${e.descripcion.substring(0,44)}`:e.descripcion.substring(0,52); s.appendChild(o); });
}
function handleFotos(input){
  const files=Array.from(input.files);
  if(fotosPendientes.length+files.length>3){ alert('Máximo 3 fotos'); return; }
  files.forEach(file=>{ const r=new FileReader(); r.onload=e=>{ fotosPendientes.push(e.target.result); renderFotoPreview(); }; r.readAsDataURL(file); });
  input.value='';
}
function renderFotoPreview(){ document.getElementById('foto-preview').innerHTML=fotosPendientes.map((f,i)=>`<div class="foto-thumb"><img src="${f}" onclick="openFotoModal('${f}')"><button class="foto-del" onclick="removeFoto(${i})">✕</button></div>`).join(''); }
function removeFoto(i){ fotosPendientes.splice(i,1); renderFotoPreview(); }
function guardarRegistro(){
  const aId=document.getElementById('reg-area').value||currentArea;
  const eqId=document.getElementById('reg-equipo').value, freq=document.getElementById('reg-freq').value, fecha=document.getElementById('reg-fecha').value;
  if(!eqId||!freq||!fecha){ alert('Completa los campos requeridos (*)'); return; }
  const eq=getEquipos(aId).find(e=>e.id==eqId);
  const regs=getRegistros();
  regs.push({id:Date.now(),equipo_id:parseInt(eqId),area_id:aId,equipo_nombre:eq?eq.descripcion.substring(0,60):'',frecuencia:freq,fecha,tecnico:document.getElementById('reg-tecnico').value,obs:document.getElementById('reg-obs').value,fotos:[...fotosPendientes],registrado:new Date().toISOString()});
  lsSet('mtto_registros',regs);
  if(eq){
    const intervs=(eq.intervenciones||[]).map(iv=>iv.frecuencia===freq?{...iv,ultima_fecha:fecha}:iv);
    if(!intervs.find(iv=>iv.frecuencia===freq)) intervs.push({frecuencia:freq,dias_ciclo:FREQ_DIAS[freq],ultima_fecha:fecha});
    saveEquipo(aId,{...eq,intervenciones:intervs});
    cambiarArea(currentArea);
  }
  fotosPendientes=[]; renderFotoPreview(); limpiarForm(); renderRegistros();
  alert('✅ Registro guardado');
}
function limpiarForm(){ ['reg-equipo','reg-freq','reg-obs'].forEach(id=>document.getElementById(id).value=''); document.getElementById('reg-tecnico').value=''; document.getElementById('reg-fecha').value='2026-06-06'; fotosPendientes=[]; renderFotoPreview(); }
function renderRegistros(){
  document.getElementById('reg-tbody').innerHTML=getRegistros().slice().reverse().map(r=>`<tr>
    <td style="font-size:11px;padding:8px 14px;border-top:1px solid var(--bd);">${fmtDate(r.fecha)}</td>
    <td style="font-size:11px;padding:8px 14px;border-top:1px solid var(--bd);">${r.equipo_nombre||'--'}</td>
    <td style="padding:8px 14px;border-top:1px solid var(--bd);"><span class="freq-tag">${r.frecuencia}</span></td>
    <td style="font-size:11px;padding:8px 14px;border-top:1px solid var(--bd);">${r.tecnico||'--'}</td>
    <td style="font-size:11px;padding:8px 14px;border-top:1px solid var(--bd);color:var(--td);">${r.obs||'--'}</td>
    <td style="padding:8px 14px;border-top:1px solid var(--bd);">${r.fotos&&r.fotos.length?r.fotos.map(f=>`<img src="${f}" style="width:30px;height:30px;object-fit:cover;border-radius:3px;cursor:pointer;border:1px solid var(--bd);margin-right:2px;" onclick="openFotoModal('${f}')">`).join(''):'--'}</td>
    <td style="padding:8px 14px;border-top:1px solid var(--bd);"><button class="btn-icon" onclick="editarRegistro(${r.id})" title="Editar">✏️</button></td>
  </tr>`).join('')||'<tr><td colspan="6" class="empty" style="padding:20px;">Sin registros</td></tr>';
}

function openEqModal(eqId){
  const areas=getAreas();
  document.getElementById('eq-area-sel').innerHTML=areas.map(a=>`<option value="${a.id}">${a.icono} ${a.nombre}</option>`).join('');
  document.getElementById('eq-area-sel').value=currentArea;
  document.getElementById('eq-freq-list').innerHTML='';
  document.getElementById('eq-edit-id').value='';
  document.getElementById('eq-delete-btn').style.display='none';
  document.getElementById('eq-modal-title').textContent='Nuevo Equipo';
  if(eqId){
    const eq=DATA.find(e=>e.id===eqId); if(!eq){alert('No encontrado');return;}
    document.getElementById('eq-modal-title').textContent='Editar Equipo';
    document.getElementById('eq-desc').value=eq.descripcion;
    document.getElementById('eq-codigo').value=eq.codigo||'';
    document.getElementById('eq-cat').value=eq.categoria;
    document.getElementById('eq-edit-id').value=eqId;
    document.getElementById('eq-delete-btn').style.display='';
    (eq.intervenciones||[]).forEach(iv=>addFreqRow(iv.frecuencia,iv.ultima_fecha,iv.tarea||''));
  } else { document.getElementById('eq-desc').value=''; document.getElementById('eq-codigo').value=''; document.getElementById('eq-cat').value='ALTO'; addFreqRow(); }
  document.getElementById('eq-modal-overlay').classList.add('on');
}
function addFreqRow(freq='',fecha='',tarea=''){
  const wrap=document.getElementById('eq-freq-list'), div=document.createElement('div');
  div.className='freq-item';
  div.innerHTML=`<div class="form-group"><label>Frecuencia</label><select class="form-control freq-sel">${['MENSUAL','BIMENSUAL','TRIMESTRAL','CUATRIMESTRAL','SEMESTRAL','ANUAL','BIANUAL'].map(f=>`<option value="${f}" ${f===freq?'selected':''}>${f}</option>`).join('')}</select></div>
  <div class="form-group"><label>Última intervención</label><input type="date" class="form-control freq-fecha" value="${fecha||''}"></div>
  <button type="button" style="background:transparent;border:none;color:var(--red);cursor:pointer;font-size:18px;padding:0 4px;margin-bottom:2px;" onclick="this.parentElement.remove()">✕</button>
  <div class="form-group freq-tarea-wrap"><label>Tarea a realizar</label><input type="text" class="form-control freq-tarea" placeholder="Ej: Lubricación de rodamientos, cambio de filtros..." value="${tarea||''}"></div>`;
  wrap.appendChild(div);
}
function guardarEquipo(){
  const desc=document.getElementById('eq-desc').value.trim(), codigo=document.getElementById('eq-codigo').value.trim();
  const cat=document.getElementById('eq-cat').value, aId=document.getElementById('eq-area-sel').value;
  const editId=document.getElementById('eq-edit-id').value;
  if(!desc){ alert('La descripción es requerida'); return; }
  const intervenciones=[...document.querySelectorAll('#eq-freq-list .freq-item')].map(row=>({ frecuencia:row.querySelector('.freq-sel').value, dias_ciclo:FREQ_DIAS[row.querySelector('.freq-sel').value]||30, ultima_fecha:row.querySelector('.freq-fecha').value||null, tarea:row.querySelector('.freq-tarea').value||'' })).filter(iv=>iv.frecuencia);
  const eq={id:editId?parseInt(editId):Date.now(),categoria:cat,descripcion:desc,codigo,intervenciones};
  saveEquipo(aId,eq); cambiarArea(currentArea); closeEqModal(); alert('✅ Equipo guardado');
}
function eliminarEquipo(){ const editId=document.getElementById('eq-edit-id').value; if(!editId) return; if(!confirm('¿Eliminar este equipo?')) return; deleteEquipo(currentArea,parseInt(editId)); cambiarArea(currentArea); closeEqModal(); }
function closeEqModal(e){ if(!e||e.target===document.getElementById('eq-modal-overlay')) document.getElementById('eq-modal-overlay').classList.remove('on'); }

function renderAreas(){
  const areas=getAreas();
  document.getElementById('areas-grid').innerHTML=areas.map(a=>{
    const eqs=getEquipos(a.id), v=countVencidos(eqs);
    return `<div class="area-card ${a.id===currentArea?'active-area':''}" style="border-top:3px solid ${a.color};" onclick="cambiarArea('${a.id}');goPage('dashboard',document.querySelector('.nav-item'))">
      <div class="area-card-actions"><button class="btn-icon" onclick="event.stopPropagation();openAreaModal('${a.id}')" title="Editar">✏️</button></div>
      <div class="area-card-icon">${a.icono}</div><div class="area-card-name">${a.nombre}</div>
      <div class="area-card-count">${eqs.length} equipos${v>0?` · <span style="color:var(--red);">${v} vencidos</span>`:''}</div>
    </div>`;
  }).join('');
}
function openAreaModal(aId){
  document.getElementById('area-nombre').value=''; document.getElementById('area-icono').value='🏭'; document.getElementById('area-color').value='#3b82f6';
  document.getElementById('area-edit-id').value=''; document.getElementById('area-delete-btn').style.display='none'; document.getElementById('area-modal-title').textContent='Nueva Área';
  if(aId){ const a=getAreas().find(x=>x.id===aId); if(!a) return; document.getElementById('area-nombre').value=a.nombre; document.getElementById('area-icono').value=a.icono; document.getElementById('area-color').value=a.color; document.getElementById('area-edit-id').value=aId; document.getElementById('area-delete-btn').style.display=''; document.getElementById('area-modal-title').textContent='Editar Área'; }
  document.getElementById('area-modal-overlay').classList.add('on');
}
function guardarArea(){
  const nombre=document.getElementById('area-nombre').value.trim(), icono=document.getElementById('area-icono').value.trim()||'🏭', color=document.getElementById('area-color').value, editId=document.getElementById('area-edit-id').value;
  if(!nombre){ alert('Nombre requerido'); return; }
  let areas=getAreas();
  if(editId) areas=areas.map(a=>a.id===editId?{...a,nombre,icono,color}:a);
  else areas.push({id:'AREA_'+Date.now(),nombre,icono,color});
  lsSet('mtto_areas',areas); buildAreaSelectors(); renderAreas(); closeAreaModal();
}
function eliminarArea(){ const editId=document.getElementById('area-edit-id').value; if(!editId||editId==='LB'){alert('No se puede eliminar el área base.');return;} if(!confirm('¿Eliminar esta área y todos sus equipos?')) return; let areas=getAreas().filter(a=>a.id!==editId); lsSet('mtto_areas',areas); localStorage.removeItem('mtto_equipos_'+editId); buildAreaSelectors(); if(currentArea===editId) cambiarArea('LB'); renderAreas(); closeAreaModal(); }
function closeAreaModal(e){ if(!e||e.target===document.getElementById('area-modal-overlay')) document.getElementById('area-modal-overlay').classList.remove('on'); }

function renderGraficas(){
  const filtArea=document.getElementById('graf-area').value, areas=getAreas();
  const aStats=areas.map(a=>{ const eqs=getEquipos(a.id); let v=0,p=0,ok=0; eqs.forEach(e=>calcIntervenciones(e.intervenciones).forEach(i=>{ if(i.estado==='VENCIDO')v++;else if(i.estado==='PROXIMO')p++;else if(i.estado==='OK')ok++; })); return {a,v,p,ok,tot:v+p+ok}; });
  document.getElementById('chart-areas').innerHTML=aStats.map(s=>{
    const pV=s.tot>0?Math.round(s.v/s.tot*100):0, pP=s.tot>0?Math.round(s.p/s.tot*100):0, pOk=s.tot>0?Math.round(s.ok/s.tot*100):0;
    return `<div class="bar-row" style="margin-bottom:8px;"><div class="bar-label" style="width:120px;font-size:10px;">${s.a.icono} ${s.a.nombre.substring(0,14)}</div>
      <div style="flex:1;"><div style="display:flex;height:20px;border-radius:4px;overflow:hidden;background:var(--s3);">
        ${s.v>0?`<div style="width:${pV}%;background:var(--red);display:flex;align-items:center;justify-content:center;"><span style="font-size:9px;color:#fff;font-weight:700;">${s.v}</span></div>`:''}
        ${s.p>0?`<div style="width:${pP}%;background:var(--yellow);display:flex;align-items:center;justify-content:center;"><span style="font-size:9px;color:#000;font-weight:700;">${s.p}</span></div>`:''}
        ${s.ok>0?`<div style="width:${pOk}%;background:var(--green);display:flex;align-items:center;justify-content:center;"><span style="font-size:9px;color:#fff;font-weight:700;">${s.ok}</span></div>`:''}
      </div></div></div>`;
  }).join('')+`<div style="display:flex;gap:12px;margin-top:8px;font-size:11px;color:var(--td);">
    <span><span style="display:inline-block;width:10px;height:10px;background:var(--red);border-radius:2px;margin-right:4px;"></span>Vencido</span>
    <span><span style="display:inline-block;width:10px;height:10px;background:var(--yellow);border-radius:2px;margin-right:4px;"></span>Próximo</span>
    <span><span style="display:inline-block;width:10px;height:10px;background:var(--green);border-radius:2px;margin-right:4px;"></span>OK</span></div>`;
  const td=filtArea?getEquipos(filtArea):DATA;
  document.getElementById('chart-cumpl').innerHTML=['ALTO','MEDIO','BAJO'].map(c=>{
    const eqs=td.filter(e=>e.categoria===c); let tot=0,ok=0;
    eqs.forEach(e=>calcIntervenciones(e.intervenciones).forEach(i=>{ tot++; if(i.estado==='OK')ok++; }));
    const pct=tot>0?Math.round(ok/tot*100):0;
    const col={ALTO:'var(--red)',MEDIO:'var(--yellow)',BAJO:'var(--green)'}[c];
    return `<div class="cumpl-row"><div class="cumpl-label">${c}</div><div class="cumpl-track"><div class="cumpl-fill" style="width:${pct}%;background:${col};"><span>${pct}%</span></div></div><span style="font-size:11px;color:var(--td);width:50px;">${ok}/${tot}</span></div>`;
  }).join('');
  const regs=getRegistros(); const cntM=new Array(12).fill(0);
  regs.forEach(r=>{ if(r.fecha) cntM[new Date(r.fecha+'T00:00:00').getMonth()]++; });
  const maxM=Math.max(...cntM,1);
  document.getElementById('chart-meses').innerHTML=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'].map((m,i)=>`<div class="bar-row"><div class="bar-label">${m}</div><div class="bar-track"><div class="bar-fill" style="width:${Math.round(cntM[i]/maxM*100)}%;background:var(--blue);"><span>${cntM[i]}</span></div></div></div>`).join('');
  const prx30=[]; (filtArea?getEquipos(filtArea):DATA).forEach(e=>calcIntervenciones(e.intervenciones).forEach(iv=>{ if(iv.dias_para_proxima>=0&&iv.dias_para_proxima<=30) prx30.push(iv.dias_para_proxima); }));
  const cs=[0,0,0,0]; prx30.forEach(d=>{ if(d<=7)cs[0]++;else if(d<=14)cs[1]++;else if(d<=21)cs[2]++;else cs[3]++; });
  const maxS=Math.max(...cs,1);
  document.getElementById('chart-proximas30').innerHTML=['Sem 1 (1-7d)','Sem 2 (8-14d)','Sem 3 (15-21d)','Sem 4 (22-30d)'].map((s,i)=>`<div class="bar-row"><div class="bar-label" style="width:120px;font-size:10px;">${s}</div><div class="bar-track"><div class="bar-fill" style="width:${Math.round(cs[i]/maxS*100)}%;background:${'#ef4444,#f59e0b,#8b5cf6,#3b82f6'.split(',')[i]};"><span>${cs[i]}</span></div></div></div>`).join('');
  document.getElementById('chart-tabla-areas').innerHTML=`<table style="width:100%;border-collapse:collapse;"><thead><tr style="background:var(--s2);"><th style="padding:8px 12px;font-size:11px;color:var(--td);text-align:left;">Área</th><th style="padding:8px 12px;font-size:11px;color:var(--td);text-align:center;">Equipos</th><th style="padding:8px 12px;font-size:11px;color:var(--td);text-align:center;color:var(--red);">Venc.</th><th style="padding:8px 12px;font-size:11px;color:var(--td);text-align:center;color:var(--yellow);">Próx.</th><th style="padding:8px 12px;font-size:11px;color:var(--td);text-align:center;color:var(--green);">OK</th><th style="padding:8px 12px;font-size:11px;color:var(--td);text-align:center;">Cumplim.</th></tr></thead><tbody>${aStats.map(s=>{ const tot=s.v+s.p+s.ok; const pct=tot>0?Math.round(s.ok/tot*100):0; const col=pct>=80?'var(--green)':pct>=50?'var(--yellow)':'var(--red)'; return `<tr><td style="padding:8px 12px;border-top:1px solid var(--bd);font-size:12px;">${s.a.icono} <b style="color:var(--tb);">${s.a.nombre}</b></td><td style="padding:8px 12px;border-top:1px solid var(--bd);text-align:center;font-size:12px;">${getEquipos(s.a.id).length}</td><td style="padding:8px 12px;border-top:1px solid var(--bd);text-align:center;font-size:12px;color:var(--red);">${s.v}</td><td style="padding:8px 12px;border-top:1px solid var(--bd);text-align:center;font-size:12px;color:var(--yellow);">${s.p}</td><td style="padding:8px 12px;border-top:1px solid var(--bd);text-align:center;font-size:12px;color:var(--green);">${s.ok}</td><td style="padding:8px 12px;border-top:1px solid var(--bd);text-align:center;"><span style="font-size:12px;font-weight:700;color:${col};">${pct}%</span></td></tr>`; }).join('')}</tbody></table>`;
}

function renderReportes(){
  let v=0,p=0,ok=0;
  DATA.forEach(e=>calcIntervenciones(e.intervenciones).forEach(i=>{ if(i.estado==='VENCIDO')v++;else if(i.estado==='PROXIMO')p++;else if(i.estado==='OK')ok++; }));
  document.getElementById('rp-total-eq').textContent=DATA.length; document.getElementById('rp-vencidos').textContent=v; document.getElementById('rp-proximos').textContent=p; document.getElementById('rp-ok').textContent=ok;
  const sinEq=DATA.filter(e=>!e.intervenciones||!e.intervenciones.length);
  document.getElementById('rp-sin-tabla').innerHTML=sinEq.length?`<table style="width:100%;border-collapse:collapse;"><thead><tr style="background:var(--s2);"><th style="padding:10px 14px;font-size:11px;color:var(--td);text-align:left;">Equipo</th><th>Categoría</th><th>Código</th></tr></thead><tbody>${sinEq.map(e=>`<tr><td style="padding:8px 14px;font-size:12px;border-top:1px solid var(--bd);">${e.descripcion.substring(0,60)}</td><td style="padding:8px 14px;border-top:1px solid var(--bd);"><span class="cat-badge cat-${e.categoria.toLowerCase()}">${e.categoria}</span></td><td style="padding:8px 14px;font-size:11px;border-top:1px solid var(--bd);font-family:var(--mono);">${e.codigo||'--'}</td></tr>`).join('')}</tbody></table>`:'<div class="empty">Todos los equipos tienen intervenciones</div>';
}

function exportCSV(){
  const areas=getAreas();
  const rows=[['Área','Categoría','Equipo','Código','Frecuencia','Última','Próxima','Días','Estado']];
  areas.forEach(a=>getEquipos(a.id).forEach(e=>{ const ivs=calcIntervenciones(e.intervenciones); if(!ivs.length){ rows.push([a.nombre,e.categoria,e.descripcion,e.codigo||'','--','--','--','--','SIN DATOS']); } else { ivs.forEach(iv=>rows.push([a.nombre,e.categoria,e.descripcion,e.codigo||'',iv.frecuencia,iv.ultima_fecha||'',iv.proxima_fecha||'',iv.dias_para_proxima,iv.estado])); } }));
  const csv=rows.map(r=>r.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\\n');
  const a=document.createElement('a'); a.href='data:text/csv;charset=utf-8,\\uFEFF'+encodeURIComponent(csv); a.download='mantenimiento_2026.csv'; a.click();
}

function exportPDF(){
  const areas=getAreas(), cfg=getConfig(); let v=0,p=0,ok=0,totalEq=0;
  const rows=areas.map(a=>{ const eqs=getEquipos(a.id); totalEq+=eqs.length; return eqs.map(e=>{ const ivs=calcIntervenciones(e.intervenciones); if(!ivs.length) return `<tr><td>${a.nombre}</td><td>${e.categoria}</td><td>${e.descripcion.substring(0,52)}</td><td>--</td><td>--</td><td>--</td><td>SIN DATOS</td></tr>`; return ivs.map(iv=>{ if(iv.estado==='VENCIDO')v++;else if(iv.estado==='PROXIMO')p++;else if(iv.estado==='OK')ok++; return `<tr><td>${a.nombre}</td><td>${e.categoria}</td><td style="font-size:10px;">${e.descripcion.substring(0,52)}</td><td>${iv.frecuencia}</td><td>${iv.ultima_fecha||'--'}</td><td>${iv.proxima_fecha||'--'}</td><td style="color:${iv.estado==='VENCIDO'?'red':iv.estado==='PROXIMO'?'orange':'green'};font-weight:bold;">${iv.estado}</td></tr>`; }).join(''); }).join(''); }).join('');
  const win=window.open('','_blank');
  win.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Reporte Mantenimiento ${cfg.year||2026}</title><style>body{font-family:Arial,sans-serif;padding:16px;font-size:11px;}h1{color:#1e3a5f;font-size:16px;}table{width:100%;border-collapse:collapse;margin-top:10px;}th{background:#1e3a5f;color:#fff;padding:5px 7px;font-size:10px;text-align:left;}td{border:1px solid #ddd;padding:4px 7px;}.st{display:flex;gap:16px;margin:8px 0;padding:8px;background:#f5f5f5;border-radius:4px;}.sv{text-align:center;}.sv b{font-size:20px;display:block;}.login-overlay{position:fixed;inset:0;background:#0a0c10;z-index:9999;display:flex;align-items:center;justify-content:center;}
.login-overlay.hidden{display:none;}
.login-box{width:340px;display:flex;flex-direction:column;align-items:center;}
.login-logo{width:120px;height:120px;object-fit:contain;margin-bottom:16px;}
.login-title{font-size:18px;font-weight:700;color:#e8edf8;text-align:center;line-height:1.3;}
.login-year{font-size:13px;color:#3b82f6;font-weight:600;margin-top:4px;}
.login-empresa{font-size:11px;color:#4a5568;margin:4px 0 24px;}
.login-card{width:100%;background:#0f1218;border:1px solid #1e2535;border-radius:12px;padding:24px;}
.login-card .form-group{margin-bottom:14px;}
.login-card label{font-size:11px;font-weight:600;color:#4a5568;text-transform:uppercase;letter-spacing:.5px;display:block;margin-bottom:5px;}
.login-card input{width:100%;background:#151922;border:1px solid #1e2535;border-radius:6px;padding:9px 12px;color:#e8edf8;font-size:13px;outline:none;font-family:var(--f);box-sizing:border-box;}
.login-card input:focus{border-color:#3b82f6;}
.login-btn{width:100%;padding:10px;background:#3b82f6;border:none;border-radius:6px;color:#fff;font-size:13px;font-weight:600;cursor:pointer;font-family:var(--f);margin-top:4px;}
.login-btn:hover{background:#2563eb;}
.login-error{font-size:12px;color:#ef4444;text-align:center;margin-top:8px;min-height:18px;}
.login-footer{margin-top:24px;text-align:center;}
.login-footer p{font-size:10px;color:#252d40;margin:0;}
.login-footer span{font-size:11px;color:#4a5568;font-weight:600;}
@media print{button{display:none;}}</style></head><body>
  <h1>📋 Plan de Mantenimiento Preventivo ${cfg.year||2026}</h1>
  <p><b>${cfg.empresa||'Planta'}</b> | Fecha: ${new Date().toLocaleDateString('es-CO')} | ${areas.length} áreas | ${totalEq} equipos</p>
  <div class="st"><div class="sv"><b style="color:red;">${v}</b>Vencidos</div><div class="sv"><b style="color:orange;">${p}</b>Próximos</div><div class="sv"><b style="color:green;">${ok}</b>OK</div></div>
  <table><thead><tr><th>Área</th><th>Cat.</th><th>Equipo</th><th>Frecuencia</th><th>Última</th><th>Próxima</th><th>Estado</th></tr></thead><tbody>${rows}</tbody></table>
  <p style="margin-top:14px;font-size:9px;color:#888;">Generado: ${new Date().toLocaleString('es-CO')}</p></body></html>`);
  win.document.close(); setTimeout(()=>win.print(),400);
}

function guardarConfig(){ const cfg=getConfig(); cfg.empresa=document.getElementById('cfg-empresa').value.trim()||'Planta de Beneficio'; cfg.year=document.getElementById('cfg-year').value.trim()||'2026'; lsSet('mtto_config',cfg); document.getElementById('sb-empresa').textContent=cfg.empresa; alert('✅ Guardado'); }
function cambiarPassword(){ const cfg=getConfig(), actual=document.getElementById('cfg-pass-actual').value, nueva=document.getElementById('cfg-pass-nueva').value, conf=document.getElementById('cfg-pass-confirm').value; if(cfg.pass&&actual!==cfg.pass){alert('Contraseña actual incorrecta');return;} if(!nueva||nueva.length<4){alert('Mínimo 4 caracteres');return;} if(nueva!==conf){alert('Las contraseñas no coinciden');return;} cfg.pass=nueva; lsSet('mtto_config',cfg); ['cfg-pass-actual','cfg-pass-nueva','cfg-pass-confirm'].forEach(id=>document.getElementById(id).value=''); alert('✅ Contraseña actualizada'); }

function exportarDatos(){
  const bk={version:2,fecha:new Date().toISOString(),areas:getAreas(),registros:getRegistros(),config:getConfig(),tecnicos:getTecnicos(),equipos_custom:{},deleted_LB:ls('mtto_deleted_LB')||[]};
  getAreas().forEach(a=>{ const c=ls('mtto_equipos_'+a.id); if(c) bk.equipos_custom[a.id]=c; });
  const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([JSON.stringify(bk,null,2)],{type:'application/json'})); a.download='mtto_backup_'+new Date().toISOString().split('T')[0]+'.json'; a.click();
}
function importarDatos(input){ const f=input.files[0]; if(!f) return; const r=new FileReader(); r.onload=e=>{ try{ const d=JSON.parse(e.target.result); if(!confirm('¿Importar? Esto reemplazará datos actuales.')) return; if(d.areas)lsSet('mtto_areas',d.areas); if(d.registros)lsSet('mtto_registros',d.registros); if(d.config)lsSet('mtto_config',d.config); if(d.equipos_custom) Object.entries(d.equipos_custom).forEach(([k,v])=>lsSet('mtto_equipos_'+k,v)); if(d.deleted_LB)lsSet('mtto_deleted_LB',d.deleted_LB); if(d.tecnicos)lsSet('mtto_tecnicos',d.tecnicos); alert('✅ Importado. Recargando...'); location.reload(); }catch(err){alert('Error: '+err.message);} }; r.readAsText(f); }

// ═══════════════════════════════════════════════════════
// TÉCNICOS
// ═══════════════════════════════════════════════════════
async function getTecnicos(){
  try{ const r=await fetch('/api/tecnicos'); const d=await r.json(); return Array.isArray(d)?d:[]; }
  catch(e){ return ls('mtto_tecnicos')||[]; }
}

async function renderTecLista(){
  const tecs = await getTecnicos();
  if(!tecs.length){
    document.getElementById('tec-lista').innerHTML = '<div style="font-size:12px;color:var(--td);padding:8px 0;">Sin técnicos registrados.</div>';
    return;
  }
  document.getElementById('tec-lista').innerHTML = `
    <table style="width:100%;border-collapse:collapse;">
      <thead><tr style="background:var(--s2);">
        <th style="padding:8px 12px;font-size:11px;color:var(--td);text-align:left;">Nombre</th>
        <th style="padding:8px 12px;font-size:11px;color:var(--td);text-align:left;">Cargo</th>
        <th style="padding:8px 12px;font-size:11px;color:var(--td);text-align:center;">Acción</th>
      </tr></thead>
      <tbody>${tecs.map(t=>`<tr>
        <td style="padding:8px 12px;font-size:12px;border-top:1px solid var(--bd);color:var(--tb);">${t.nombre}</td>
        <td style="padding:8px 12px;font-size:12px;border-top:1px solid var(--bd);">
          <span style="font-size:10px;font-weight:600;padding:2px 8px;border-radius:8px;background:${t.cargo==='Supervisor'?'rgba(139,92,246,.15)':'rgba(59,130,246,.15)'};color:${t.cargo==='Supervisor'?'var(--purple)':'var(--blue)'};">${t.cargo}</span>
        </td>
        <td style="padding:8px 12px;border-top:1px solid var(--bd);text-align:center;">
          <button class="btn-icon del" onclick="eliminarTecnico(${t.id})" title="Eliminar">🗑</button>
        </td>
      </tr>`).join('')}</tbody>
    </table>`;
}

async function agregarTecnico(){
  const nombre=document.getElementById('tec-nombre').value.trim();
  const cargo=document.getElementById('tec-cargo').value.trim();
  if(!nombre){alert('Ingresa el nombre del técnico.');return;}
  if(!cargo){alert('Ingresa el cargo del técnico.');return;}
  try{
    const r=await fetch('/api/tecnicos',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre,cargo})});
    if(!r.ok) throw new Error('Error al guardar');
    document.getElementById('tec-nombre').value='';
    document.getElementById('tec-cargo').value='';
    await renderTecLista();
    await populateTecnicoSelect();
  }catch(e){alert('Error: '+e.message);}
}

async function eliminarTecnico(id){
  if(!confirm('¿Eliminar este técnico?')) return;
  try{
    await fetch('/api/tecnicos/'+id,{method:'DELETE'});
    await renderTecLista();
    await populateTecnicoSelect();
  }catch(e){alert('Error: '+e.message);}
}

async function populateTecnicoSelect(){
  const sel = document.getElementById('reg-tecnico');
  if(!sel) return;
  const current = sel.value;
  const tecs = await getTecnicos();
  sel.innerHTML = '<option value="">-- Seleccionar técnico --</option>';
  tecs.forEach(t=>{
    const op = document.createElement('option');
    op.value = t.nombre;
    op.textContent = t.nombre;
    sel.appendChild(op);
  });
  if(current) sel.value = current;
}

// ── SIDEBAR TOGGLE ───────────────────────────────────
function toggleSidebar(){
  const sb = document.querySelector('.sidebar');
  const btn = document.getElementById('sb-toggle-btn');
  sb.classList.toggle('collapsed');
  btn.textContent = sb.classList.contains('collapsed') ? '❯' : '❮';
  btn.title = sb.classList.contains('collapsed') ? 'Expandir menú' : 'Colapsar menú';
}

// ── LOGIN ────────────────────────────────────────────
function doLogin(){
  const cfg = getConfig();
  const user = document.getElementById('login-user').value.trim();
  const pass = document.getElementById('login-pass').value;
  const err  = document.getElementById('login-error');

  if(!user){ err.textContent='Ingresa tu nombre de usuario.'; return; }

  // Si hay contraseña configurada, validarla; si no, entra directo
  if(cfg.pass && pass !== cfg.pass){
    err.textContent='Contraseña incorrecta.';
    document.getElementById('login-pass').value='';
    return;
  }

  document.getElementById('login-overlay').classList.add('hidden');
  err.textContent='';
}

function checkLogin(){
  const cfg = getConfig();
  // Siempre mostrar login para que el usuario se identifique
  document.getElementById('login-year').textContent   = cfg.year||'2026';
  document.getElementById('login-empresa').textContent = cfg.empresa||'Planta de Beneficio';
}

// ── BUSCADOR DE EQUIPOS ───────────────────────────────
let _equiposReg = [];

function populateRegEquipos(){
  populateTecnicoSelect();
  const aId=document.getElementById('reg-area').value||currentArea;
  const s=document.getElementById('reg-equipo'); s.innerHTML='<option value="">-- Seleccionar equipo --</option>';
  getEquipos(aId).forEach(e=>{ const o=document.createElement('option'); o.value=e.id; o.textContent=e.codigo?`[${e.codigo}] ${e.descripcion.substring(0,44)}`:e.descripcion.substring(0,52); s.appendChild(o); });
}

function filtrarEquipos(q){
  const dropdown = document.getElementById('eq-dropdown');
  if(q) document.getElementById('reg-equipo').value = '';
  // Load equipos if not loaded yet
  if(!_equiposReg || !_equiposReg.length){
    const aId = document.getElementById('reg-area').value || currentArea;
    _equiposReg = getEquipos(aId);
  }
  if(!_equiposReg || !_equiposReg.length){ dropdown.style.display='none'; return; }
  if(q !== undefined && q.length < 1){ dropdown.style.display='none'; return; }
  const ql = q.toLowerCase();
  // Use _equiposReg if loaded, else read from hidden select
  let source = _equiposReg;
  if(!source || !source.length){
    const opts = document.getElementById('reg-equipo-hidden').options;
    source = Array.from(opts).filter(o=>o.value).map(o=>({
      id: o.value,
      descripcion: o.textContent.replace(/^\\[.*?\\] /,''),
      codigo: o.textContent.match(/^\\[(.*?)\\]/)?.[1]||''
    }));
  }
  const source2 = _equiposReg.length ? _equiposReg : source;
  const matches = !ql ? source2.slice(0,15) : source2.filter(e =>
    e.descripcion.toLowerCase().includes(ql) ||
    (e.codigo||'').toLowerCase().includes(ql)
  ).slice(0, 15);
  if(!matches.length){ dropdown.style.display='none'; return; }
  dropdown.innerHTML = matches.map(e => `
    <div onclick="seleccionarEquipo(${e.id},'${e.descripcion.replace(/'/g,"\\'")}','${(e.codigo||'').replace(/'/g,"\\'")}');"
      style="padding:8px 12px;cursor:pointer;font-size:12px;border-bottom:1px solid var(--bd);"
      onmouseover="this.style.background='var(--s2)'" onmouseout="this.style.background=''">
      <span style="color:var(--tb);font-weight:600;">${e.descripcion.substring(0,55)}</span>
      ${e.codigo?`<span style="font-size:10px;color:var(--td);margin-left:6px;font-family:var(--mono);">${e.codigo}</span>`:''}
    </div>`).join('');
  dropdown.style.display = 'block';
}

function seleccionarEquipo(id, desc, codigo){
  document.getElementById('reg-equipo').value = id;
  document.getElementById('reg-equipo-search').value = codigo ? `[${codigo}] ${desc}` : desc;
  document.getElementById('eq-dropdown').style.display = 'none';
}

// Cerrar dropdown al hacer clic fuera
document.addEventListener('click', function(e){
  const dd = document.getElementById('eq-dropdown');
  const inp = document.getElementById('reg-equipo-search');
  if(dd && inp && !dd.contains(e.target) && e.target !== inp){
    dd.style.display = 'none';
  }
});

// ── EDITAR REGISTRO ───────────────────────────────────
function editarRegistro(id){
  const regs = getRegistros();
  const r = regs.find(x=>x.id===id);
  if(!r){ alert('Registro no encontrado'); return; }
  document.getElementById('reg-edit-id').value = id;
  document.getElementById('reg-edit-fecha').value = r.fecha;
  document.getElementById('reg-edit-freq').value = r.frecuencia;
  document.getElementById('reg-edit-tecnico').value = r.tecnico||'';
  document.getElementById('reg-edit-obs').value = r.obs||'';
  document.getElementById('reg-edit-overlay').classList.add('on');
}

function guardarEditReg(){
  const id = parseInt(document.getElementById('reg-edit-id').value);
  const regs = getRegistros();
  const idx = regs.findIndex(x=>x.id===id);
  if(idx<0) return;
  regs[idx].fecha      = document.getElementById('reg-edit-fecha').value;
  regs[idx].frecuencia = document.getElementById('reg-edit-freq').value;
  regs[idx].tecnico    = document.getElementById('reg-edit-tecnico').value;
  regs[idx].obs        = document.getElementById('reg-edit-obs').value;
  lsSet('mtto_registros', regs);
  // Update equipo ultima_fecha
  const r = regs[idx];
  const eq = getEquipos(r.area_id).find(e=>e.id==r.equipo_id);
  if(eq){
    const intervs=(eq.intervenciones||[]).map(iv=>iv.frecuencia===r.frecuencia?{...iv,ultima_fecha:r.fecha}:iv);
    saveEquipo(r.area_id,{...eq,intervenciones:intervs});
    cambiarArea(currentArea);
  }
  closeRegEdit();
  renderRegistros();
  alert('✅ Registro actualizado');
}

function eliminarRegistro(){
  const id = parseInt(document.getElementById('reg-edit-id').value);
  if(!confirm('¿Eliminar este registro?')) return;
  lsSet('mtto_registros', getRegistros().filter(x=>x.id!==id));
  closeRegEdit();
  renderRegistros();
  cambiarArea(currentArea);
}

function closeRegEdit(e){
  if(!e||e.target===document.getElementById('reg-edit-overlay'))
    document.getElementById('reg-edit-overlay').classList.remove('on');
}

// ── MOSTRAR TAREA AL SELECCIONAR FRECUENCIA ───────────────────
function mostrarTareaFreq(){
  const eqId = document.getElementById('reg-equipo').value;
  const freq  = document.getElementById('reg-freq').value;
  const hint  = document.getElementById('reg-tarea-hint');
  if(!eqId||!freq){ hint.style.display='none'; return; }
  const aId = document.getElementById('reg-area').value||currentArea;
  const eq  = getEquipos(aId).find(e=>e.id==eqId);
  if(!eq){ hint.style.display='none'; return; }
  const iv = (eq.intervenciones||[]).find(i=>i.frecuencia===freq);
  if(iv&&iv.tarea){ hint.textContent='📋 '+iv.tarea; hint.style.display='block'; }
  else { hint.style.display='none'; }
}

</script>
</body>
</html>
"""

@app.get("/")
def root(): return HTMLResponse(content=HTML)
