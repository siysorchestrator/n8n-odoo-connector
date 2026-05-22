#Modelos pydantic que se utilizamos para crear y actualizar datos en Odoo desde N8N
#Se usa pydantic para manejar datos tipados y facil traduccion del json al objeto.

from pydantic import BaseModel
from typing import Optional, List

# --- Partner ---
class PartnerCreate(BaseModel):
    name: str
    phone: Optional[str]
    email: Optional[str]
    street: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    state_id: Optional[int]
    country_id: Optional[int]

class PartnerUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    street: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    state_id: Optional[int]
    country_id: Optional[int]

# --- Ticket de soporte ---
class TicketCreate(BaseModel):
    name: str
    partner_id: Optional[int]
    priority: Optional[int]
    partner_phone: Optional[str]
    description: Optional[str]

# --- Sales Quote ---
class SaleCreate(BaseModel):
    partner_id: int
    order_line: Optional[List[dict]] = []  # [{'product_id': int, 'product_uom_qty': float, 'price_unit': float}]

class SaleUpdate(BaseModel):
    order_line: Optional[List[dict]]

# --- Repair Order ---
class RepairCreate(BaseModel):
    internal_notes: Optional[str]
    x_studio_servicio_solicitado: Optional[str]
    x_studio_tipo_de_servicio: Optional[str]

class RepairUpdate(BaseModel):
    internal_notes: Optional[str]
    x_studio_servicio_solicitado: Optional[str]
    x_studio_tipo_de_servicio: Optional[str]

# --- Equipos Medicos ---
class EquipoCreate(BaseModel):
    x_name: str
    x_studio_numero_de_serie: Optional[str] = "Desconocido"
    x_studio_clasificacin: Optional[str] = ""
    x_studio_marca_equipo: Optional[int] = 1
    x_studio_modelo_equipo: Optional[int] = 1
    x_studio_poseedor: Optional[int] = 0
    x_studio_propietario: Optional[int] = 0

class EquipoUpdate(BaseModel):
    x_name: Optional[str]
    x_studio_numero_de_serie: Optional[str] = "Desconocido"
    x_studio_clasificacin: Optional[str] = ""
    x_studio_marca_equipo: Optional[int] = 1
    x_studio_modelo_equipo: Optional[int] = 1
    x_studio_poseedor: Optional[int] = 0
    x_studio_propietario: Optional[int] = 0

# --- Mensajes ---
class OdooMessageCreate(BaseModel):
    contact_phone: str
    message_body: str   
    message_id: Optional[str] = None 

# --- Canales de chat ---
class ChatChannelNameUpdate(BaseModel):
    name: str

# --- Ticket de licitación ---
class LicitacionCreate(BaseModel):
    x_tipo_servicio: Optional[str]
    x_studio_stage_id: Optional[int] = 1
    x_studio_equipo: Optional[int] = 4
    x_studio_activo: Optional[int]

class LicitacionUpdate(BaseModel):
    x_tipo_servicio: Optional[str]
    x_studio_stage_id: Optional[int] = 1
    x_studio_equipo: Optional[int] = 4