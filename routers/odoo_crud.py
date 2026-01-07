from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from services.odoo_service import odoo, handle_incoming_n8n_message
from dependencies import verify_api_key
from models.models import (
    PartnerCreate, PartnerUpdate, 
    SaleCreate, 
    RepairCreate, RepairUpdate, 
    EquipoCreate, EquipoUpdate, 
    OdooMessageCreate, TicketCreate, ChatChannelNameUpdate
)

# We protect all routes in this router with the API Key
router = APIRouter(dependencies=[Depends(verify_api_key)])

# ==========================================
# =============== PARTNERS =================
# ==========================================

@router.get("/partners")
def list_partners(limit: int = 10, phone: str | None = None):
    domain = [("phone_sanitized", "=", phone)] if phone else []
    return odoo.search_read(
        "res.partner", 
        domain, 
        ["id", "name", "phone_sanitized", "email", "street", "city", "state_id", "zip"], 
        limit
    )

@router.get("/partners/{partner_id}")
def get_partner(partner_id: int):
    return odoo.read(
        "res.partner",
        [partner_id],
        ["id", "name", "phone_sanitized", "email", "street", "city", "state_id", "zip"]
    )

@router.post("/partners")
def create_partner(data: PartnerCreate):
    partner_id = odoo.create("res.partner", data.model_dump())
    return {"partner_id": partner_id}

@router.put("/partners/{partner_id}")
def update_partner(partner_id: int, data: PartnerUpdate):
    # exclude_unset=True ensures we only send fields that were actually included in the JSON
    odoo.write("res.partner", [partner_id], data.model_dump(exclude_unset=True))
    return {"updated": partner_id}

# ==========================================
# ================ TICKETS =================
# ==========================================

@router.post("/ticket")
def create_ticket(data: TicketCreate):
    tick_id = odoo.create("helpdesk.ticket", data.model_dump())
    return {"ticket_id": tick_id}

@router.get("/ticket/{tick_id}")
def get_ticket(tick_id: int):
    return odoo.read(
        "helpdesk.ticket",
        [tick_id],
        ["ticket_ref", "name", "partner_id", "priority", "partner_phone", "description"]
    )

# ==========================================
# ============ ORDENES DE VENTA ============
# ==========================================

@router.get("/sales")
def list_sales(limit: int = 10, partner_id: int | None = None):
    domain = [('partner_id', '=', partner_id)] if partner_id else []
    return odoo.search_read(
        "sale.order", 
        domain, 
        ["id", "partner_id", "order_line", "repair_order_ids"], 
        limit
    )

@router.get("/sales/{sale_id}")
def get_sale(sale_id: int):
    return odoo.read(
        "sale.order",
        [sale_id],
        ["id", "partner_id", "order_line", "repair_order_ids"]
    )

@router.post("/sales")
def create_sale(data: SaleCreate):
    sale_id = odoo.create("sale.order", data.model_dump())
    return {"sale_id": sale_id}

# ==========================================
# ================= REPAIRS ================
# ==========================================

@router.get("/repairs")
def list_repairs(limit: int = 10, partner_id: int | None = None):
    domain = [('partner_id', '=', partner_id)] if partner_id else []
    return odoo.search_read(
        "repair.order", 
        domain, 
        ["id", "partner_id", "product_id", "product_qty", "internal_notes"], 
        limit
    )

@router.get("/repairs/{repair_id}")
def get_repair(repair_id: int):
    return odoo.read(
        "repair.order",
        [repair_id],
        ["id", "partner_id", "product_id", "product_qty", "internal_notes"]
    )

@router.post("/repairs")
def create_repair(data: RepairCreate):
    repair_id = odoo.create("repair.order", data.model_dump())
    return {"repair_id": repair_id}

@router.put("/repairs/{repair_id}")
def update_repair(repair_id: int, data: RepairUpdate):
    odoo.write("repair.order", [repair_id], data.model_dump(exclude_unset=True))
    return {"updated": repair_id}

# ==========================================
# ============ EQUIPOS MEDICOS =============
# ==========================================

@router.get("/equipos")
def list_equipos(limit: int = 10, poseedor: int | None = None, serie: str | None = None):
    domain = []
    if poseedor:
        domain.append(('x_studio_poseedor', '=', poseedor))
    if serie:
        domain.append(('x_studio_numero_de_serie', '=', serie))
        
    return odoo.search_read(
        "x_equipo_medico", 
        domain, 
        ["id", "x_name", "x_studio_numero_de_serie", "x_studio_clasificacin", "x_studio_marca_equipo", "x_studio_modelo_equipo", "x_studio_propietario", "x_studio_poseedor", "x_studio_notas_1"], 
        limit
    )

@router.get("/equipos/{equipo_id}")
def get_equipo(equipo_id: int):
    return odoo.read(
        "x_equipo_medico",
        [equipo_id],
        ["id", "x_name", "x_studio_numero_de_serie", "x_studio_clasificacin", "x_studio_marca_equipo", "x_studio_modelo_equipo", "x_studio_propietario", "x_studio_poseedor", "x_studio_notas_1"]
    )

@router.post("/equipos")
def create_equipo(data: EquipoCreate):
    equipo_id = odoo.create("x_equipo_medico", data.model_dump())
    return {"id": equipo_id}

@router.put("/equipos/{equipo_id}")
def update_equipo(equipo_id: int, data: EquipoUpdate):
    odoo.write("x_equipo_medico", [equipo_id], data.model_dump(exclude_unset=True))
    return {"updated": equipo_id}

# ==========================================
# ============ X_INSTALACIONES =============
# ==========================================

@router.get("/instalaciones")
def list_instalaciones(limit: int = 1, serial_code: str | None = None):
    domain = []
    if serial_code:
        domain.append(('x_codigo_serial', '=', serial_code))
    
    fields_to_fetch = [
        'x_id_item',
        'x_nombre',
        'x_fecha',
        'x_codigo_serial',
        'x_equipo',
        'x_meses'
    ]
    
    return odoo.search_read(
        "x_instalaciones",
        domain,
        fields_to_fetch,
        limit
    )

@router.get("/instalaciones/serial/{serial_code}")
def get_instalacion_by_serial(serial_code: str):
    fields_to_fetch = [
        "id",
        'x_id_item',
        'x_nombre',
        'x_fecha',
        'x_codigo_serial',
        'x_equipo',
        'x_meses'
    ]
    
    return odoo.search_read(
        "x_instalaciones",
        [('x_codigo_serial', '=', serial_code)],
        fields_to_fetch,
        limit=1
    )

@router.get("/instalaciones/{instalacion_id}")
def get_instalacion(instalacion_id: int):
    fields_to_fetch = [
        "id",
        'x_id_item',
        'x_nombre',
        'x_fecha',
        'x_codigo_serial',
        'x_equipo',
        'x_meses'
    ]
    return odoo.read(
        "x_instalaciones",
        [instalacion_id],
        fields_to_fetch
    )

# ==========================================
# ========== WHATSAPP LOGGING ==============
# ==========================================

@router.post("/log_message")
def log_message_endpoint(data: OdooMessageCreate):
    try:
        result = handle_incoming_n8n_message(data)
        return {"status": "success", **result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))