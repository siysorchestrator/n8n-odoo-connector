from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from services.odoo_service import odoo, handle_incoming_n8n_message
from dependencies import verify_api_key
from models import PartnerCreate, PartnerUpdate, OdooMessageCreate # Import others...

# We protect all routes in this router with the API Key
router = APIRouter(dependencies=[Depends(verify_api_key)])

# --- PARTNERS ---
@router.get("/partners")
def list_partners(limit: int = 10, phone: str | None = None):
    domain = [("phone_sanitized", "=", phone)] if phone else []
    return odoo.search_read("res.partner", domain, ["id", "name", "phone_sanitized", "email", "street", "city", "state_id", "zip"], limit)

@router.post("/partners")
def create_partner(data: PartnerCreate):
    return {"partner_id": odoo.create("res.partner", data.model_dump())}

@router.put("/partners/{partner_id}")
def update_partner(partner_id: int, data: PartnerUpdate):
    odoo.write("res.partner", [partner_id], data.model_dump(exclude_unset=True))
    return {"updated": partner_id}

# --- MESSAGES (Complex Logic) ---
@router.post("/log_message")
def log_message_endpoint(data: OdooMessageCreate):
    try:
        result = handle_incoming_n8n_message(data)
        return {"status": "success", **result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ... Add the Sales, Repairs, Equipos endpoints here following the same pattern ...