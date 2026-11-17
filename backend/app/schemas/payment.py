from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class PaymentCreate(BaseModel):
    invoice_id: Optional[int] = None
    customer_id: int
    amount: Decimal
    payment_mode: str = "bank_transfer"  # cash, bank_transfer, upi, cheque
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    payment_number: str
    invoice_id: Optional[int] = None
    invoice_number: Optional[str] = None
    customer_id: int
    customer_name: Optional[str] = None
    payment_date: datetime
    amount: Decimal
    payment_mode: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

