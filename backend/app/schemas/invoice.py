from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class InvoiceItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    hsn_code: str
    quantity: Decimal
    unit_price: Decimal
    taxable_value: Decimal
    cgst_rate: Decimal
    cgst_amount: Decimal
    sgst_rate: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal
    total_item_amount: Decimal

    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    order_id: Optional[int] = None
    customer_id: int
    customer_name: Optional[str] = None
    invoice_date: datetime
    due_date: Optional[datetime] = None
    place_of_supply: str
    is_interstate: bool
    taxable_amount: Decimal
    cgst_rate: Decimal
    cgst_amount: Decimal
    sgst_rate: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    status: str
    dispatch_status: str
    dispatched_at: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[InvoiceItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

