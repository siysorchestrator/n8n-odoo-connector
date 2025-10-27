#RESPONSABILIDADES:
#1. Ser el Broker para las comunicaciones entre Odoo y el agente de N8N. Usamos FastAPI para hacerlo simple.
#2. Fungir como proxy entre whatsapp business y odoo/N8N. Recibe los mensajes y los reenvía a Odoo y N8N sin alteraciones

from fastapi import FastAPI, Header, Query, HTTPException, Request, Response, BackgroundTasks
from typing import List
from odoo_client import OdooClient
from models import PartnerCreate, PartnerUpdate, EquipoCreate, EquipoUpdate, PreOrderCreate, SaleCreate, OdooMessageCreate, RepairCreate, RepairUpdate
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

API_SECRET_KEY = os.getenv("PROXY_API_SECRET_KEY")

#############################################################################
############### ------ n8n - Odoo CONNECTION LAYER ------ ###################
#############################################################################

# ------------------ CLIENTES ------------------
@app.get("/partners")
def list_partners(limit: int = 10, phone: str | None = Query(None), x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
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
def list_partners(partner_id: int, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return odoo.read(
        "res.partner",
        [partner_id],
        ["id", "name", "phone_sanitized", "email", "street", "city", "state_id", "zip"]
    )

@app.post("/partners")
def create_partner(data: PartnerCreate, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    partner_id = odoo.create("res.partner", data.model_dump())
    return {"partner_id": partner_id}

@app.put("/partners/{partner_id}")
def update_partner(partner_id: int, data: PartnerUpdate, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    odoo.write("res.partner", [partner_id], data.model_dump(exclude_unset=True))
    return {"updated": partner_id}

# ------------------ PRE-ORDENES ------------------
@app.get("/preorder/{preorder_id}")
def list_preorders(preorder_id: int, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return odoo.read(
        "x_pre_orden",
        [preorder_id],
        ["id", "x_name", "x_studio_cliente", "x_studio_tipo_de_servicio", "x_studio_marca_equipo", "x_studio_modelo_equipo", "x_studio_serie_equipo", "x_studio_descripcion_de_servicio"]
    )

@app.post("/preorder")
def create_sale(data: PreOrderCreate, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    order_id = odoo.create("x_pre_orden", data.model_dump())
    return {"order_id": order_id}

# ------------------ ORDENES DE VENTA ------------------
@app.get("/sales")
def list_sales(limit: int = 10, partner_id: int | None = Query(None), x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    domain = []
    if partner_id:
        domain.append(('partner_id', '=', partner_id))  
    result = odoo.search_read("sale.order", domain, ["id", "partner_id", "order_line", "repair_order_ids"], limit)
    if not result:
        return result
    return result

@app.get("/sales/{sale_id}")
def list_sales(sale_id: int, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return odoo.read(
        "sale.order",
        [sale_id],
        ["id", "partner_id", "order_line", "repair_order_ids"]
    )

@app.post("/sales")
def create_sale(data: SaleCreate, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    sale_id = odoo.create("sale.order", data.model_dump())
    return {"sale_id": sale_id}

# ------------------ OT ------------------
@app.get("/repairs")
def list_repairs(limit: int = 10, partner_id: int | None = Query(None), x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    domain = []
    if partner_id:
        domain.append(('partner_id', '=', partner_id))
    result = odoo.search_read("repair.order", domain, ["id", "partner_id", "product_id", "product_qty", "internal_notes"], limit)
    if not result:
        return result
    return result

@app.get("/repairs/{repair_id}")
def list_partners(repair_id: int, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return odoo.read(
        "repair.order",
        [repair_id],
        ["id", "partner_id", "product_id", "product_qty", "internal_notes"]
    )

@app.post("/repairs")
def create_repair(data: RepairCreate, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    repair_id = odoo.create("repair.order", data.model_dump())
    return {"repair_id": repair_id}

@app.put("/repairs/{repair_id}")
def update_repair(repair_id: int, data: RepairUpdate, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    odoo.write("repair.order", [repair_id], data.model_dump(exclude_unset=True))
    return {"updated": repair_id}

# ------------------ EQUIPOS ------------------
@app.get("/equipos")
def list_equipos(limit: int = 10, poseedor: int | None = Query(None), serie: str | None = Query(None), x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
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
def list_equipos(equipo_id: int, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return odoo.read(
        "x_equipo_medico",
        [equipo_id],
        ["id", "x_name", "x_studio_numero_de_serie", "x_studio_clasificacin", "x_studio_marca_equipo", "x_studio_modelo_equipo", "x_studio_propietario", "x_studio_poseedor", "x_studio_notas_1"]
    )

@app.post("/equipos")
def create_equipos(data: EquipoCreate, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    equipo_id = odoo.create("x_equipo_medico", data.model_dump())
    return {"id": equipo_id}

@app.put("/equipos/{equipo_id}")
def update_equipos(equipo_id: int, data: EquipoUpdate, x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    odoo.write("x_equipo_medico", [equipo_id], data.model_dump(exclude_unset=True))
    return {"updated": equipo_id}

# ------------------ WHATSAPP MESSAGES ------------------
@app.post("/log_message")
def log_message(data: OdooMessageCreate, x_api_key: str = Header(None)):
    """
    Recibe un mensaje saliente de n8n y lo archiva en el modelo discuss.channel
    para que aparezca en la interfaz de chat de whatsapp de Odoo.
    Esto nos permitirá ver las interacciones con el bot.
    """
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        BOT_PARTNER_ID = 3  #Bot's Partner ID (from the Contact's URL)
        
        channel_domain = [('whatsapp_number', '=', data.contact_phone)]
        channel_data = odoo.search_read("discuss.channel", channel_domain, ["id"], limit=1)
        channel_id = 0
        if channel_data:
            channel_id = channel_data[0]['id']
        else:
            raise HTTPException(status_code=404, detail="Discussion channel was not found.")

        mail_message_id = odoo.models.execute_kw(
            odoo.db,                  # 1. Database name
            odoo.uid,                 # 2. User ID
            odoo.password,            # 3. Password/API Key
            'discuss.channel',        # 4. Model
            'message_post',           # 5. Method
            [channel_id],             # Positional arguments (the ID of the channel to post on)
            {                         # Keyword arguments (the message values)
                'body': data.message_body,
                'subject': "from n8n",
                'message_type': 'whatsapp_message',
                'subtype_id': 1,
                'author_id': BOT_PARTNER_ID,
            }
        )

        if not mail_message_id:
            raise HTTPException(status_code=500, detail="Failed to post message to channel in Odoo.")

        if isinstance(mail_message_id, list) and mail_message_id:
            mail_message_id = mail_message_id[0]

        return {
            "status": "success",
            "detail": "Message successfully logged and visible in discuss.channel.",
            "channel_id": channel_id,
            "mail_message_id": mail_message_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )


#############################################################################
############# ------ WHATSAPP BUSINESS WEBHOOK CALLS ------ #################
#############################################################################

N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")
ODOO_WEBHOOK_URL = os.environ.get("ODOO_WEBHOOK_URL")
WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")

if not all([N8N_WEBHOOK_URL, ODOO_WEBHOOK_URL, WHATSAPP_VERIFY_TOKEN]):
    print("FATAL ERROR: Environment variables are not set.")

client = httpx.AsyncClient(timeout=10.0)

async def forward_webhook(url: str, body: bytes, signature: str | None):
    """
    Reenvía de manera asíncrona el body y la firma del request. El body es importante que no se altere.
    """
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        
        is_odoo_request = ODOO_WEBHOOK_URL and ODOO_WEBHOOK_URL in url

        if is_odoo_request and signature:
            headers['X-Hub-Signature-256'] = signature
            print(f"Forwarding to Odoo with signature...")

        response = await client.post(url, content=body, headers=headers)
        
        if is_odoo_request:
            print(f"--- Full Response from Odoo ({url}) ---")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}") 
            print("------------------------------------------")
        else:
            print(f"Forwarded to {url}: Status {response.status_code}")

    except httpx.RequestError as e:
        print(f"Error forwarding to {url}: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()

@app.get("/webhook")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
):
    '''
    Recibe el challenge de Facebook para darle de alta como receptor del webhook.
    '''
    print("GET request received for verification.")
    if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
        print("Verification successful!")
        return Response(content=challenge, media_type="text/plain")
    else:
        print("Verification failed.")
        raise HTTPException(status_code=403, detail="Verification token mismatch")

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256")
):
    """
    Recibe el webhook de whatsapp y lo reenvía sin parsearlo.
    """
    print(f"POST request received. Signature found: {x_hub_signature_256 is not None}")
    
    body_bytes = await request.body()
    
    background_tasks.add_task(forward_webhook, N8N_WEBHOOK_URL, body_bytes, x_hub_signature_256)
    background_tasks.add_task(forward_webhook, ODOO_WEBHOOK_URL, body_bytes, x_hub_signature_256)

    return {"status": "received"}