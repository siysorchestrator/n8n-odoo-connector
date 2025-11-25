from fastapi import FastAPI
from routers import odoo_crud, whatsapp
from services.webhook_service import close_client

app = FastAPI(title="Odoo Proxy API")

# Register Routers
app.include_router(odoo_crud.router, tags=["Odoo CRM"])
app.include_router(whatsapp.router, tags=["WhatsApp Webhooks"])

@app.get("/")
def read_root():
    return {"status": "Service Running"}

@app.on_event("shutdown")
async def shutdown_event():
    await close_client()