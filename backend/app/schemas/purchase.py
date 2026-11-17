from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class SupplierBase(BaseModel):
    name: str
    code: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    state: str = "Tamil Nadu"
    gstin: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PurchaseItemCreate(BaseModel):
    item_type: str  # "raw" or "packaging"
    raw_material_id: Optional[int] = None
    packaging_material_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    unit: str

class PurchaseCreate(BaseModel):
    supplier_id: int
    supplier_invoice_no: Optional[str] = None
    items: List[PurchaseItemCreate]
    notes: Optional[str] = None

class PurchaseItemResponse(BaseModel):
    id: int
    item_type: str
    item_name: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    total_cost: Decimal
    unit: str

    class Config:
        from_attributes = True

class PurchaseResponse(BaseModel):
    id: int
    purchase_number: str
    supplier_id: int
    supplier_name: Optional[str] = None
    supplier_invoice_no: Optional[str] = None
    purchase_date: datetime
    status: str
    total_amount: Decimal
    notes: Optional[str] = None
    items: List[PurchaseItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

