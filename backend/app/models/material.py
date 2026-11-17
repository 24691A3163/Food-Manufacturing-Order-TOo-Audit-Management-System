from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class RawMaterial(Base):
    __tablename__ = "raw_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    unit = Column(String(50), default="kg", nullable=False)  # kg, litre, etc.
    current_stock = Column(Numeric(12, 4), default=0.0000, nullable=False)
    reorder_level = Column(Numeric(12, 4), default=20.0000, nullable=False)
    weighted_average_cost = Column(Numeric(12, 4), default=0.0000, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    bom_items = relationship("BOMItem", back_populates="raw_material")
    stock_movements = relationship("StockMovement", back_populates="raw_material")

class PackagingMaterial(Base):
    __tablename__ = "packaging_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    unit = Column(String(50), default="piece", nullable=False)
    current_stock = Column(Numeric(12, 2), default=0.00, nullable=False)
    reorder_level = Column(Numeric(12, 2), default=100.00, nullable=False)
    unit_cost = Column(Numeric(12, 4), default=0.0000, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    bom_items = relationship("BOMItem", back_populates="packaging_material")
    stock_movements = relationship("StockMovement", back_populates="packaging_material")

