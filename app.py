"""API + web (PWA) de prueba: Consultas de Siniestros. SOLO DATA FICTICIA."""
import os
import unicodedata
from urllib.parse import quote
from fastapi import FastAPI, HTTPException
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


def _norm(s):  # mayusculas y sin tildes, para comparar nombres de seguros
    return "".join(c for c in unicodedata.normalize("NFD", s.strip().upper()) if unicodedata.category(c) != "Mn")


# ASESORES_WSP="VIDA CAJA=51911111111;ONCOLOGICO=51922222222;..."  (los seguros sin numero usan ASESOR_WSP)
ASESORES_WSP = {_norm(k): v.strip() for k, _, v in
                (p.partition("=") for p in os.environ.get("ASESORES_WSP", "").split(";") if "=" in p)}


@app.get("/api/asesor")
def asesor(producto: str = ""):
    numero = ASESORES_WSP.get(_norm(producto), ASESOR_WSP)
    texto = f"Hola, necesito ayuda con un siniestro del seguro {producto}" if producto else \
        "Hola, necesito ayuda con un siniestro"
    return {"whatsapp": f"https://wa.me/{numero}?text={quote(texto)}"}


PUBLICOS = {"index.html", "manifest.json", "sw.js", "icon-192.png", "icon-512.png"}


def archivo(n):  # funciona con los archivos en la raiz o dentro de static/
    return n if os.path.exists(n) else os.path.join("static", n)


@app.get("/static/{nombre}")
def estaticos(nombre: str):
    if nombre not in PUBLICOS:
        raise HTTPException(404)
    return FileResponse(archivo(nombre))


@app.get("/")
def index():
    return FileResponse(archivo("index.html"))


@app.get("/sw.js")
def sw():
    return FileResponse(archivo("sw.js"), media_type="application/javascript")
