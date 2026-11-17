import io
import pandas as pd
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Dict, Any, List

from backend.app.api.deps import get_db
from backend.app.models.invoice import Invoice
from backend.app.models.customer import Customer
from backend.app.models.production import ProductionRun
from backend.app.models.inventory import StockMovement
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.product import Product

router = APIRouter()

@router.get("/sales-summary")
def get_sales_summary(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    total_invoiced = sum([Decimal(str(inv.total_amount)) for inv in invoices], Decimal("0.00"))
    total_taxable = sum([Decimal(str(inv.taxable_amount)) for inv in invoices], Decimal("0.00"))
    total_tax = sum([Decimal(str(inv.cgst_amount + inv.sgst_amount + inv.igst_amount)) for inv in invoices], Decimal("0.00"))
    total_collected = sum([Decimal(str(inv.amount_paid)) for inv in invoices], Decimal("0.00"))
    total_outstanding = sum([Decimal(str(inv.balance_due)) for inv in invoices], Decimal("0.00"))

    # Customer breakdown
    customers = db.query(Customer).all()
    cust_data = []
    for c in customers:
        c_invoices = [inv for inv in invoices if inv.customer_id == c.id]
        c_sales = sum([Decimal(str(i.total_amount)) for i in c_invoices], Decimal("0.00"))
        cust_data.append({
            "customer_id": c.id,
            "customer_name": c.name,
            "state": c.state,
            "total_purchases": c_sales,
            "balance_outstanding": Decimal(str(c.balance_outstanding))
        })

    return {
        "total_invoiced": total_invoiced,
        "total_taxable": total_taxable,
        "total_tax": total_tax,
        "total_collected": total_collected,
        "total_outstanding": total_outstanding,
        "customer_breakdown": cust_data
    }

@router.get("/gst-gstr1")
def get_gst_gstr1(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.invoice_date.desc()).all()
    total_taxable = Decimal("0.00")
    total_cgst = Decimal("0.00")
    total_sgst = Decimal("0.00")
    total_igst = Decimal("0.00")
    total_cess = Decimal("0.00")

    b2b_records = []
    for inv in invoices:
        total_taxable += Decimal(str(inv.taxable_amount))
        total_cgst += Decimal(str(inv.cgst_amount))
        total_sgst += Decimal(str(inv.sgst_amount))
        total_igst += Decimal(str(inv.igst_amount))

        b2b_records.append({
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date.strftime("%d-%m-%Y") if inv.invoice_date else "",
            "customer_name": inv.customer.name if inv.customer else "",
            "customer_gstin": inv.customer.gstin if inv.customer and inv.customer.gstin else "Unregistered",
            "place_of_supply": inv.place_of_supply,
            "is_interstate": inv.is_interstate,
            "taxable_value": inv.taxable_amount,
            "cgst_amount": inv.cgst_amount,
            "sgst_amount": inv.sgst_amount,
            "igst_amount": inv.igst_amount,
            "invoice_total": inv.total_amount,
            "status": inv.status
        })

    return {
        "gstin": "33AABCS9876Q1Z2",
        "tax_period": "Current Month",
        "summary": {
            "total_taxable": total_taxable,
            "total_cgst": total_cgst,
            "total_sgst": total_sgst,
            "total_igst": total_igst,
            "total_tax": total_cgst + total_sgst + total_igst,
            "invoice_count": len(invoices)
        },
        "b2b_invoices": b2b_records
    }

@router.get("/export/stock-ledger-csv")
def export_stock_ledger_csv(db: Session = Depends(get_db)):
    movements = db.query(StockMovement).order_by(StockMovement.id.desc()).all()
    data = []
    for m in movements:
        item_name = ""
        if m.item_type == "raw" and m.raw_material:
            item_name = m.raw_material.name
        elif m.item_type == "packaging" and m.packaging_material:
            item_name = m.packaging_material.name
        elif m.item_type == "finished_good" and m.product:
            item_name = m.product.name

        data.append({
            "ID": m.id,
            "Timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M:%S") if m.timestamp else "",
            "Item Type": m.item_type.upper(),
            "Item Description": item_name,
            "Movement": m.movement_type.upper(),
            "Quantity": float(m.quantity),
            "Document Type": m.source_document_type,
            "Document Reference": m.source_document_id or "",
            "Batch Number": m.batch_number or "",
            "Unit Cost (INR)": float(m.unit_cost),
            "Running Balance": float(m.running_balance),
            "Notes": m.notes or ""
        })

    df = pd.DataFrame(data)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=Stock_Ledger_Export.csv"}
    )

@router.get("/export/production-excel")
def export_production_excel(db: Session = Depends(get_db)):
    runs = db.query(ProductionRun).order_by(ProductionRun.id.desc()).all()
    data = []
    for r in runs:
        data.append({
            "Batch Number": r.batch_number,
            "Product": r.product.name if r.product else "",
            "Planned Qty (Pkts)": float(r.planned_quantity),
            "Actual Good Qty": float(r.actual_good_quantity),
            "Damaged Pouches": float(r.damaged_quantity),
            "Cartons Used": float(r.cartons_used),
            "Yield Variance %": float(r.yield_variance_percent),
            "Oil Variance %": float(r.oil_variance_percent),
            "Variance Alert (>3%)": "ALERT" if r.is_variance_alert else "NORMAL",
            "Status": r.status.upper(),
            "Date": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Production_Yield_Report")
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Production_Audit_Report.xlsx"}
    )

