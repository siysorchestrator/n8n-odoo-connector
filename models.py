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
    state_id: Optional[str]
    country_id: Optional[str]

class PartnerUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    street: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    state_id: Optional[str]
    country_id: Optional[str]

# --- Pre-Orden ---
class PreOrderCreate(BaseModel):
    x_studio_cliente: int
    x_studio_marca_equipo: Optional[str]
    x_studio_modelo_equipo: Optional[str]
    x_studio_serie_equipo: Optional[str]
    x_studio_descripcion_de_servicio: Optional[str]
    x_studio_tipo_de_servicio: Optional[str]

class PreOrderUpdate(BaseModel):
    x_studio_cliente: int   
    x_studio_marca_equipo: Optional[str]
    x_studio_modelo_equipo: Optional[str]
    x_studio_serie_equipo: Optional[str]
    x_studio_descripcion_de_servicio: Optional[str]
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