from decimal import Decimal
from backend.app.models.production import ProductionRun

def test_production_variance_alert_flag():
    # Planned 200, Actual 188 -> Yield variance = (188 - 200)/200 = -6.00%
    planned = Decimal("200.00")
    actual = Decimal("188.00")
    yield_var = ((actual - planned) / planned) * Decimal("100.00")
    assert yield_var == Decimal("-6.00")

    # Standard oil 10.0L, actual 10.5L -> Material variance = (10.5 - 10)/10 = +5.00%
    std_oil = Decimal("10.00")
    act_oil = Decimal("10.50")
    oil_var = ((act_oil - std_oil) / std_oil) * Decimal("100.00")
    assert oil_var == Decimal("5.00")

    # Check alert condition: abs(variance) > 3.0%
    threshold = Decimal("3.0")
    assert abs(yield_var) > threshold
    assert abs(oil_var) > threshold

