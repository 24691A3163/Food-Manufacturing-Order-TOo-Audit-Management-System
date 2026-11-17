from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.api.deps import get_db, require_roles
from backend.app.models.product import Product
from backend.app.models.user import User
from backend.app.schemas.product import ProductCreate, ProductResponse

router = APIRouter()

@router.get("", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active == True).order_by(Product.name).all()

@router.post("", response_model=ProductResponse)
def create_product(
    prod_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "owner"]))
):
    existing = db.query(Product).filter(Product.sku == prod_in.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product SKU already exists")

    product = Product(**prod_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

