from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class RawMaterialBase(BaseModel):
    name: str
    code: str
    unit: str = "kg"
    reorder_level: Decimal = Decimal("20.00")
    weighted_average_cost: Decimal = Decimal("0.00")

class RawMaterialCreate(RawMaterialBase):
    opening_stock: Optional[Decimal] = Decimal("0.00")

class RawMaterialResponse(RawMaterialBase):
    id: int
    current_stock: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PackagingMaterialBase(BaseModel):
    name: str
    code: str
    unit: str = "piece"
    reorder_level: Decimal = Decimal("100.00")
    unit_cost: Decimal = Decimal("0.00")

class PackagingMaterialCreate(PackagingMaterialBase):
    opening_stock: Optional[Decimal] = Decimal("0.00")

class PackagingMaterialResponse(PackagingMaterialBase):
    id: int
    current_stock: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

