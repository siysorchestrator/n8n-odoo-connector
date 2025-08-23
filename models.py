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
    country_id: 156


class PartnerUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]

# --- Repair Order ---
class RepairCreate(BaseModel):
    partner_id: int
    product_id: int
    product_qty: float
    product_uom: int
    internal_notes: Optional[str]

class RepairUpdate(BaseModel):
    product_qty: Optional[float]
    internal_notes: Optional[str]

# --- Sales Quote ---
class SaleCreate(BaseModel):
    partner_id: int
    order_line: List[dict]  # [{'product_id': int, 'product_uom_qty': float, 'price_unit': float}]

class SaleUpdate(BaseModel):
    order_line: Optional[List[dict]]

# --- Product / Inventory ---
class ProductCreate(BaseModel):
    name: str
    list_price: float
    qty_available: Optional[float] = 0

class ProductUpdate(BaseModel):
    name: Optional[str]
    list_price: Optional[float]
    qty_available: Optional[float]

# --- Product / Inventory ---
class ProductCreate(BaseModel):
    name: str
    list_price: float
    qty_available: Optional[float] = 0

class ProductUpdate(BaseModel):
    name: Optional[str]
    list_price: Optional[float]
    qty_available: Optional[float]