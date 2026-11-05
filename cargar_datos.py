"""Crea las tablas y carga la data de PRUEBA (ficticia) en la base.

Uso local:   python cargar_datos.py            (usa SQLite: prueba.db)
Uso Render:  DATABASE_URL=postgres://... python cargar_datos.py
"""
import csv, os, random
from datetime import date, timedelta
from sqlalchemy import create_engine, text

DB = os.environ.get("DATABASE_URL", "sqlite:///prueba.db").replace("postgres://", "postgresql://", 1)
eng = create_engine(DB)
random.seed(7)

NOMBRES = ["JUAN", "MARIA", "LUIS", "ROSA", "CARLOS", "ANA", "JOSE", "CARMEN", "PEDRO", "LUCIA", "MIGUEL", "ELENA",
           "JORGE", "SOFIA", "RAUL", "PATRICIA", "DIEGO", "VERONICA", "OSCAR", "GLADYS"]
APELLIDOS = ["PRUEBA", "DEMO", "FICTICIO", "EJEMPLO", "TEST", "SIMULADO", "MUESTRA", "MODELO"]
ESTADOS = [("PAGADO", 50), ("EN PROCESO POR ASEGURADORA", 15), ("PENDIENTE CLIENTE", 15), ("RECHAZADO", 8),
           ("NO ATENDIDO", 7), ("CERRADO ADMINISTRATIVAMENTE", 5)]
ASESORES = ["ASESOR DEMO NORTE", "ASESOR DEMO SUR", "ASESOR DEMO LIMA", "ASESOR DEMO CENTRO"]

req = list(csv.DictReader(open("data/requisitos.csv", encoding="utf-8")))
ags = list(csv.DictReader(open("data/agencias.csv", encoding="utf-8")))
prod_causa = sorted({(r["producto"], r["causa"]) for r in req})

with eng.begin() as c:
    c.execute(text("DROP TABLE IF EXISTS requisitos")); c.execute(text("DROP TABLE IF EXISTS siniestros"))
    c.execute(text("CREATE TABLE requisitos (producto VARCHAR(80), causa VARCHAR(120), orden INT, documento VARCHAR(300))"))
    c.execute(text("""CREATE TABLE siniestros (id INT PRIMARY KEY, dni VARCHAR(12), asegurado VARCHAR(120),
        region VARCHAR(40), agencia VARCHAR(80), producto VARCHAR(80), causa VARCHAR(120), fecha_declaracion DATE,
        monto_reclamado NUMERIC(12,2), monto_indemnizado NUMERIC(12,2), estado VARCHAR(40), fecha_estado DATE,
        documentos_pendientes VARCHAR(600), asesor VARCHAR(80))"""))
    c.execute(text("INSERT INTO requisitos VALUES (:producto,:causa,:orden,:documento)"), req)
    filas = []
    for i in range(1, 401):
        p, ca = random.choice(prod_causa)
        ag = random.choice(ags)
        est = random.choices([e for e, _ in ESTADOS], [w for _, w in ESTADOS])[0]
        fd = date(2026, 1, 1) + timedelta(days=random.randint(0, 300))
        rec = round(random.uniform(500, 60000), 2)
        docs = [r["documento"] for r in req if r["producto"] == p and r["causa"] == ca]
        pend = "; ".join(random.sample(docs, k=min(len(docs), random.randint(1, 2)))) if est == "PENDIENTE CLIENTE" else None
        filas.append(dict(id=i, dni=str(90000000 + i), asegurado=f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)} {random.choice(NOMBRES)}",
                          region=ag["Region"], agencia=ag["Agencia"], producto=p, causa=ca, fecha_declaracion=fd,
                          monto_reclamado=rec, monto_indemnizado=rec if est == "PAGADO" else 0, estado=est,
                          fecha_estado=fd + timedelta(days=random.randint(3, 45)), documentos_pendientes=pend,
                          asesor=random.choice(ASESORES)))
    c.execute(text("""INSERT INTO siniestros VALUES (:id,:dni,:asegurado,:region,:agencia,:producto,:causa,:fecha_declaracion,
        :monto_reclamado,:monto_indemnizado,:estado,:fecha_estado,:documentos_pendientes,:asesor)"""), filas)
print(f"OK: {len(req)} requisitos y {len(filas)} siniestros ficticios (DNI de prueba 90000001 a 90000400)")
