from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class BillOfMaterials(Base):
    __tablename__ = "bill_of_materials"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    version = Column(String(50), default="1.0", nullable=False)
    batch_size = Column(Numeric(12, 2), default=200.00, nullable=False)  # e.g., 200 packets
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="boms")
    items = relationship("BOMItem", back_populates="bom", cascade="all, delete-orphan")
    production_runs = relationship("ProductionRun", back_populates="bom")

class BOMItem(Base):
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False, index=True)
    item_type = Column(String(20), nullable=False)  # "raw" or "packaging"
    raw_material_id = Column(Integer, ForeignKey("raw_materials.id"), nullable=True)
    packaging_material_id = Column(Integer, ForeignKey("packaging_materials.id"), nullable=True)
    standard_quantity = Column(Numeric(12, 4), nullable=False)
    unit = Column(String(50), nullable=False)

    # Relationships
    bom = relationship("BillOfMaterials", back_populates="items")
    raw_material = relationship("RawMaterial", back_populates="bom_items")
    packaging_material = relationship("PackagingMaterial", back_populates="bom_items")

