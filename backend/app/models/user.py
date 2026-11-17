import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    SALESMAN = "salesman"
    PRODUCTION = "production"
    AUDITOR = "auditor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, native_enum=False), default=UserRole.SALESMAN, nullable=False)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="salesman")
    production_runs = relationship("ProductionRun", back_populates="supervisor")

