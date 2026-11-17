from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from decimal import Decimal

from backend.app.api.deps import get_db, require_roles
from backend.app.models.payment import Payment
from backend.app.models.customer import Customer
from backend.app.models.invoice import Invoice
from backend.app.models.user import User
from backend.app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter()

@router.get("", response_model=List[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    payments = db.query(Payment).order_by(Payment.id.desc()).all()
    results = []
    for p in payments:
        results.append({
            "id": p.id,
            "payment_number": p.payment_number,
            "invoice_id": p.invoice_id,
            "invoice_number": p.invoice.invoice_number if p.invoice else None,
            "customer_id": p.customer_id,
            "customer_name": p.customer.name if p.customer else None,
            "payment_date": p.payment_date,
            "amount": p.amount,
            "payment_mode": p.payment_mode,
            "reference_number": p.reference_number,
            "notes": p.notes,
            "created_at": p.created_at
        })
    return results

@router.post("", response_model=PaymentResponse)
def record_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "owner"]))
):
    customer = db.query(Customer).filter(Customer.id == payment_in.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    year = datetime.now(timezone.utc).year
    prefix = f"PAY-{year}-"
    last_pay = db.query(Payment).filter(Payment.payment_number.like(f"{prefix}%")).order_by(Payment.id.desc()).first()
    next_seq = 1
    if last_pay:
        try:
            next_seq = int(last_pay.payment_number.split("-")[-1]) + 1
        except Exception:
            next_seq = 1
    payment_number = f"{prefix}{next_seq:04d}"

    amt = Decimal(str(payment_in.amount))
    payment = Payment(
        payment_number=payment_number,
        invoice_id=payment_in.invoice_id,
        customer_id=customer.id,
        payment_date=datetime.now(timezone.utc),
        amount=amt,
        payment_mode=payment_in.payment_mode,
        reference_number=payment_in.reference_number,
        notes=payment_in.notes
    )
    db.add(payment)

    # Adjust invoice if specified
    if payment_in.invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == payment_in.invoice_id).first()
        if invoice:
            invoice.amount_paid = Decimal(str(invoice.amount_paid)) + amt
            invoice.balance_due = Decimal(str(invoice.total_amount)) - invoice.amount_paid
            if invoice.balance_due <= Decimal("0.00"):
                invoice.status = "paid"
                invoice.balance_due = Decimal("0.00")
            else:
                invoice.status = "partially_paid"

    # Reduce customer balance outstanding
    customer.balance_outstanding = max(Decimal("0.00"), Decimal(str(customer.balance_outstanding)) - amt)

    db.commit()
    db.refresh(payment)
    return get_payments(db)[0]

