from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal

from backend.app.api.deps import get_db, get_current_user, require_roles
from backend.app.models.production import ProductionRun, ProductionMaterialIssue
from backend.app.models.bom import BillOfMaterials
from backend.app.models.product import Product
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.expense import Expense
from backend.app.models.user import User
from backend.app.schemas.production import ProductionRunCreate, ProductionRunResponse
from backend.app.services.inventory_service import InventoryService
from backend.app.core.config import settings

router = APIRouter()

@router.get("", response_model=List[ProductionRunResponse])
def get_production_runs(db: Session = Depends(get_db)):
    runs = db.query(ProductionRun).order_by(ProductionRun.id.desc()).all()
    results = []
    for r in runs:
        issues = []
        for issue in r.material_issues:
            name = None
            if issue.material_type == "raw" and issue.raw_material_id:
                rm = db.query(RawMaterial).filter(RawMaterial.id == issue.raw_material_id).first()
                name = rm.name if rm else None
            elif issue.material_type == "packaging" and issue.packaging_material_id:
                pm = db.query(PackagingMaterial).filter(PackagingMaterial.id == issue.packaging_material_id).first()
                name = pm.name if pm else None
            issues.append({
                "id": issue.id,
                "material_type": issue.material_type,
                "material_name": name,
                "standard_qty": issue.standard_qty,
                "actual_qty": issue.actual_qty,
                "unit": issue.unit,
                "unit_cost": issue.unit_cost,
                "total_cost": issue.total_cost,
                "variance_percent": issue.variance_percent
            })
        results.append({
            "id": r.id,
            "batch_number": r.batch_number,
            "product_id": r.product_id,
            "product_name": r.product.name if r.product else None,
            "planned_quantity": r.planned_quantity,
            "actual_good_quantity": r.actual_good_quantity,
            "damaged_quantity": r.damaged_quantity,
            "cartons_used": r.cartons_used,
            "yield_variance_percent": r.yield_variance_percent,
            "oil_variance_percent": r.oil_variance_percent,
            "is_variance_alert": r.is_variance_alert,
            "status": r.status,
            "supervisor_name": r.supervisor.full_name if r.supervisor else None,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "notes": r.notes,
            "material_issues": issues,
            "created_at": r.created_at
        })
    return results

@router.post("", response_model=ProductionRunResponse)
def create_production_run(
    run_in: ProductionRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["production", "admin", "owner"]))
):
    bom = db.query(BillOfMaterials).filter(BillOfMaterials.id == run_in.bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="Bill of Materials not found")
    product = db.query(Product).filter(Product.id == run_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Generate Batch Number: BATCH-YYYY-XXXX
    year = datetime.now(timezone.utc).year
    prefix = f"BATCH-{year}-"
    last_batch = db.query(ProductionRun).filter(ProductionRun.batch_number.like(f"{prefix}%")).order_by(ProductionRun.id.desc()).first()
    next_seq = 1
    if last_batch:
        try:
            next_seq = int(last_batch.batch_number.split("-")[-1]) + 1
        except Exception:
            next_seq = 1
    batch_number = f"{prefix}{next_seq:04d}"

    # Calculate Yield Variance: ((Actual - Planned) / Planned) * 100
    planned_qty = Decimal(str(run_in.planned_quantity))
    actual_good_qty = Decimal(str(run_in.actual_good_quantity))
    yield_variance = Decimal("0.00")
    if planned_qty > 0:
        yield_variance = (((actual_good_qty - planned_qty) / planned_qty) * Decimal("100.00")).quantize(Decimal("0.01"))

    # Check alert threshold
    threshold = Decimal(str(settings.VARIANCE_ALERT_THRESHOLD_PERCENT))
    is_alert = 1 if abs(yield_variance) > threshold else 0

    oil_variance = Decimal("0.00")

    run = ProductionRun(
        batch_number=batch_number,
        bom_id=bom.id,
        product_id=product.id,
        planned_quantity=planned_qty,
        actual_good_quantity=actual_good_qty,
        damaged_quantity=run_in.damaged_quantity,
        cartons_used=run_in.cartons_used,
        yield_variance_percent=yield_variance,
        oil_variance_percent=Decimal("0.00"),
        is_variance_alert=is_alert,
        status="completed",
        supervisor_id=current_user.id,
        notes=run_in.notes
    )
    db.add(run)
    db.flush()

    # Process material issues
    for issue_input in run_in.material_issues:
        if issue_input.material_type == "raw" and issue_input.raw_material_id:
            rm = db.query(RawMaterial).filter(RawMaterial.id == issue_input.raw_material_id).first()
            if not rm:
                raise HTTPException(status_code=404, detail=f"Raw material {issue_input.raw_material_id} not found")

            # Standard qty from BOM scaled to planned_quantity
            bom_item = next((b for b in bom.items if b.raw_material_id == rm.id), None)
            std_qty = (Decimal(str(bom_item.standard_quantity)) * (planned_qty / Decimal(str(bom.batch_size)))) if bom_item else Decimal("0.00")
            act_qty = Decimal(str(issue_input.actual_qty))
            cost = Decimal(str(rm.weighted_average_cost))

            var_pct = Decimal("0.00")
            if std_qty > 0:
                var_pct = (((act_qty - std_qty) / std_qty) * Decimal("100.00")).quantize(Decimal("0.01"))

            # Check if this is oil to record oil variance
            if "oil" in rm.name.lower():
                oil_variance = var_pct
                if abs(oil_variance) > threshold:
                    is_alert = 1

            InventoryService.record_raw_material_movement(
                db, rm.id, "out", act_qty, "production_issue", run.batch_number, run.batch_number, cost, f"Production Issue for {batch_number}"
            )

            p_issue = ProductionMaterialIssue(
                production_run_id=run.id,
                material_type="raw",
                raw_material_id=rm.id,
                standard_qty=std_qty,
                actual_qty=act_qty,
                unit=rm.unit,
                unit_cost=cost,
                total_cost=(act_qty * cost).quantize(Decimal("0.01")),
                variance_percent=var_pct
            )
            db.add(p_issue)

        elif issue_input.material_type == "packaging" and issue_input.packaging_material_id:
            pm = db.query(PackagingMaterial).filter(PackagingMaterial.id == issue_input.packaging_material_id).first()
            if not pm:
                raise HTTPException(status_code=404, detail=f"Packaging material {issue_input.packaging_material_id} not found")

            bom_item = next((b for b in bom.items if b.packaging_material_id == pm.id), None)
            std_qty = (Decimal(str(bom_item.standard_quantity)) * (planned_qty / Decimal(str(bom.batch_size)))) if bom_item else Decimal("0.00")
            act_qty = Decimal(str(issue_input.actual_qty))
            cost = Decimal(str(pm.unit_cost))

            var_pct = Decimal("0.00")
            if std_qty > 0:
                var_pct = (((act_qty - std_qty) / std_qty) * Decimal("100.00")).quantize(Decimal("0.01"))

            InventoryService.record_packaging_movement(
                db, pm.id, "out", act_qty, "production_issue", run.batch_number, run.batch_number, cost, f"Production Issue for {batch_number}"
            )

            p_issue = ProductionMaterialIssue(
                production_run_id=run.id,
                material_type="packaging",
                packaging_material_id=pm.id,
                standard_qty=std_qty,
                actual_qty=act_qty,
                unit=pm.unit,
                unit_cost=cost,
                total_cost=(act_qty * cost).quantize(Decimal("0.01")),
                variance_percent=var_pct
            )
            db.add(p_issue)

    # Record finished goods receipt into inventory
    if actual_good_qty > 0:
        InventoryService.record_product_movement(
            db, product.id, "in", actual_good_qty, "production_receipt", run.batch_number, run.batch_number, Decimal(str(product.selling_price)), f"Production Output: {actual_good_qty} packets"
        )

    # Record direct expenses if any
    if run_in.labour_expense > 0:
        db.add(Expense(
            production_run_id=run.id,
            expense_type="labour",
            amount=Decimal(str(run_in.labour_expense)),
            description="Production line labour"
        ))
    if run_in.power_gas_expense > 0:
        db.add(Expense(
            production_run_id=run.id,
            expense_type="power_gas",
            amount=Decimal(str(run_in.power_gas_expense)),
            description="Power and fuel gas"
        ))

    run.oil_variance_percent = oil_variance
    run.is_variance_alert = is_alert
    db.commit()
    return get_production_runs(db)[0]

@router.get("/variance-alerts")
def get_variance_alerts(db: Session = Depends(get_db)):
    runs = db.query(ProductionRun).filter(ProductionRun.is_variance_alert == 1).order_by(ProductionRun.id.desc()).all()
    alerts = []
    for r in runs:
        alerts.append({
            "id": r.id,
            "batch_number": r.batch_number,
            "product_name": r.product.name if r.product else "Food Item",
            "yield_variance_percent": r.yield_variance_percent,
            "oil_variance_percent": r.oil_variance_percent,
            "actual_good_quantity": r.actual_good_quantity,
            "damaged_quantity": r.damaged_quantity,
            "planned_quantity": r.planned_quantity,
            "date": r.created_at,
            "supervisor": r.supervisor.full_name if r.supervisor else "Supervisor"
        })
    return alerts

