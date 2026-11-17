from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    invoice_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    due_date = Column(DateTime, nullable=True)
    place_of_supply = Column(String(100), default="Tamil Nadu", nullable=False)
    is_interstate = Column(Boolean, default=False, nullable=False)
    
    # Financials
    taxable_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    cgst_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    cgst_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    sgst_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    sgst_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    igst_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    igst_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    total_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    amount_paid = Column(Numeric(12, 2), default=0.00, nullable=False)
    balance_due = Column(Numeric(12, 2), default=0.00, nullable=False)
    
    status = Column(String(50), default="unpaid", nullable=False)  # unpaid, partially_paid, paid, cancelled
    dispatch_status = Column(String(50), default="pending", nullable=False)  # pending, dispatched
    dispatched_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="invoice")
    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    hsn_code = Column(String(20), default="21069099", nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    taxable_value = Column(Numeric(12, 2), nullable=False)
    cgst_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    cgst_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    sgst_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    sgst_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    igst_rate = Column(Numeric(5, 2), default=0.00, nullable=False)
    igst_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    total_item_amount = Column(Numeric(12, 2), nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")

