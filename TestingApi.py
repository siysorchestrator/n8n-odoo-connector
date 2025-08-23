import xmlrpc.client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("XMLRPC_SERVER_URL"),
db = os.getenv("XMLRPC_DB_NAME"),
username = os.getenv("XMLRPC_USERNAME"),
password = os.getenv("XMLRPC_PASSWORD")

# --- 1. Authenticate user ---
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
print("UID:", uid)

if not uid:
    raise Exception("Authentication failed")

# --- 2. Create model proxy (for object operations) ---
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# fields = models.execute_kw(
#     db, uid, password,
#     'res.country', 'fields_get',
#     [], {'attributes': ['string', 'help', 'type']}
# )

# with open("res_country_fields.txt", "w", encoding="utf-8") as f:
#     for field, info in fields.items():
#         f.write(f"Field: {field}\n")
#         f.write(f"  Label: {info.get('string')}\n")
#         f.write(f"  Type: {info.get('type')}\n")
#         f.write(f"  Help: {info.get('help')}\n")
#         f.write("----\n")


# Fetch states only for Mexico (country_id = 156)
states = models.execute_kw(
    db, uid, password,
    'res.country.state', 'search_read',
    [[['country_id', '=', 156]]],  # domain filter
    {'fields': ['id', 'name']}  # only fetch id and name
)

# Create dictionary: state_id -> state_name
mexico_states = {state['id']: state['name'] for state in states}

# Print mapping
for state_id, state_name in mexico_states.items():
    print(f"{state_id}: {state_name}")