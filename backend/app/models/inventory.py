from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    item_type = Column(String(50), nullable=False, index=True)  # "raw", "packaging", "finished_good"
    raw_material_id = Column(Integer, ForeignKey("raw_materials.id"), nullable=True, index=True)
    packaging_material_id = Column(Integer, ForeignKey("packaging_materials.id"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    
    movement_type = Column(String(10), nullable=False)  # "in" or "out"
    quantity = Column(Numeric(12, 4), nullable=False)
    source_document_type = Column(String(50), nullable=False, index=True)  # opening_balance, purchase, production_issue, production_receipt, dispatch, adjustment, credit_note
    source_document_id = Column(String(100), nullable=True)  # ID or Number of source doc (e.g. "PUR-001", "BATCH-001", "INV-001")
    batch_number = Column(String(50), nullable=True)
    unit_cost = Column(Numeric(12, 4), default=0.0000, nullable=False)
    running_balance = Column(Numeric(12, 4), nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)

    # Relationships
    raw_material = relationship("RawMaterial", back_populates="stock_movements")
    packaging_material = relationship("PackagingMaterial", back_populates="stock_movements")
    product = relationship("Product", back_populates="stock_movements")

