import xmlrpc.client

url = "https://janssenlearing.odoo.com/"
db = "janssenlearing"
username = 'atsuro095@gmail.com'
password = 'Suprise1835!'
key = '8df6f9649dc0e69fe88517c7c7bb89daf8baeb22'

# --- 1. Authenticate user ---
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
print("UID:", uid)

if not uid:
    raise Exception("Authentication failed")

# --- 2. Create model proxy (for object operations) ---
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# --- 3. Example: Search for partners (clients) ---
partners = models.execute_kw(
    db, uid, password,
    "res.partner", "search_read",
    [[["is_company", "=", False]]],    # Domain filter
    {"fields": ["name", "email"], "limit": 5}
)
print("Partners:", partners)

# --- 4. Example: Create a new client ---
new_partner_id = models.execute_kw(
    db, uid, password,
    "res.partner", "create",
    [{
        "name": "New Client from Python",
        "email": "client@example.com",
        "phone": "+521234567890",
    }]
)
print("Created Partner ID:", new_partner_id)

# --- 5. Example: Update a record ---
models.execute_kw(
    db, uid, password,
    "res.partner", "write",
    [[new_partner_id], {"phone": "+529876543210"}]
)
print("Updated Partner phone!")

# --- 6. Example: Create a repair order (if you have repair module) ---
new_repair_id = models.execute_kw(
    db, uid, password,
    "repair.order", "create",
    [{
        "name": "REP-TEST-001",                # custom reference
        "partner_id": new_partner_id,          # link to your client
        "product_id": 1,                       # replace with a valid product_id
        "product_qty": 1,
        "product_uom": 1,                      # replace with a valid UoM ID
        "internal_notes": "Repair created via XML-RPC",
        "company_id": 1,                       # if needed
        "state": "draft"                       # usually default, but can be set
    }]
)
print("Created Repair Order ID:", new_repair_id)