from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Dict, Any, List

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.order import Order
from backend.app.models.invoice import Invoice
from backend.app.models.production import ProductionRun
from backend.app.models.customer import Customer
from backend.app.models.product import Product
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.user import User

router = APIRouter()

@router.get("/owner")
def get_owner_dashboard(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    orders = db.query(Order).order_by(Order.id.desc()).all()
    batches = db.query(ProductionRun).order_by(ProductionRun.id.desc()).all()
    customers = db.query(Customer).all()
    products = db.query(Product).all()

    total_invoiced = sum([Decimal(str(inv.total_amount)) for inv in invoices], Decimal("0.00"))
    total_collections = sum([Decimal(str(inv.amount_paid)) for inv in invoices], Decimal("0.00"))
    total_ar = sum([Decimal(str(c.balance_outstanding)) for c in customers], Decimal("0.00"))

    total_fg_pkts = sum([Decimal(str(p.current_stock)) for p in products], Decimal("0.00"))
    variance_alerts = len([b for b in batches if b.is_variance_alert == 1])

    rms = db.query(RawMaterial).all()
    pms = db.query(PackagingMaterial).all()
    low_stock_count = len([r for r in rms if r.current_stock <= r.reorder_level]) + \
                      len([p for p in pms if p.current_stock <= p.reorder_level]) + \
                      len([pr for pr in products if pr.current_stock <= pr.reorder_level])

    # Sample monthly trend for Recharts
    sales_trend = [
        {"month": "Jul", "sales": 45000, "production": 42000, "collections": 40000},
        {"month": "Aug", "sales": 52000, "production": 50000, "collections": 48000},
        {"month": "Sep", "sales": 61000, "production": 58000, "collections": 59000},
        {"month": "Oct", "sales": 70000, "production": 68000, "collections": 65000},
        {"month": "Nov", "sales": float(total_invoiced) if total_invoiced > 0 else 7875, "production": 5855, "collections": float(total_collections) if total_collections > 0 else 4000},
    ]

    category_dist = [
        {"name": "Murukku", "value": 45, "color": "#1e3a8a"},
        {"name": "Mixture", "value": 25, "color": "#0284c7"},
        {"name": "Chips", "value": 20, "color": "#10b981"},
        {"name": "Sweets", "value": 10, "color": "#f59e0b"}
    ]

    recent_orders_data = [
        {
            "id": o.id,
            "order_number": o.order_number,
            "customer_name": o.customer.name if o.customer else "",
            "salesman_name": o.salesman.full_name if o.salesman else "",
            "total_amount": float(o.total_amount),
            "status": o.status,
            "date": o.created_at.strftime("%d %b %H:%M") if o.created_at else ""
        }
        for o in orders[:5]
    ]

    recent_batches_data = [
        {
            "id": b.id,
            "batch_number": b.batch_number,
            "product_name": b.product.name if b.product else "",
            "actual_good": float(b.actual_good_quantity),
            "yield_variance": float(b.yield_variance_percent),
            "is_alert": bool(b.is_variance_alert),
            "status": b.status
        }
        for b in batches[:5]
    ]

    return {
        "total_invoiced_mtd": total_invoiced,
        "total_collections_mtd": total_collections,
        "total_outstanding_ar": total_ar,
        "finished_goods_packets": total_fg_pkts,
        "active_variance_alerts_count": variance_alerts,
        "recent_batches_count": len(batches),
        "low_stock_items_count": low_stock_count,
        "sales_trend": sales_trend,
        "category_distribution": category_dist,
        "recent_orders": recent_orders_data,
        "recent_batches": recent_batches_data
    }

@router.get("/salesman")
def get_salesman_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(Order.salesman_id == current_user.id).order_by(Order.id.desc()).all()
    customers = db.query(Customer).filter(Customer.is_active == True).all()

    total_value = sum([Decimal(str(o.total_amount)) for o in orders], Decimal("0.00"))
    pending_count = len([o for o in orders if o.status in ["submitted", "draft"]])
    approved_count = len([o for o in orders if o.status in ["approved", "invoiced", "dispatched"]])

    return {
        "salesman_name": current_user.full_name,
        "total_orders_count": len(orders),
        "total_sales_value": total_value,
        "pending_orders_count": pending_count,
        "approved_orders_count": approved_count,
        "customers": [
            {
                "id": c.id,
                "name": c.name,
                "code": c.code,
                "state": c.state,
                "phone": c.phone,
                "balance_outstanding": float(c.balance_outstanding)
            }
            for c in customers
        ],
        "recent_orders": [
            {
                "id": o.id,
                "order_number": o.order_number,
                "customer_name": o.customer.name if o.customer else "",
                "total_amount": float(o.total_amount),
                "status": o.status,
                "date": o.created_at.strftime("%d %b %H:%M") if o.created_at else ""
            }
            for o in orders[:10]
        ]
    }

