from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.config import settings
from backend.app.models.customer import Customer
from backend.app.models.invoice import Invoice

class GSTService:
    @staticmethod
    def is_interstate_transaction(customer: Customer) -> bool:
        """
        Company is located in Tamil Nadu (State Code 33).
        If customer state is NOT Tamil Nadu or state_code != 33, it's interstate.
        """
        company_state_code = settings.COMPANY_STATE_CODE.strip()
        cust_code = (customer.state_code or "").strip()
        cust_state = (customer.state or "").strip().lower()

        if cust_code:
            return cust_code != company_state_code
        return cust_state != settings.COMPANY_STATE.strip().lower()

    @staticmethod
    def calculate_taxes(
        taxable_value: Decimal,
        gst_rate: Decimal,
        is_interstate: bool
    ) -> Dict[str, Decimal]:
        """
        Calculates CGST, SGST, IGST and Total with strict 2-decimal half-up rounding.
        """
        taxable = Decimal(str(taxable_value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        rate = Decimal(str(gst_rate))

        if is_interstate:
            igst_rate = rate
            cgst_rate = Decimal("0.00")
            sgst_rate = Decimal("0.00")
            
            igst_amount = (taxable * (igst_rate / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            cgst_amount = Decimal("0.00")
            sgst_amount = Decimal("0.00")
        else:
            igst_rate = Decimal("0.00")
            cgst_rate = (rate / Decimal("2")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            sgst_rate = (rate / Decimal("2")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
            cgst_amount = (taxable * (cgst_rate / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            sgst_amount = (taxable * (sgst_rate / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            igst_amount = Decimal("0.00")

        total_tax = cgst_amount + sgst_amount + igst_amount
        total_amount = taxable + total_tax

        return {
            "taxable_value": taxable,
            "is_interstate": is_interstate,
            "cgst_rate": cgst_rate,
            "cgst_amount": cgst_amount,
            "sgst_rate": sgst_rate,
            "sgst_amount": sgst_amount,
            "igst_rate": igst_rate,
            "igst_amount": igst_amount,
            "total_tax": total_tax,
            "total_amount": total_amount
        }

    @staticmethod
    def generate_invoice_number(db: Session) -> str:
        current_year = datetime.now(timezone.utc).year
        prefix = f"INV-{current_year}-"
        
        last_invoice = db.query(Invoice).filter(
            Invoice.invoice_number.like(f"{prefix}%")
        ).order_by(Invoice.id.desc()).first()

        if not last_invoice:
            next_seq = 1
        else:
            try:
                seq_str = last_invoice.invoice_number.split("-")[-1]
                next_seq = int(seq_str) + 1
            except Exception:
                next_seq = 1

        return f"{prefix}{next_seq:04d}"

