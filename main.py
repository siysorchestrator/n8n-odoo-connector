from fastapi import FastAPI, Query, HTTPException
from typing import List
from odoo_client import OdooClient
from models import PartnerCreate, PartnerUpdate, RepairCreate, RepairUpdate, SaleCreate, SaleUpdate, ProductCreate, ProductUpdate
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
    partner_id = odoo.create("res.partner", data.dict())
    return {"partner_id": partner_id}

@app.put("/partners/{partner_id}")
def update_partner(partner_id: int, data: PartnerUpdate):
    odoo.write("res.partner", [partner_id], data.dict(exclude_unset=True))
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

# ------------------ PRODUCTOS/EQUIPOS ------------------
@app.get("/products")
def list_products(limit: int = 10, partner_id: int | None = Query(None)):
    domain = []
    if partner_id:
        domain.append(('partner_id', '=', partner_id))
    result = odoo.search_read("product.product", [], ["id", "name", "list_price", "qty_available"], limit)
    if not result:
        return result
    return result

@app.post("/products")
def create_product(data: ProductCreate):
    product_id = odoo.create("product.product", data.dict())
    return {"product_id": product_id}

@app.put("/products/{product_id}")
def update_product(product_id: int, data: ProductUpdate):
    odoo.write("product.product", [product_id], data.dict(exclude_unset=True))
    return {"updated": product_id}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    odoo.unlink("product.product", [product_id])
    return {"deleted": product_id}
