"""API + web (PWA) de prueba: Consultas de Siniestros. SOLO DATA FICTICIA."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, text

DB = os.environ.get("DATABASE_URL", "sqlite:///prueba.db").replace("postgres://", "postgresql://", 1)
eng = create_engine(DB, pool_pre_ping=True)
ASESOR_WSP = os.environ.get("ASESOR_WSP", "51999999999")  # numero ficticio
app = FastAPI(title="Consultas Siniestros (prueba)")


def q(sql, **p):
    with eng.connect() as c:
        return [dict(r._mapping) for r in c.execute(text(sql), p)]


@app.get("/api/productos")
def productos():
    return [r["producto"] for r in q("SELECT DISTINCT producto FROM requisitos ORDER BY producto")]


@app.get("/api/causas")
def causas(producto: str):
    return [r["causa"] for r in q("SELECT DISTINCT causa FROM requisitos WHERE producto=:p ORDER BY causa", p=producto)]


@app.get("/api/requisitos")
def requisitos(producto: str, causa: str):
    return [r["documento"] for r in q("SELECT documento FROM requisitos WHERE producto=:p AND causa=:c ORDER BY orden",
                                      p=producto, c=causa)]


@app.get("/api/estado/{dni}")
def estado(dni: str):
    dni = dni.strip()
    if not dni.isdigit() or not 6 <= len(dni) <= 12:
        raise HTTPException(400, "DNI no valido")
    rows = q("""SELECT asegurado, agencia, producto, causa, fecha_declaracion, estado, fecha_estado,
                monto_reclamado, monto_indemnizado, documentos_pendientes, asesor
                FROM siniestros WHERE dni=:d ORDER BY fecha_declaracion DESC""", d=dni)
    for r in rows:
        for k in ("fecha_declaracion", "fecha_estado"):
            r[k] = str(r[k])[:10]
        for k in ("monto_reclamado", "monto_indemnizado"):
            r[k] = float(r[k] or 0)
    return rows


@app.get("/api/asesor")
def asesor():
    return {"whatsapp": f"https://wa.me/{ASESOR_WSP}?text=Hola,%20necesito%20ayuda%20con%20un%20siniestro"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/sw.js")
def sw():
    return FileResponse("static/sw.js", media_type="application/javascript")
