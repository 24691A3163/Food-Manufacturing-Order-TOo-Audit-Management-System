from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.api.deps import get_db, require_roles
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.user import User
from backend.app.schemas.material import (
    RawMaterialCreate, RawMaterialResponse,
    PackagingMaterialCreate, PackagingMaterialResponse
)
from backend.app.services.inventory_service import InventoryService

router = APIRouter()

@router.get("/raw", response_model=List[RawMaterialResponse])
def get_raw_materials(db: Session = Depends(get_db)):
    return db.query(RawMaterial).filter(RawMaterial.is_active == True).order_by(RawMaterial.name).all()

@router.post("/raw", response_model=RawMaterialResponse)
def create_raw_material(
    rm_in: RawMaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "production", "owner"]))
):
    existing = db.query(RawMaterial).filter(RawMaterial.code == rm_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Raw material code already exists")

    rm_data = rm_in.model_dump()
    opening = rm_data.pop("opening_stock", 0)
    rm = RawMaterial(**rm_data)
    db.add(rm)
    db.flush()

    if opening and opening > 0:
        InventoryService.record_raw_material_movement(
            db, rm.id, "in", opening, "opening_balance", None, None, rm.weighted_average_cost, "Opening Stock"
        )
    db.commit()
    db.refresh(rm)
    return rm

@router.get("/packaging", response_model=List[PackagingMaterialResponse])
def get_packaging_materials(db: Session = Depends(get_db)):
    return db.query(PackagingMaterial).filter(PackagingMaterial.is_active == True).order_by(PackagingMaterial.name).all()

@router.post("/packaging", response_model=PackagingMaterialResponse)
def create_packaging_material(
    pm_in: PackagingMaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "production", "owner"]))
):
    existing = db.query(PackagingMaterial).filter(PackagingMaterial.code == pm_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Packaging material code already exists")

    pm_data = pm_in.model_dump()
    opening = pm_data.pop("opening_stock", 0)
    pm = PackagingMaterial(**pm_data)
    db.add(pm)
    db.flush()

    if opening and opening > 0:
        InventoryService.record_packaging_movement(
            db, pm.id, "in", opening, "opening_balance", None, None, pm.unit_cost, "Opening Stock"
        )
    db.commit()
    db.refresh(pm)
    return pm

