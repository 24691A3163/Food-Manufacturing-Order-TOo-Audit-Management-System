from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal

from backend.app.api.deps import get_db, require_roles
from backend.app.models.invoice import Invoice, InvoiceItem
from backend.app.models.order import Order
from backend.app.models.customer import Customer
from backend.app.models.user import User
from backend.app.schemas.invoice import InvoiceResponse
from backend.app.services.gst_service import GSTService
from backend.app.services.inventory_service import InventoryService
from backend.app.services.pdf_service import PDFService

router = APIRouter()

@router.get("", response_model=List[InvoiceResponse])
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.id.desc()).all()
    results = []
    for inv in invoices:
        items = []
        for itm in inv.items:
            items.append({
                "id": itm.id,
                "product_id": itm.product_id,
                "product_name": itm.product.name if itm.product else None,
                "hsn_code": itm.hsn_code,
                "quantity": itm.quantity,
                "unit_price": itm.unit_price,
                "taxable_value": itm.taxable_value,
                "cgst_rate": itm.cgst_rate,
                "cgst_amount": itm.cgst_amount,
                "sgst_rate": itm.sgst_rate,
                "sgst_amount": itm.sgst_amount,
                "igst_rate": itm.igst_rate,
                "igst_amount": itm.igst_amount,
                "total_item_amount": itm.total_item_amount
            })
        results.append({
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "order_id": inv.order_id,
            "customer_id": inv.customer_id,
            "customer_name": inv.customer.name if inv.customer else None,
            "invoice_date": inv.invoice_date,
            "due_date": inv.due_date,
            "place_of_supply": inv.place_of_supply,
            "is_interstate": inv.is_interstate,
            "taxable_amount": inv.taxable_amount,
            "cgst_rate": inv.cgst_rate,
            "cgst_amount": inv.cgst_amount,
            "sgst_rate": inv.sgst_rate,
            "sgst_amount": inv.sgst_amount,
            "igst_rate": inv.igst_rate,
            "igst_amount": inv.igst_amount,
            "total_amount": inv.total_amount,
            "amount_paid": inv.amount_paid,
            "balance_due": inv.balance_due,
            "status": inv.status,
            "dispatch_status": inv.dispatch_status,
            "dispatched_at": inv.dispatched_at,
            "notes": inv.notes,
            "items": items,
            "created_at": inv.created_at
        })
    return results

@router.post("/generate-from-order/{order_id}", response_model=InvoiceResponse)
def generate_invoice_from_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "owner"]))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.invoice:
        raise HTTPException(status_code=400, detail=f"Invoice already generated: {order.invoice.invoice_number}")

    customer = order.customer
    is_interstate = GSTService.is_interstate_transaction(customer)

    # Calculate GST line items
    taxable_amount = Decimal("0.00")
    total_cgst = Decimal("0.00")
    total_sgst = Decimal("0.00")
    total_igst = Decimal("0.00")
    total_invoice_amt = Decimal("0.00")

    invoice_number = GSTService.generate_invoice_number(db)
    invoice = Invoice(
        invoice_number=invoice_number,
        order_id=order.id,
        customer_id=customer.id,
        invoice_date=datetime.now(timezone.utc),
        place_of_supply=customer.state,
        is_interstate=is_interstate,
        taxable_amount=Decimal("0.00"),
        cgst_rate=Decimal("0.00"),
        cgst_amount=Decimal("0.00"),
        sgst_rate=Decimal("0.00"),
        sgst_amount=Decimal("0.00"),
        igst_rate=Decimal("0.00"),
        igst_amount=Decimal("0.00"),
        total_amount=Decimal("0.00"),
        amount_paid=Decimal("0.00"),
        balance_due=Decimal("0.00"),
        status="unpaid",
        dispatch_status="pending",
        notes=f"Generated from {order.order_number}"
    )
    db.add(invoice)
    db.flush()

    for item in order.items:
        prod = item.product
        item_taxable = Decimal(str(item.subtotal))
        item_gst_rate = Decimal(str(prod.gst_rate))
        tax_calc = GSTService.calculate_taxes(item_taxable, item_gst_rate, is_interstate)

        taxable_amount += tax_calc["taxable_value"]
        total_cgst += tax_calc["cgst_amount"]
        total_sgst += tax_calc["sgst_amount"]
        total_igst += tax_calc["igst_amount"]
        total_invoice_amt += tax_calc["total_amount"]

        inv_item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=prod.id,
            hsn_code=prod.hsn_code,
            quantity=item.quantity,
            unit_price=item.unit_price,
            taxable_value=tax_calc["taxable_value"],
            cgst_rate=tax_calc["cgst_rate"],
            cgst_amount=tax_calc["cgst_amount"],
            sgst_rate=tax_calc["sgst_rate"],
            sgst_amount=tax_calc["sgst_amount"],
            igst_rate=tax_calc["igst_rate"],
            igst_amount=tax_calc["igst_amount"],
            total_item_amount=tax_calc["total_amount"]
        )
        db.add(inv_item)

    invoice.taxable_amount = taxable_amount
    invoice.cgst_rate = Decimal("2.50") if not is_interstate else Decimal("0.00")
    invoice.cgst_amount = total_cgst
    invoice.sgst_rate = Decimal("2.50") if not is_interstate else Decimal("0.00")
    invoice.sgst_amount = total_sgst
    invoice.igst_rate = Decimal("5.00") if is_interstate else Decimal("0.00")
    invoice.igst_amount = total_igst
    invoice.total_amount = total_invoice_amt
    invoice.balance_due = total_invoice_amt

    # Update customer balance and order status
    customer.balance_outstanding = Decimal(str(customer.balance_outstanding)) + total_invoice_amt
    order.status = "invoiced"

    db.commit()
    db.refresh(invoice)
    return get_invoices(db)[0]

@router.post("/{invoice_id}/dispatch")
def dispatch_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "owner"]))
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.dispatch_status == "dispatched":
        raise HTTPException(status_code=400, detail="Invoice is already dispatched")

    # Reduce finished goods stock atomically for each item
    for item in invoice.items:
        InventoryService.record_product_movement(
            db=db,
            product_id=item.product_id,
            movement_type="out",
            quantity=Decimal(str(item.quantity)),
            source_document_type="dispatch",
            source_document_id=invoice.invoice_number,
            unit_cost=Decimal(str(item.unit_price)),
            notes=f"Dispatch for {invoice.customer.name} under {invoice.invoice_number}",
            created_by=current_user.full_name
        )

    invoice.dispatch_status = "dispatched"
    invoice.dispatched_at = datetime.now(timezone.utc)
    if invoice.order:
        invoice.order.status = "dispatched"

    db.commit()
    return {"message": f"Invoice {invoice.invoice_number} dispatched successfully", "dispatch_status": "dispatched"}

@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    pdf_bytes = PDFService.generate_invoice_pdf(invoice)
    filename = f"Invoice_{invoice.invoice_number}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

