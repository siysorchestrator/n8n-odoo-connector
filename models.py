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

# --- Repair Order ---
class RepairCreate(BaseModel):
    partner_id: int
    product_id: int
    product_qty: float
    product_uom: int
    internal_notes: Optional[str]

class RepairUpdate(BaseModel):
    partner_id: int
    product_id: int
    product_qty: float
    product_uom: int
    internal_notes: Optional[str]

# --- Sales Quote ---
class SaleCreate(BaseModel):
    partner_id: int
    order_line: List[dict]  # [{'product_id': int, 'product_uom_qty': float, 'price_unit': float}]

class SaleUpdate(BaseModel):
    order_line: Optional[List[dict]]

# --- Equipos Medicos ---
class EquipoCreate(BaseModel):
    name: str
    x_studio_numero_de_serie: Optional[str] = None
    x_studio_marca: Optional[str] = None
    x_studio_modelo: Optional[str] = None
    x_studio_poseedor: Optional[str]

class EquipoUpdate(BaseModel):
    name: str
    x_studio_numero_de_serie: Optional[str] = None
    x_studio_marca: Optional[str] = None
    x_studio_modelo: Optional[str] = None
    x_studio_poseedor: Optional[str]