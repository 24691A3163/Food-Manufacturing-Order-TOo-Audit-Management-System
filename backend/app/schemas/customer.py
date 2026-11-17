from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    code: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    state: str = "Tamil Nadu"
    state_code: str = "33"
    gstin: Optional[str] = None
    credit_limit: Decimal = Decimal("50000.00")

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    balance_outstanding: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

