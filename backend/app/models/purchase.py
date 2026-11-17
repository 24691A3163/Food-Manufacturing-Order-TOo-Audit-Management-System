from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    purchase_number = Column(String(50), unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    supplier_invoice_no = Column(String(100), nullable=True)
    purchase_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(String(50), default="received", nullable=False)  # draft, ordered, received, cancelled
    total_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")

class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False, index=True)
    item_type = Column(String(20), nullable=False)  # "raw" or "packaging"
    raw_material_id = Column(Integer, ForeignKey("raw_materials.id"), nullable=True)
    packaging_material_id = Column(Integer, ForeignKey("packaging_materials.id"), nullable=True)
    quantity = Column(Numeric(12, 4), nullable=False)
    unit_price = Column(Numeric(12, 4), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)
    unit = Column(String(50), nullable=False)

    # Relationships
    purchase = relationship("Purchase", back_populates="items")

