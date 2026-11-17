from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from backend.app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # LOGIN, ORDER_CREATE, ORDER_APPROVE, INVOICE_GENERATE, DISPATCH, BATCH_RECORD, PAYMENT_LOG, CANCELLATION
    entity_name = Column(String(100), nullable=False, index=True)  # Order, Invoice, ProductionRun, Payment, StockMovement
    entity_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)  # JSON or descriptive text of old/new values
    ip_address = Column(String(50), nullable=True)

