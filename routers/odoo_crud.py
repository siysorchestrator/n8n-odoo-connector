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
    
# ==========================================
# ============= CHAT CHANNELS ==============
# ==========================================

@router.get("/chat_channels/by_member/{partner_id}")
def get_channels_by_member(partner_id: int, limit: int = 20):
    """
    Obtener canales donde un partner específico es miembro
    
    Args:
        partner_id: ID del partner/res.partner a buscar
        limit: Límite de resultados
    """
    try:
        print(f"[DEBUG] get_channels_by_member llamado: partner_id={partner_id}, limit={limit}")
        
        # Primero verificar si el partner existe
        try:
            partner = odoo.read("res.partner", [partner_id], ["id", "name"])
            if not partner:
                raise HTTPException(status_code=404, detail=f"Partner con ID {partner_id} no encontrado")
            print(f"[DEBUG] Partner encontrado: {partner[0]['name']}")
        except Exception as e:
            print(f"[DEBUG] Error al buscar partner: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Partner con ID {partner_id} no encontrado")
        
        # Buscar canales de tipo chat (WhatsApp sería un tipo específico o chat general)
        # Usamos un límite mayor inicial y filtramos después
        all_channels = odoo.search_read(
            "discuss.channel", 
            [('channel_type', '=', 'chat')],  # Solo canales de tipo chat
            ["id", "name", "channel_type", "description", "channel_partner_ids", "uuid"],
            limit=limit * 3  # Buscamos más inicialmente
        )
        
        print(f"[DEBUG] Canales encontrados inicialmente: {len(all_channels)}")
        
        # Filtrar canales donde el partner está presente
        filtered_channels = []
        for channel in all_channels:
            member_partner_ids = channel.get("channel_partner_ids", [])
            
            if partner_id in member_partner_ids:
                filtered_channels.append({
                    "id": channel["id"],
                    "name": channel["name"],
                    "channel_type": channel["channel_type"],
                    "description": channel.get("description", ""),
                    "uuid": channel.get("uuid", ""),
                    "member_count": len(member_partner_ids)
                })
        
        print(f"[DEBUG] Canales filtrados donde el partner es miembro: {len(filtered_channels)}")
        
        return {
            "partner_id": partner_id,
            "partner_name": partner[0]['name'] if partner else "Desconocido",
            "count": len(filtered_channels),
            "channels": filtered_channels[:limit]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Error in get_channels_by_member: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chat_channels/{channel_id}/add_users")
def add_users_to_channel(
    channel_id: int,
    user_ids: List[int] = Query(..., description="IDs de usuarios (res.users) a agregar")
):
    """
    Agregar usuarios específicos a un canal existente
    
    Args:
        channel_id: ID del canal existente
        user_ids: Lista de IDs de usuarios (res.users) a agregar
    """
    try:
        print(f"[DEBUG] add_users_to_channel llamado: channel_id={channel_id}, user_ids={user_ids}")
        
        # 1. Verificar que el canal existe
        channel = odoo.read("discuss.channel", [channel_id], ["id", "name", "channel_partner_ids"])
        if not channel:
            raise HTTPException(status_code=404, detail=f"Canal con ID {channel_id} no encontrado")
        
        channel_name = channel[0].get('name', f'Canal {channel_id}')
        current_partner_ids = channel[0].get('channel_partner_ids', [])
        print(f"[DEBUG] Canal encontrado: {channel_name}, miembros actuales: {len(current_partner_ids)}")
        
        # 2. Obtener los partner IDs de los usuarios
        print(f"[DEBUG] Obteniendo partners para usuarios: {user_ids}")
        users = odoo.read("res.users", user_ids, ["partner_id", "name"])
        
        partner_ids_to_add = []
        user_info = []
        for user in users:
            if user and 'partner_id' in user and user['partner_id']:
                partner_id = user['partner_id'][0]
                user_name = user.get('name', f'Usuario {user["id"]}')
                partner_ids_to_add.append(partner_id)
                user_info.append({
                    "user_id": user["id"],
                    "user_name": user_name,
                    "partner_id": partner_id
                })
        
        if not partner_ids_to_add:
            raise HTTPException(status_code=400, detail="No se encontraron partners para los usuarios especificados")
        
        print(f"[DEBUG] Partners a agregar: {partner_ids_to_add}")
        print(f"[DEBUG] Info usuarios: {user_info}")
        
        # 3. Filtrar partners que ya están en el canal
        new_partner_ids = [pid for pid in partner_ids_to_add if pid not in current_partner_ids]
        
        if not new_partner_ids:
            return {
                "status": "info",
                "message": "Todos los usuarios ya son miembros del canal",
                "channel_id": channel_id,
                "channel_name": channel_name,
                "added_count": 0,
                "already_members": [info for info in user_info if info["partner_id"] in current_partner_ids]
            }
        
        print(f"[DEBUG] Nuevos partners a agregar: {new_partner_ids}")
        
        # 4. Agregar cada partner al canal
        successfully_added = []
        failed_to_add = []
        
        for partner_id in new_partner_ids:
            try:
                # Usar (4, id, 0) para agregar a la lista de muchos-a-muchos
                odoo.write("discuss.channel", [channel_id], {
                    'channel_partner_ids': [(4, partner_id, 0)]
                })
                successfully_added.append(partner_id)
                print(f"[DEBUG] Partner {partner_id} agregado exitosamente")
            except Exception as e:
                print(f"[DEBUG] Error al agregar partner {partner_id}: {str(e)}")
                failed_to_add.append({
                    "partner_id": partner_id,
                    "error": str(e)
                })
        
        # 5. Preparar respuesta
        added_user_info = []
        for info in user_info:
            if info["partner_id"] in successfully_added:
                added_user_info.append(info)
        
        response = {
            "status": "success" if successfully_added else "partial",
            "message": f"Se agregaron {len(successfully_added)} de {len(new_partner_ids)} usuarios al canal",
            "channel_id": channel_id,
            "channel_name": channel_name,
            "added_count": len(successfully_added),
            "added_users": added_user_info,
            "total_members_now": len(current_partner_ids) + len(successfully_added)
        }
        
        if failed_to_add:
            response["failed_to_add"] = failed_to_add
            response["failed_count"] = len(failed_to_add)
        
        print(f"[DEBUG] Respuesta final: {response}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Error in add_users_to_channel: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al agregar usuarios al canal: {str(e)}")
