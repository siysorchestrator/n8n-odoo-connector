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
    if is_employee_user(partner_id):
        raise HTTPException(
            status_code=403,
            detail=f"No se puede actualizar el partner {partner_id} porque es un empleado (usuario del sistema)."
        )
    
    odoo.write("res.partner", [partner_id], data.model_dump(exclude_unset=True))
    return {"updated": partner_id, "message": "Partner actualizado exitosamente"}

def is_employee_user(partner_id):
    try:
        user_ids = odoo.search_read("res.users", [["partner_id", "=", partner_id]])
        
        if not user_ids:
            return False
        
        user = odoo.read("res.users", [user_ids[0]], ["groups_id", "share"])[0]
        
        internal_group_ids = odoo.search_read("res.groups", [
            ["name", "=", "base.group_user"]
        ])
        
        if not internal_group_ids:
            return True
        
        is_internal = internal_group_ids[0] in user.get("groups_id", [])
        is_not_portal = not user.get("share", False)
        
        return is_internal or is_not_portal
        
    except Exception as e:
        print(f"Error verificando si es empleado: {str(e)}")
        return False

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

# ==========================================
# ================ LABEL ===================
# ==========================================   

@router.put("/label/{label_name}")
def add_label(label_name: str, ticket_id: int = Query(..., description="ID del ticket")):
    
    try:
        print(f"DEBUG: Agregando etiqueta '{label_name}' al ticket {ticket_id}")
        
        existing_labels = odoo.search_read(
            "helpdesk.tag",
            [("name", "=", label_name)],
            ["id", "name"]
        )
        print(f"DEBUG: Etiquetas existentes encontradas: {existing_labels}")
        
        if existing_labels:
            tag_id = existing_labels[0]["id"]
            print(f"DEBUG: Usando etiqueta existente con ID: {tag_id}")
        else:
            print(f"DEBUG: Creando nueva etiqueta: {label_name}")
            tag_id = odoo.create("helpdesk.tag", {
                "name": label_name
            })
            print(f"DEBUG: Nueva etiqueta creada con ID: {tag_id}")
        
        ticket_data = odoo.read(
            "helpdesk.ticket",
            [ticket_id],
            ["tag_ids", "name"]
        )
        print(f"DEBUG: Datos del ticket: {ticket_data}")
        
        if not ticket_data:
            raise HTTPException(status_code=404, detail=f"Ticket con ID {ticket_id} no encontrado")

        current_tags = ticket_data[0].get("tag_ids")
        print(f"DEBUG: Etiquetas actuales del ticket: {current_tags}")

        if current_tags is None:
            current_tags = []

        if isinstance(current_tags, bool):
            current_tags = []

        if isinstance(current_tags, list):
            current_tags = [int(tag) for tag in current_tags if tag is not None]
        
        print(f"DEBUG: Etiquetas procesadas: {current_tags}")

        if tag_id in current_tags:
            return {
                "message": f"La etiqueta '{label_name}' ya estaba asignada al ticket",
                "ticket_id": ticket_id,
                "tag_id": tag_id,
                "status": "already_assigned"
            }

        new_tags = current_tags + [tag_id]
        print(f"DEBUG: Nuevas etiquetas a asignar: {new_tags}")

        update_data = {
            "tag_ids": [(6, 0, new_tags)]
        }
        print(f"DEBUG: Datos a enviar a Odoo: {update_data}")
        
        odoo.write("helpdesk.ticket", [ticket_id], update_data)
        
        return {
            "message": f"Etiqueta '{label_name}' agregada exitosamente al ticket {ticket_id}",
            "ticket_id": ticket_id,
            "tag_id": tag_id,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR DETALLADO:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al agregar etiqueta: {str(e)}")