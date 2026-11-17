from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.core.config import settings
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.services.benchmark_service import BenchmarkService
from backend.app.models.user import User

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

def auto_seed_if_empty():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            print("Fresh database detected. Initializing with NIT Trichy benchmark scenario...")
            BenchmarkService.run_benchmark(db)
            print("NIT Trichy benchmark scenario seeded.")
    except Exception as e:
        print(f"Seed note: {e}")
    finally:
        db.close()

# Import routers
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.customers import router as customers_router
from backend.app.api.v1.products import router as products_router
from backend.app.api.v1.materials import router as materials_router
from backend.app.api.v1.bom import router as bom_router
from backend.app.api.v1.orders import router as orders_router
from backend.app.api.v1.invoices import router as invoices_router
from backend.app.api.v1.production import router as production_router
from backend.app.api.v1.inventory import router as inventory_router
from backend.app.api.v1.purchases import router as purchases_router
from backend.app.api.v1.costing import router as costing_router
from backend.app.api.v1.payments import router as payments_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.benchmark import router as benchmark_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
api_v1 = settings.API_V1_STR
app.include_router(auth_router, prefix=f"{api_v1}/auth", tags=["Authentication & Users"])
app.include_router(dashboard_router, prefix=f"{api_v1}/dashboard", tags=["Dashboards"])
app.include_router(customers_router, prefix=f"{api_v1}/customers", tags=["Customers"])
app.include_router(products_router, prefix=f"{api_v1}/products", tags=["Products"])
app.include_router(materials_router, prefix=f"{api_v1}/materials", tags=["Raw & Packaging Materials"])
app.include_router(bom_router, prefix=f"{api_v1}/bom", tags=["Bill of Materials"])
app.include_router(orders_router, prefix=f"{api_v1}/orders", tags=["Sales Orders"])
app.include_router(invoices_router, prefix=f"{api_v1}/invoices", tags=["GST Invoices & Dispatch"])
app.include_router(production_router, prefix=f"{api_v1}/production", tags=["Production & Variance"])
app.include_router(inventory_router, prefix=f"{api_v1}/inventory", tags=["Stock Ledger & Inventory"])
app.include_router(purchases_router, prefix=f"{api_v1}/purchases", tags=["Purchases & Suppliers"])
app.include_router(costing_router, prefix=f"{api_v1}/costing", tags=["Costing & Margins"])
app.include_router(payments_router, prefix=f"{api_v1}/payments", tags=["Payments & Receivables"])
app.include_router(reports_router, prefix=f"{api_v1}/reports", tags=["Reports & Exports"])
app.include_router(benchmark_router, prefix=f"{api_v1}/benchmark", tags=["Benchmark Runner"])

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": "1.0.0"}

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "docs": f"{settings.API_V1_STR}/docs",
        "benchmark_endpoint": f"{settings.API_V1_STR}/benchmark/run"
    }
