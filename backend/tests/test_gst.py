from decimal import Decimal
from backend.app.services.gst_service import GSTService
from backend.app.models.customer import Customer

def test_intrastate_gst_calculation():
    # Intrastate Tamil Nadu (2.5% CGST + 2.5% SGST on ₹7,500)
    tax_result = GSTService.calculate_taxes(
        taxable_value=Decimal("7500.00"),
        gst_rate=Decimal("5.00"),
        is_interstate=False
    )
    assert tax_result["taxable_value"] == Decimal("7500.00")
    assert tax_result["cgst_rate"] == Decimal("2.50")
    assert tax_result["cgst_amount"] == Decimal("187.50")
    assert tax_result["sgst_rate"] == Decimal("2.50")
    assert tax_result["sgst_amount"] == Decimal("187.50")
    assert tax_result["igst_rate"] == Decimal("0.00")
    assert tax_result["igst_amount"] == Decimal("0.00")
    assert tax_result["total_amount"] == Decimal("7875.00")

def test_interstate_gst_calculation():
    # Interstate Karnataka (5.0% IGST on ₹6,000)
    tax_result = GSTService.calculate_taxes(
        taxable_value=Decimal("6000.00"),
        gst_rate=Decimal("5.00"),
        is_interstate=True
    )
    assert tax_result["taxable_value"] == Decimal("6000.00")
    assert tax_result["cgst_amount"] == Decimal("0.00")
    assert tax_result["sgst_amount"] == Decimal("0.00")
    assert tax_result["igst_rate"] == Decimal("5.00")
    assert tax_result["igst_amount"] == Decimal("300.00")
    assert tax_result["total_amount"] == Decimal("6300.00")

def test_customer_state_detection():
    tn_customer = Customer(name="TN Mart", code="C-01", state="Tamil Nadu", state_code="33")
    ka_customer = Customer(name="KA Store", code="C-02", state="Karnataka", state_code="29")
    
    assert GSTService.is_interstate_transaction(tn_customer) is False
    assert GSTService.is_interstate_transaction(ka_customer) is True

