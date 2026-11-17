from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class StockMovementResponse(BaseModel):
    id: int
    timestamp: datetime
    item_type: str
    item_name: Optional[str] = None
    item_code: Optional[str] = None
    movement_type: str
    quantity: Decimal
    source_document_type: str
    source_document_id: Optional[str] = None
    batch_number: Optional[str] = None
    unit_cost: Decimal
    running_balance: Decimal
    notes: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True

class StockItemSummary(BaseModel):
    id: int
    name: str
    code: str
    category: Optional[str] = None
    unit: str
    current_stock: Decimal
    reorder_level: Decimal
    unit_valuation: Decimal
    total_valuation: Decimal
    is_low_stock: bool

class StockDashboardResponse(BaseModel):
    raw_materials: list[StockItemSummary]
    packaging_materials: list[StockItemSummary]
    finished_goods: list[StockItemSummary]
    total_raw_valuation: Decimal
    total_packaging_valuation: Decimal
    total_fg_valuation: Decimal
    total_inventory_valuation: Decimal

