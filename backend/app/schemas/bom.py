from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class BOMItemCreate(BaseModel):
    item_type: str  # "raw" or "packaging"
    raw_material_id: Optional[int] = None
    packaging_material_id: Optional[int] = None
    standard_quantity: Decimal
    unit: str

class BOMItemResponse(BaseModel):
    id: int
    item_type: str
    item_name: Optional[str] = None
    raw_material_id: Optional[int] = None
    packaging_material_id: Optional[int] = None
    standard_quantity: Decimal
    unit: str

    class Config:
        from_attributes = True

class BOMCreate(BaseModel):
    product_id: int
    version: str = "1.0"
    batch_size: Decimal = Decimal("200.00")
    notes: Optional[str] = None
    items: List[BOMItemCreate]

class BOMResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    version: str
    batch_size: Decimal
    is_active: bool
    notes: Optional[str] = None
    items: List[BOMItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

