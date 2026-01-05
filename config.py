import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Security
    API_SECRET_KEY = os.getenv("PROXY_API_SECRET_KEY")

    # Odoo Connection
    ODOO_URL = os.getenv("XMLRPC_SERVER_URL")
    ODOO_DB = os.getenv("XMLRPC_DB_NAME")
    ODOO_USER = os.getenv("XMLRPC_USERNAME")
    ODOO_PASSWORD = os.getenv("XMLRPC_PASSWORD")

    # Webhooks
    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
    ODOO_WEBHOOK_URL = os.getenv("ODOO_WEBHOOK_URL")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

    # Constants / IDs
    BOT_PARTNER_ID = os.getenv("BOT_PARTNER_ID")
    WHATSAPP_ACCOUNT_ID = os.getenv("ODOO_WHATSAPP_ID")

settings = Settings()