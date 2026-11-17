from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    category = Column(String(100), default="Savouries", nullable=False)  # Murukku, Mixture, Chips, Sweets
    unit = Column(String(50), default="packet", nullable=False)
    weight_grams = Column(Numeric(8, 2), default=200.00, nullable=False)
    hsn_code = Column(String(20), default="21069099", nullable=False)
    selling_price = Column(Numeric(12, 2), default=50.00, nullable=False)  # Pre-tax selling price
    gst_rate = Column(Numeric(5, 2), default=5.00, nullable=False)  # 5%
    current_stock = Column(Numeric(12, 2), default=0.00, nullable=False)
    reorder_level = Column(Numeric(12, 2), default=50.00, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    boms = relationship("BillOfMaterials", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    invoice_items = relationship("InvoiceItem", back_populates="product")
    production_runs = relationship("ProductionRun", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")

