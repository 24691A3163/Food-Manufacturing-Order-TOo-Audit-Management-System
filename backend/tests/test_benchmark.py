from decimal import Decimal
from backend.app.services.benchmark_service import BenchmarkService

def test_full_benchmark_scenario(db_session):
    """
    Validates all 16 steps of the internship problem statement:
    - Flour closing: 120 kg
    - Oil closing: 19.5 litres
    - Spice mix closing: 3.8 kg
    - Pouches closing: 306 pcs
    - Cartons closing: 21 pcs
    - Finished goods after production: 238 packets
    - Finished goods after Retailer A dispatch: 88 packets
    - Production yield variance: -6%
    - Oil consumption variance: +5%
    - Retailer A taxable: ₹7,500
    - CGST: ₹187.50
    - SGST: ₹187.50
    - Invoice total: ₹7,875
    - Retailer A outstanding: ₹3,875
    - Distributor B shortage: 32 packets
    """
    res = BenchmarkService.run_benchmark(db_session)
    assert res["status"] == "success"

    closing = res["closing_balances"]
    assert closing["flour_kg"] == Decimal("120.00")
    assert closing["oil_litres"] == Decimal("19.50")
    assert closing["spice_mix_kg"] == Decimal("3.80")
    assert closing["pouches_pcs"] == Decimal("306.00")
    assert closing["cartons_pcs"] == Decimal("21.00")
    assert closing["finished_goods_after_production"] == Decimal("238.00")
    assert closing["finished_goods_pkts"] == Decimal("88.00")

    variances = res["production_variances"]
    assert variances["yield_variance_percent"] == Decimal("-6.00")
    assert variances["oil_variance_percent"] == Decimal("5.00")
    assert variances["variance_alert_flagged"] is True

    invoice = res["retailer_a_gst_invoice"]
    assert invoice["taxable_amount"] == Decimal("7500.00")
    assert invoice["cgst_amount"] == Decimal("187.50")
    assert invoice["sgst_amount"] == Decimal("187.50")
    assert invoice["total_amount"] == Decimal("7875.00")
    assert invoice["amount_paid"] == Decimal("4000.00")
    assert invoice["outstanding_balance"] == Decimal("3875.00")

    shortage = res["distributor_b_shortage"]
    assert shortage["shortage_quantity"] == Decimal("32.00")

    costing = res["unit_costing"]
    assert costing["actual_good_quantity"] == Decimal("188.00")
    assert costing["cost_per_good_packet"] == Decimal("31.14")
    assert costing["selling_price"] == Decimal("50.00")

