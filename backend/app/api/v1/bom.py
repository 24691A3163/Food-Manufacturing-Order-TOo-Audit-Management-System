from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from backend.app.api.deps import get_db, require_roles
from backend.app.models.bom import BillOfMaterials, BOMItem
from backend.app.models.product import Product
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.user import User
from backend.app.schemas.bom import BOMCreate, BOMResponse

router = APIRouter()

@router.get("", response_model=List[BOMResponse])
def get_boms(db: Session = Depends(get_db)):
    boms = db.query(BillOfMaterials).filter(BillOfMaterials.is_active == True).all()
    results = []
    for b in boms:
        items = []
        for itm in b.items:
            name = None
            if itm.item_type == "raw" and itm.raw_material_id:
                rm = db.query(RawMaterial).filter(RawMaterial.id == itm.raw_material_id).first()
                name = rm.name if rm else None
            elif itm.item_type == "packaging" and itm.packaging_material_id:
                pm = db.query(PackagingMaterial).filter(PackagingMaterial.id == itm.packaging_material_id).first()
                name = pm.name if pm else None
            items.append({
                "id": itm.id,
                "item_type": itm.item_type,
                "item_name": name,
                "raw_material_id": itm.raw_material_id,
                "packaging_material_id": itm.packaging_material_id,
                "standard_quantity": itm.standard_quantity,
                "unit": itm.unit
            })
        results.append({
            "id": b.id,
            "product_id": b.product_id,
            "product_name": b.product.name if b.product else None,
            "version": b.version,
            "batch_size": b.batch_size,
            "is_active": b.is_active,
            "notes": b.notes,
            "items": items,
            "created_at": b.created_at
        })
    return results

@router.post("", response_model=BOMResponse)
def create_bom(
    bom_in: BOMCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["production", "admin", "owner"]))
):
    product = db.query(Product).filter(Product.id == bom_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    bom = BillOfMaterials(
        product_id=bom_in.product_id,
        version=bom_in.version,
        batch_size=bom_in.batch_size,
        notes=bom_in.notes
    )
    db.add(bom)
    db.flush()

    for itm in bom_in.items:
        bom_item = BOMItem(
            bom_id=bom.id,
            item_type=itm.item_type,
            raw_material_id=itm.raw_material_id,
            packaging_material_id=itm.packaging_material_id,
            standard_quantity=itm.standard_quantity,
            unit=itm.unit
        )
        db.add(bom_item)

    db.commit()
    db.refresh(bom)
    return get_boms(db)[-1]

