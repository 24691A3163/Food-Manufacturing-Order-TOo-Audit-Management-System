from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ProductionRun(Base):
    __tablename__ = "production_runs"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(50), unique=True, index=True, nullable=False)
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    planned_quantity = Column(Numeric(12, 2), default=200.00, nullable=False)
    actual_good_quantity = Column(Numeric(12, 2), default=0.00, nullable=False)
    damaged_quantity = Column(Numeric(12, 2), default=0.00, nullable=False)  # Damaged pouches/packets
    cartons_used = Column(Numeric(12, 2), default=0.00, nullable=False)
    yield_variance_percent = Column(Numeric(6, 2), default=0.00, nullable=False)  # e.g., -6.00%
    oil_variance_percent = Column(Numeric(6, 2), default=0.00, nullable=False)    # e.g., +5.00%
    is_variance_alert = Column(Integer, default=0, nullable=False)  # 1 if abs(variance) > 3%
    status = Column(String(50), default="in_progress", nullable=False)  # planned, in_progress, completed, cancelled
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_time = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    bom = relationship("BillOfMaterials", back_populates="production_runs")
    product = relationship("Product", back_populates="production_runs")
    supervisor = relationship("User", back_populates="production_runs")
    material_issues = relationship("ProductionMaterialIssue", back_populates="production_run", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="production_run", cascade="all, delete-orphan")

class ProductionMaterialIssue(Base):
    __tablename__ = "production_material_issues"

    id = Column(Integer, primary_key=True, index=True)
    production_run_id = Column(Integer, ForeignKey("production_runs.id"), nullable=False, index=True)
    material_type = Column(String(20), nullable=False)  # "raw" or "packaging"
    raw_material_id = Column(Integer, ForeignKey("raw_materials.id"), nullable=True)
    packaging_material_id = Column(Integer, ForeignKey("packaging_materials.id"), nullable=True)
    standard_qty = Column(Numeric(12, 4), nullable=False)
    actual_qty = Column(Numeric(12, 4), nullable=False)
    unit = Column(String(50), nullable=False)
    unit_cost = Column(Numeric(12, 4), default=0.0000, nullable=False)
    total_cost = Column(Numeric(12, 2), default=0.00, nullable=False)
    variance_percent = Column(Numeric(6, 2), default=0.00, nullable=False)

    # Relationships
    production_run = relationship("ProductionRun", back_populates="material_issues")

