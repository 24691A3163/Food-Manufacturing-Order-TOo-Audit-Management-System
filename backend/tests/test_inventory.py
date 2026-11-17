import pytest
from decimal import Decimal
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.product import Product
from backend.app.models.inventory import StockMovement
from backend.app.services.inventory_service import InventoryService

def test_inventory_atomic_movement_and_ledger(db_session):
    # Setup material
    rm = RawMaterial(name="Flour", code="RM-FLOUR", unit="kg", current_stock=Decimal("100.00"), weighted_average_cost=Decimal("42.0000"))
    db_session.add(rm)
    db_session.commit()

    # Issue 40 kg flour
    movement = InventoryService.record_raw_material_movement(
        db=db_session,
        raw_material_id=rm.id,
        movement_type="out",
        quantity=Decimal("40.00"),
        source_document_type="production_issue",
        source_document_id="BATCH-001"
    )
    db_session.commit()

    assert rm.current_stock == Decimal("60.00")
    assert movement.running_balance == Decimal("60.00")
    assert movement.movement_type == "out"

    # Ledger entry verification
    ledger_records = db_session.query(StockMovement).filter(StockMovement.raw_material_id == rm.id).all()
    assert len(ledger_records) == 1
    assert ledger_records[0].source_document_id == "BATCH-001"

def test_inventory_insufficient_stock_error(db_session):
    product = Product(name="Murukku", sku="MRK-200", selling_price=Decimal("50.00"), current_stock=Decimal("88.00"))
    db_session.add(product)
    db_session.commit()

    # Attempt to dispatch 120 packets when only 88 are available
    with pytest.raises(ValueError) as excinfo:
        InventoryService.record_product_movement(
            db=db_session,
            product_id=product.id,
            movement_type="out",
            quantity=Decimal("120.00"),
            source_document_type="dispatch"
        )
    assert "Insufficient finished goods stock" in str(excinfo.value)

def test_weighted_average_cost_calculation(db_session):
    # 100 kg @ ₹42 opening + 60 kg @ ₹45 purchase = 160 kg @ ₹43.125
    rm = RawMaterial(name="Flour", code="RM-FLOUR", unit="kg", current_stock=Decimal("100.00"), weighted_average_cost=Decimal("42.0000"))
    db_session.add(rm)
    db_session.commit()

    InventoryService.record_raw_material_movement(
        db=db_session,
        raw_material_id=rm.id,
        movement_type="in",
        quantity=Decimal("60.00"),
        source_document_type="purchase",
        unit_cost=Decimal("45.0000")
    )
    db_session.commit()

    assert rm.current_stock == Decimal("160.00")
    expected_wac = Decimal("43.125")
    assert round(rm.weighted_average_cost, 3) == expected_wac

