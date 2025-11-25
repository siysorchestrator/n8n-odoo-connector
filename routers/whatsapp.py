from fastapi import APIRouter, Query, Response, HTTPException, Request, Header, BackgroundTasks
from config import settings
from services.webhook_service import forward_webhook_payload

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
):
    if mode == 'subscribe' and token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification token mismatch")

@router.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256")
):
    body_bytes = await request.body()
    
    # Fire and forget tasks to N8N and Odoo
    background_tasks.add_task(forward_webhook_payload, settings.N8N_WEBHOOK_URL, body_bytes, x_hub_signature_256)
    background_tasks.add_task(forward_webhook_payload, settings.ODOO_WEBHOOK_URL, body_bytes, x_hub_signature_256)

    return {"status": "received"}