from fastapi import FastAPI, Header, Query, HTTPException, Request, Response, BackgroundTasks
from typing import List
from odoo_client import OdooClient
from models import PartnerCreate, PartnerUpdate, EquipoCreate, EquipoUpdate, PreOrderCreate, PreOrderUpdate
import os
from dotenv import load_dotenv
import httpx

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


##########WHATSAPP WEBHOOK CALLS#################

N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")
ODOO_WEBHOOK_URL = os.environ.get("ODOO_WEBHOOK_URL")
WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")

# Basic check to ensure config is loaded
if not all([N8N_WEBHOOK_URL, ODOO_WEBHOOK_URL, WHATSAPP_VERIFY_TOKEN]):
    print("FATAL ERROR: Environment variables are not set.")

# Create an asynchronous HTTP client
client = httpx.AsyncClient(timeout=10.0)

async def forward_webhook(url: str, data: dict, signature256: str | None, signature: str | None):
    """
    Asynchronously sends the webhook data to the specified URL
    and includes the X-Hub-Signature-256 header for Odoo.
    """
    try:
        # Start with base headers
        headers = {'Content-Type': 'application/json'}
        
        # Check if this is the Odoo request
        is_odoo_request = ODOO_WEBHOOK_URL and ODOO_WEBHOOK_URL in url

        # If it is Odoo AND we have a signature, add it to the headers
        if is_odoo_request and signature:
            headers['X-Hub-Signature-256'] = signature256
            headers['X-Hub-Signature'] = signature
            print(f"Forwarding to Odoo with signature...")
        elif is_odoo_request:
            print(f"Warning: Forwarding to Odoo *without* signature.")

        response = await client.post(url, json=data, headers=headers)
        
        if is_odoo_request:
            # --- Detailed Odoo Response (Same as before) ---
            print(f"--- Full Response from Odoo ({url}) ---")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}") 
            print("------------------------------------------")
        else:
            # --- Standard n8n Response (Same as before) ---
            print(f"Forwarded to {url}: Status {response.status_code}")

    except httpx.RequestError as e:
        print(f"Error forwarding to {url}: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanly close the httpx client when the app shuts down.
    """
    await client.aclose()

@app.get("/webhook")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
):
    """
    Handles the WhatsApp Webhook Verification Challenge.
    """
    print("GET request received for verification.")
    if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
        print("Verification successful!")
        return Response(content=challenge, media_type="text/plain")
    else:
        print(f"Verification failed. Token: {token} | Mode: {mode}")
        raise HTTPException(status_code=403, detail="Verification token mismatch")

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    # This is the "FastAPI" way to grab the specific header
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
    x_hub_signature: str | None = Header(None, alias="X-Hub-Signature")
):
    """
    Receives incoming messages from WhatsApp and forwards them
    WITH THE SIGNATURE HEADER to Odoo.
    """
    data = await request.json()

    # Pass the signature to the background tasks
    # The n8n call will ignore it, the Odoo call will use it.
    background_tasks.add_task(forward_webhook, N8N_WEBHOOK_URL, data, x_hub_signature_256, x_hub_signature)
    background_tasks.add_task(forward_webhook, ODOO_WEBHOOK_URL, data, x_hub_signature_256, x_hub_signature)

    return {"status": "received"}
