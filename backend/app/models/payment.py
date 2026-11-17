from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, index=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    payment_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_mode = Column(String(50), default="bank_transfer", nullable=False)  # cash, bank_transfer, upi, cheque
    reference_number = Column(String(100), nullable=True)  # UTR, Cheque No, Transaction ID
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")

