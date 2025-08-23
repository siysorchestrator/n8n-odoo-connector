from fastapi import FastAPI, Query, HTTPException
from typing import List
from odoo_client import OdooClient
from models import PartnerCreate, PartnerUpdate, RepairCreate, RepairUpdate, SaleCreate, SaleUpdate, EquipoCreate,EquipoUpdate
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
        domain.append(("phone", "=", phone))

    result = odoo.search_read(
        "res.partner",
        domain,
        ["id", "name", "phone", "email"],
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
        ["id", "name", "phone", "email"]
    )

@app.post("/partners")
def create_partner(data: PartnerCreate):
    partner_id = odoo.create("res.partner", data.model_dump())
    return {"partner_id": partner_id}

@app.put("/partners/{partner_id}")
def update_partner(partner_id: int, data: PartnerUpdate):
    odoo.write("res.partner", [partner_id], data.model_dump(exclude_unset=True))
    return {"updated": partner_id}

@app.delete("/partners/{partner_id}")
def delete_partner(partner_id: int):
    odoo.unlink("res.partner", [partner_id])
    return {"deleted": partner_id}

# ------------------ OT ------------------
@app.get("/repairs")
def list_repairs(limit: int = 10, partner_id: int | None = Query(None)):
    domain = []
    if partner_id:
        domain.append(('partner_id', '=', partner_id))
    result = odoo.search_read("repair.order", domain, ["id", "partner_id", "product_id", "product_qty", "internal_notes"], limit)
    if not result:
        return result
    return result

@app.get("/repairs/{repair_id}")
def list_partners(repair_id: int):
    return odoo.read(
        "repair.order",
        [repair_id],
        ["id", "partner_id", "product_id", "product_qty", "internal_notes"]
    )

@app.post("/repairs")
def create_repair(data: RepairCreate):
    repair_id = odoo.create("repair.order", data.dict())
    return {"repair_id": repair_id}

@app.put("/repairs/{repair_id}")
def update_repair(repair_id: int, data: RepairUpdate):
    odoo.write("repair.order", [repair_id], data.dict(exclude_unset=True))
    return {"updated": repair_id}

@app.delete("/repairs/{repair_id}")
def delete_repair(repair_id: int):
    odoo.unlink("repair.order", [repair_id])
    return {"deleted": repair_id}

# ------------------ COTIZACIONES ------------------
@app.get("/sales")
def list_sales(limit: int = 10, partner_id: int | None = Query(None)):
    domain = []
    if partner_id:
        domain.append(('partner_id', '=', partner_id))  
    result = odoo.search_read("sale.order", domain, ["id", "partner_id", "order_line"], limit)
    if not result:
        return result
    return result

@app.post("/sales")
def create_sale(data: SaleCreate):
    sale_id = odoo.create("sale.order", data.dict())
    return {"sale_id": sale_id}

@app.put("/sales/{sale_id}")
def update_sale(sale_id: int, data: SaleUpdate):
    odoo.write("sale.order", [sale_id], data.dict(exclude_unset=True))
    return {"updated": sale_id}

@app.delete("/sales/{sale_id}")
def delete_sale(sale_id: int):
    odoo.unlink("sale.order", [sale_id])
    return {"deleted": sale_id}

# ------------------ EQUIPOS ------------------
@app.get("/equipos")
def list_equipos(limit: int = 10, poseedor: int | None = Query(None), serie: str | None = Query(None)):
    domain = []
    if poseedor:
        domain.append(('x_studio_poseedor', '=', poseedor))
    if serie:
        domain.append(('x_studio_numero_de_serie', '=', serie))
    result = odoo.search_read("x_equipos_medicos", domain, ["id", "x_name", "x_studio_poseedor", "x_studio_numero_de_serie"], limit)
    if not result:
        return result
    return result

@app.post("/equipos")
def create_equipos(data: EquipoCreate):
    equipo_id = odoo.create("x_equipos_medicos", data.dict())
    return {"product_id": equipo_id}

@app.put("/equipos/{equipo_id}")
def update_equipos(equipo_id: int, data: EquipoUpdate):
    odoo.write("x_equipos_medicos", [equipo_id], data.dict(exclude_unset=True))
    return {"updated": equipo_id}

@app.delete("/equipos/{equipo_id}")
def delete_equipos(equipo_id: int):
    odoo.unlink("x_equipos_medicos", [equipo_id])
    return {"deleted": equipo_id}
