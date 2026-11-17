from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    contact_person = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    billing_address = Column(String(500), nullable=True)
    shipping_address = Column(String(500), nullable=True)
    state = Column(String(100), nullable=False, default="Tamil Nadu")
    state_code = Column(String(10), nullable=False, default="33")
    gstin = Column(String(15), nullable=True)
    credit_limit = Column(Numeric(12, 2), default=0.00, nullable=False)
    balance_outstanding = Column(Numeric(12, 2), default=0.00, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")

