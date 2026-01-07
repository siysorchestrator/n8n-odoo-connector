from models.odoo_client import OdooClient
from config import settings

odoo = OdooClient(
    url=settings.ODOO_URL,
    db=settings.ODOO_DB,
    username=settings.ODOO_USER,
    password=settings.ODOO_PASSWORD
)

def handle_incoming_n8n_message(data):
    partner_domain = [('phone_sanitized', '=', '+' + data.contact_phone)]
    partner_data = odoo.search_read("res.partner", partner_domain, ["id", "name"], limit=1)
    
    contact_partner_id = partner_data[0]['id'] if partner_data else None  # Cambiado el nombre
    partner_name = partner_data[0]['name'] if partner_data else None

    desired_name = f"{partner_name} ({data.contact_phone})" if partner_name else data.contact_phone

    channel_domain = [('whatsapp_number', '=', data.contact_phone)]
    channel_data = odoo.search_read("discuss.channel", channel_domain, ["id", "name"], limit=1)
    
    if channel_data:
        channel_id = channel_data[0]['id']
        if channel_data[0]['name'] != desired_name:
            odoo.write('discuss.channel', [channel_id], {'name': desired_name})
    else:
        members_to_add = settings.DEFAULT_CHANNEL_MEMBERS.copy()
        
        if contact_partner_id and contact_partner_id not in members_to_add:
            members_to_add.append(contact_partner_id)
        
        channel_member_ids = []
        for member_partner_id in members_to_add:
            channel_member_ids.append((0, 0, {
                'partner_id': member_partner_id
            }))
        
        channel_vals = {
            'name': desired_name,
            'whatsapp_number': data.contact_phone,
            'channel_type': 'whatsapp',
            'wa_account_id': settings.WHATSAPP_ACCOUNT_ID,
            'description': 'Created via n8n API',
            'channel_member_ids': channel_member_ids
        }
        channel_id = odoo.create('discuss.channel', channel_vals)

    msg_id = odoo.models.execute_kw(
        odoo.db, odoo.uid, odoo.password,
        'discuss.channel', 'message_post',
        [channel_id],
        {
            'body': data.message_body,
            'subject': "from n8n",
            'message_type': 'whatsapp_message',
            'subtype_id': 1,
            'author_id': int(settings.BOT_PARTNER_ID),
        }
    )
    
    return {
        "channel_id": channel_id,
        "channel_name": desired_name,
        "message_id": msg_id if not isinstance(msg_id, list) else msg_id[0]
    }