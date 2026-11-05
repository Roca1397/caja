# Prototipo – Consultas de Siniestros (DATOS FICTICIOS)

Web para celular (se puede "instalar" como app) con 3 opciones:
1. **Requisitos por seguro** → eliges seguro y qué ocurrió → lista de documentos.
2. **Estado de siniestro** → escribes el DNI → estado, montos y documentos pendientes.
3. **Contactar a un asesor** → abre WhatsApp con el número que configures.

> Solo data inventada (DNI 90000001 al 90000400). No subir bases reales de la Caja.
> La lista de requisitos es REFERENCIAL: reemplazar `data/requisitos.csv` por la oficial.

## Archivos
- `app.py` – API y web.
- `cargar_datos.py` – crea las tablas y carga requisitos + 400 siniestros ficticios.
- `data/requisitos.csv` – producto, causa, orden, documento (edítalo en Excel y guarda como CSV UTF-8).
- `data/agencias.csv` – agencias y regiones.
- `static/` – pantalla (index.html), ícono y archivos para instalar en el celular.
- `render.yaml` – configuración para Render (web + base PostgreSQL gratis).

## Probar en tu PC
```
pip install -r requirements.txt
python cargar_datos.py
uvicorn app:app --reload
```
Abre http://localhost:8000

## Publicar en Render
1. Crea un repositorio en GitHub y sube esta carpeta.
2. En render.com → **New → Blueprint** → elige el repositorio. Render lee `render.yaml`
   y crea la base `siniestros-demo-db` y el servicio web.
3. Espera que termine el deploy y abre la URL que te da (…onrender.com).
4. En el celular: abre la URL en Chrome → menú ⋮ → **Agregar a pantalla principal**.

Notas del plan gratis: el servicio "se duerme" sin uso (la 1ra consulta tarda ~30-50 s)
y la base PostgreSQL gratis expira a los 30 días.

## Cambiar el número del asesor
En Render → servicio → Environment → `ASESOR_WSP` (formato 51 + número, sin +).
