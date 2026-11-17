from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: Decimal
    unit_price: Optional[Decimal] = None

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]
    notes: Optional[str] = None

class OrderApproveReject(BaseModel):
    action: str  # "approve" or "reject"
    rejection_reason: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    customer_name: Optional[str] = None
    salesman_id: int
    salesman_name: Optional[str] = None
    order_date: datetime
    status: str
    total_amount: Decimal
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    items: List[OrderItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

