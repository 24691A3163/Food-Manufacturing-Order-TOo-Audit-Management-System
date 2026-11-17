from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class MaterialIssueInput(BaseModel):
    material_type: str  # "raw" or "packaging"
    raw_material_id: Optional[int] = None
    packaging_material_id: Optional[int] = None
    actual_qty: Decimal

class ProductionRunCreate(BaseModel):
    bom_id: int
    product_id: int
    planned_quantity: Decimal = Decimal("200.00")
    material_issues: List[MaterialIssueInput]
    actual_good_quantity: Decimal
    damaged_quantity: Decimal = Decimal("0.00")
    cartons_used: Decimal = Decimal("0.00")
    labour_expense: Decimal = Decimal("0.00")
    power_gas_expense: Decimal = Decimal("0.00")
    notes: Optional[str] = None

class ProductionMaterialIssueResponse(BaseModel):
    id: int
    material_type: str
    material_name: Optional[str] = None
    standard_qty: Decimal
    actual_qty: Decimal
    unit: str
    unit_cost: Decimal
    total_cost: Decimal
    variance_percent: Decimal

    class Config:
        from_attributes = True

class ProductionRunResponse(BaseModel):
    id: int
    batch_number: str
    product_id: int
    product_name: Optional[str] = None
    planned_quantity: Decimal
    actual_good_quantity: Decimal
    damaged_quantity: Decimal
    cartons_used: Decimal
    yield_variance_percent: Decimal
    oil_variance_percent: Decimal
    is_variance_alert: int
    status: str
    supervisor_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    material_issues: List[ProductionMaterialIssueResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

