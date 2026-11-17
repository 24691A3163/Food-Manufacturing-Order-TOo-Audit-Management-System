from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.services.benchmark_service import BenchmarkService

router = APIRouter()

@router.post("/run")
def run_benchmark_endpoint(db: Session = Depends(get_db)):
    """
    Executes the exact 16-step benchmark scenario from the internship problem statement:
    Resets tables, runs all 16 operations, computes variances, taxes, costing,
    and returns a complete audit verification report.
    """
    result = BenchmarkService.run_benchmark(db)
    return result

@router.get("/status")
def get_benchmark_status(db: Session = Depends(get_db)):
    """
    Evaluates current database status and returns the 16-step benchmark scorecard.
    """
    from backend.app.models.material import RawMaterial, PackagingMaterial
    from backend.app.models.product import Product
    from backend.app.models.invoice import Invoice
    from backend.app.models.customer import Customer
    from backend.app.models.production import ProductionRun

    flour = db.query(RawMaterial).filter(RawMaterial.code == "RM-FLOUR").first()
    oil = db.query(RawMaterial).filter(RawMaterial.code == "RM-OIL").first()
    spice = db.query(RawMaterial).filter(RawMaterial.code == "RM-SPICE").first()
    pouches = db.query(PackagingMaterial).filter(PackagingMaterial.code == "PM-POUCH-200G").first()
    cartons = db.query(PackagingMaterial).filter(PackagingMaterial.code == "PM-CARTON").first()
    murukku = db.query(Product).filter(Product.sku == "MRK-200G").first()
    retailer_a = db.query(Customer).filter(Customer.code == "CUST-TN-001").first()
    inv_a = db.query(Invoice).first()
    prod_run = db.query(ProductionRun).first()

    if not flour or not murukku:
        return {"is_seeded": False, "message": "Benchmark data is not yet initialized. Click 'Run Benchmark'."}

    return {
        "is_seeded": True,
        "flour_balance": float(flour.current_stock) if flour else 0,
        "flour_expected": 120.0,
        "oil_balance": float(oil.current_stock) if oil else 0,
        "oil_expected": 19.5,
        "spice_balance": float(spice.current_stock) if spice else 0,
        "spice_expected": 3.8,
        "pouches_balance": float(pouches.current_stock) if pouches else 0,
        "pouches_expected": 306.0,
        "cartons_balance": float(cartons.current_stock) if cartons else 0,
        "cartons_expected": 21.0,
        "finished_goods_balance": float(murukku.current_stock) if murukku else 0,
        "finished_goods_expected": 88.0,
        "retailer_a_outstanding": float(retailer_a.balance_outstanding) if retailer_a else 0,
        "retailer_a_expected": 3875.0,
        "invoice_total": float(inv_a.total_amount) if inv_a else 0,
        "invoice_expected": 7875.0,
        "yield_variance": float(prod_run.yield_variance_percent) if prod_run else 0,
        "yield_variance_expected": -6.0,
        "oil_variance": float(prod_run.oil_variance_percent) if prod_run else 0,
        "oil_variance_expected": 5.0
    }

