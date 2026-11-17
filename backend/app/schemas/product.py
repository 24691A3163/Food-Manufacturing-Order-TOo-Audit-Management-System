from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    sku: str
    category: str = "Savouries"
    unit: str = "packet"
    weight_grams: Decimal = Decimal("200.00")
    hsn_code: str = "21069099"
    selling_price: Decimal = Decimal("50.00")
    gst_rate: Decimal = Decimal("5.00")
    reorder_level: Decimal = Decimal("50.00")

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    current_stock: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

