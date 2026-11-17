from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from backend.app.api.deps import get_db, require_roles
from backend.app.models.customer import Customer
from backend.app.models.user import User
from backend.app.schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter()

@router.get("", response_model=List[CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).filter(Customer.is_active == True).order_by(Customer.name).all()

@router.post("", response_model=CustomerResponse)
def create_customer(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "owner"]))
):
    existing = db.query(Customer).filter(Customer.code == customer_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer code already exists")
    
    customer = Customer(**customer_in.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

