from fastapi import FastAPI, Query, HTTPException
from typing import List
from odoo_client import OdooClient
from models import PartnerCreate, PartnerUpdate, EquipoCreate, EquipoUpdate, PreOrderCreate, PreOrderUpdate
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Odoo Proxy API")


odoo = OdooClient(
    url = os.getenv("XMLRPC_SERVER_URL"),
    db = os.getenv("XMLRPC_DB_NAME"),
    username = os.getenv("XMLRPC_USERNAME"),
    password = os.getenv("XMLRPC_PASSWORD")
)

# ------------------ CLIENTES ------------------
@app.get("/partners")
def list_partners(limit: int = 10, phone: str | None = Query(None)):
    domain = []
    if phone:
        domain.append(("phone_sanitized", "=", phone))

    result = odoo.search_read(
        "res.partner",
        domain,
        ["id", "name", "phone_sanitized", "email", "street", "city", "state_id", "zip"],
        limit
    )
    if not result:
        return result
    return result

@app.get("/partners/{partner_id}")
def list_partners(partner_id: int):
    return odoo.read(
        "res.partner",
        [partner_id],
        ["id", "name", "phone_sanitized", "email", "street", "city", "state_id", "zip"]
    )

@app.post("/partners")
def create_partner(data: PartnerCreate):
    partner_id = odoo.create("res.partner", data.model_dump())
    return {"partner_id": partner_id}

@app.put("/partners/{partner_id}")
def update_partner(partner_id: int, data: PartnerUpdate):
    odoo.write("res.partner", [partner_id], data.model_dump(exclude_unset=True))
    return {"updated": partner_id}

# ------------------ PRE-ORDENES ------------------
@app.post("/preorder")
def create_sale(data: PreOrderCreate):
    order_id = odoo.create("x_pre_orden", data.model_dump())
    return {"order_id": order_id}

# ------------------ EQUIPOS ------------------
@app.get("/equipos")
def list_equipos(limit: int = 10, poseedor: int | None = Query(None), serie: str | None = Query(None)):
    domain = []
    if poseedor:
        domain.append(('x_studio_poseedor', '=', poseedor))
    if serie:
        domain.append(('x_studio_numero_de_serie', '=', serie))
    result = odoo.search_read(
        "x_equipo_medico", 
        domain, 
        ["id", "x_name", "x_studio_numero_de_serie", "x_studio_clasificacin", "x_studio_marca_equipo", "x_studio_modelo_equipo", "x_studio_propietario", "x_studio_poseedor", "x_studio_notas_1"], 
        limit
    )
    if not result:
        return result
    return result

@app.get("/equipos/{equipo_id}")
def list_equipos(equipo_id: int):
    return odoo.read(
        "x_equipo_medico",
        [equipo_id],
        ["id", "x_name", "x_studio_numero_de_serie", "x_studio_clasificacin", "x_studio_marca_equipo", "x_studio_modelo_equipo", "x_studio_propietario", "x_studio_poseedor", "x_studio_notas_1"]
    )

@app.post("/equipos")
def create_equipos(data: EquipoCreate):
    equipo_id = odoo.create("x_equipo_medico", data.model_dump())
    return {"id": equipo_id}

@app.put("/equipos/{equipo_id}")
def update_equipos(equipo_id: int, data: EquipoUpdate):
    odoo.write("x_equipo_medico", [equipo_id], data.model_dump(exclude_unset=True))
    return {"updated": equipo_id}
