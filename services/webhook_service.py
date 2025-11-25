import httpx
from config import settings

client = httpx.AsyncClient(timeout=10.0)

async def forward_webhook_payload(target_url: str, body: bytes, signature: str | None):
    if not target_url:
        return

    try:
        headers = {'Content-Type': 'application/json'}
        
        # Add signature only if sending to Odoo
        is_odoo = settings.ODOO_WEBHOOK_URL and settings.ODOO_WEBHOOK_URL in target_url
        if is_odoo and signature:
            headers['X-Hub-Signature-256'] = signature

        response = await client.post(target_url, content=body, headers=headers)
        
        # Logging
        if is_odoo:
            print(f"--- Odoo Webhook Response ({response.status_code}) ---")
            print(response.text)
        else:
            print(f"Forwarded to {target_url}: {response.status_code}")

    except httpx.RequestError as e:
        print(f"Error forwarding to {target_url}: {e}")

async def close_client():
    await client.aclose()