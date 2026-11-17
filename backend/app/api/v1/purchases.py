from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from decimal import Decimal

from backend.app.api.deps import get_db, require_roles
from backend.app.models.purchase import Purchase, PurchaseItem
from backend.app.models.supplier import Supplier
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.user import User
from backend.app.schemas.purchase import (
    SupplierCreate, SupplierResponse,
    PurchaseCreate, PurchaseResponse
)
from backend.app.services.inventory_service import InventoryService

router = APIRouter()

@router.get("/suppliers", response_model=List[SupplierResponse])
def get_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).filter(Supplier.is_active == True).all()

@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(
    sup_in: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "owner"]))
):
    existing = db.query(Supplier).filter(Supplier.code == sup_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Supplier code already exists")
    supplier = Supplier(**sup_in.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier

@router.get("", response_model=List[PurchaseResponse])
def get_purchases(db: Session = Depends(get_db)):
    purchases = db.query(Purchase).order_by(Purchase.id.desc()).all()
    results = []
    for p in purchases:
        items = []
        for itm in p.items:
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
                "quantity": itm.quantity,
                "unit_price": itm.unit_price,
                "total_cost": itm.total_cost,
                "unit": itm.unit
            })
        results.append({
            "id": p.id,
            "purchase_number": p.purchase_number,
            "supplier_id": p.supplier_id,
            "supplier_name": p.supplier.name if p.supplier else None,
            "supplier_invoice_no": p.supplier_invoice_no,
            "purchase_date": p.purchase_date,
            "status": p.status,
            "total_amount": p.total_amount,
            "notes": p.notes,
            "items": items,
            "created_at": p.created_at
        })
    return results

@router.post("", response_model=PurchaseResponse)
def create_purchase(
    purchase_in: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "owner"]))
):
    supplier = db.query(Supplier).filter(Supplier.id == purchase_in.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    year = datetime.now(timezone.utc).year
    prefix = f"PUR-{year}-"
    last_po = db.query(Purchase).filter(Purchase.purchase_number.like(f"{prefix}%")).order_by(Purchase.id.desc()).first()
    next_seq = 1
    if last_po:
        try:
            next_seq = int(last_po.purchase_number.split("-")[-1]) + 1
        except Exception:
            next_seq = 1
    purchase_number = f"{prefix}{next_seq:04d}"

    total_amount = Decimal("0.00")
    po = Purchase(
        purchase_number=purchase_number,
        supplier_id=supplier.id,
        supplier_invoice_no=purchase_in.supplier_invoice_no,
        status="received",
        total_amount=Decimal("0.00"),
        notes=purchase_in.notes
    )
    db.add(po)
    db.flush()

    for itm in purchase_in.items:
        qty = Decimal(str(itm.quantity))
        price = Decimal(str(itm.unit_price))
        subtotal = (qty * price).quantize(Decimal("0.01"))
        total_amount += subtotal

        po_item = PurchaseItem(
            purchase_id=po.id,
            item_type=itm.item_type,
            raw_material_id=itm.raw_material_id,
            packaging_material_id=itm.packaging_material_id,
            quantity=qty,
            unit_price=price,
            total_cost=subtotal,
            unit=itm.unit
        )
        db.add(po_item)

        if itm.item_type == "raw" and itm.raw_material_id:
            InventoryService.record_raw_material_movement(
                db, itm.raw_material_id, "in", qty, "purchase", po.purchase_number, None, price, f"Purchase from {supplier.name}"
            )
        elif itm.item_type == "packaging" and itm.packaging_material_id:
            InventoryService.record_packaging_movement(
                db, itm.packaging_material_id, "in", qty, "purchase", po.purchase_number, None, price, f"Purchase from {supplier.name}"
            )

    po.total_amount = total_amount
    db.commit()
    db.refresh(po)
    return get_purchases(db)[0]

