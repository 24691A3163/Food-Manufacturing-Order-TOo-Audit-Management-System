from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    production_run_id = Column(Integer, ForeignKey("production_runs.id"), nullable=True, index=True)
    expense_type = Column(String(50), nullable=False)  # labour, power_gas, freight, packaging_overhead, other
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(255), nullable=True)
    expense_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    production_run = relationship("ProductionRun", back_populates="expenses")

