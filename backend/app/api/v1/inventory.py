from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from backend.app.api.deps import get_db
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.product import Product
from backend.app.models.inventory import StockMovement
from backend.app.schemas.inventory import StockDashboardResponse, StockMovementResponse, StockItemSummary

router = APIRouter()

@router.get("/dashboard", response_model=StockDashboardResponse)
def get_stock_dashboard(db: Session = Depends(get_db)):
    rms = db.query(RawMaterial).filter(RawMaterial.is_active == True).all()
    pms = db.query(PackagingMaterial).filter(PackagingMaterial.is_active == True).all()
    products = db.query(Product).filter(Product.is_active == True).all()

    raw_items = []
    total_raw_val = Decimal("0.00")
    for r in rms:
        stock = Decimal(str(r.current_stock))
        wac = Decimal(str(r.weighted_average_cost))
        val = (stock * wac).quantize(Decimal("0.01"))
        total_raw_val += val
        raw_items.append(StockItemSummary(
            id=r.id,
            name=r.name,
            code=r.code,
            category="Raw Material",
            unit=r.unit,
            current_stock=stock,
            reorder_level=Decimal(str(r.reorder_level)),
            unit_valuation=wac,
            total_valuation=val,
            is_low_stock=stock <= Decimal(str(r.reorder_level))
        ))

    pack_items = []
    total_pack_val = Decimal("0.00")
    for p in pms:
        stock = Decimal(str(p.current_stock))
        cost = Decimal(str(p.unit_cost))
        val = (stock * cost).quantize(Decimal("0.01"))
        total_pack_val += val
        pack_items.append(StockItemSummary(
            id=p.id,
            name=p.name,
            code=p.code,
            category="Packaging Material",
            unit=p.unit,
            current_stock=stock,
            reorder_level=Decimal(str(p.reorder_level)),
            unit_valuation=cost,
            total_valuation=val,
            is_low_stock=stock <= Decimal(str(p.reorder_level))
        ))

    fg_items = []
    total_fg_val = Decimal("0.00")
    for pr in products:
        stock = Decimal(str(pr.current_stock))
        price = Decimal(str(pr.selling_price))
        val = (stock * price).quantize(Decimal("0.01"))
        total_fg_val += val
        fg_items.append(StockItemSummary(
            id=pr.id,
            name=pr.name,
            code=pr.sku,
            category=pr.category,
            unit=pr.unit,
            current_stock=stock,
            reorder_level=Decimal(str(pr.reorder_level)),
            unit_valuation=price,
            total_valuation=val,
            is_low_stock=stock <= Decimal(str(pr.reorder_level))
        ))

    return StockDashboardResponse(
        raw_materials=raw_items,
        packaging_materials=pack_items,
        finished_goods=fg_items,
        total_raw_valuation=total_raw_val.quantize(Decimal("0.01")),
        total_packaging_valuation=total_pack_val.quantize(Decimal("0.01")),
        total_fg_valuation=total_fg_val.quantize(Decimal("0.01")),
        total_inventory_valuation=(total_raw_val + total_pack_val + total_fg_val).quantize(Decimal("0.01"))
    )

@router.get("/ledger", response_model=List[StockMovementResponse])
def get_stock_ledger(
    item_type: Optional[str] = Query(None, description="raw, packaging, finished_good"),
    source_document_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(StockMovement).order_by(StockMovement.id.desc())
    if item_type:
        query = query.filter(StockMovement.item_type == item_type)
    if source_document_type:
        query = query.filter(StockMovement.source_document_type == source_document_type)

    movements = query.limit(500).all()
    results = []
    for m in movements:
        name = None
        code = None
        if m.item_type == "raw" and m.raw_material_id:
            rm = db.query(RawMaterial).filter(RawMaterial.id == m.raw_material_id).first()
            name = rm.name if rm else None
            code = rm.code if rm else None
        elif m.item_type == "packaging" and m.packaging_material_id:
            pm = db.query(PackagingMaterial).filter(PackagingMaterial.id == m.packaging_material_id).first()
            name = pm.name if pm else None
            code = pm.code if pm else None
        elif m.item_type == "finished_good" and m.product_id:
            p = db.query(Product).filter(Product.id == m.product_id).first()
            name = p.name if p else None
            code = p.sku if p else None

        results.append(StockMovementResponse(
            id=m.id,
            timestamp=m.timestamp,
            item_type=m.item_type,
            item_name=name,
            item_code=code,
            movement_type=m.movement_type,
            quantity=m.quantity,
            source_document_type=m.source_document_type,
            source_document_id=m.source_document_id,
            batch_number=m.batch_number,
            unit_cost=m.unit_cost,
            running_balance=m.running_balance,
            notes=m.notes,
            created_by=m.created_by
        ))
    return results

