from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.api.deps import get_db
from backend.app.models.production import ProductionRun
from backend.app.services.costing_service import CostingService

router = APIRouter()

@router.get("/batch/{batch_id}")
def get_batch_costing(batch_id: int, db: Session = Depends(get_db)):
    try:
        return CostingService.calculate_production_run_costing(db, batch_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/all-batches")
def get_all_batch_costings(db: Session = Depends(get_db)):
    runs = db.query(ProductionRun).order_by(ProductionRun.id.desc()).all()
    results = []
    for r in runs:
        try:
            results.append(CostingService.calculate_production_run_costing(db, r.id))
        except Exception:
            continue
    return results

