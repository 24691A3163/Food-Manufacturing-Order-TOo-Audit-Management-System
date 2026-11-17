from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.production import ProductionRun, ProductionMaterialIssue
from backend.app.models.expense import Expense
from backend.app.models.product import Product

class CostingService:
    @staticmethod
    def calculate_production_run_costing(db: Session, production_run_id: int) -> Dict[str, Any]:
        """
        Calculates total batch manufacturing cost, cost per good packet, and profit margin.
        """
        run = db.query(ProductionRun).filter(ProductionRun.id == production_run_id).first()
        if not run:
            raise ValueError(f"Production run {production_run_id} not found")

        # 1. Raw Material Cost
        rm_issues = db.query(ProductionMaterialIssue).filter(
            ProductionMaterialIssue.production_run_id == run.id,
            ProductionMaterialIssue.material_type == "raw"
        ).all()
        rm_cost = sum([Decimal(str(item.total_cost)) for item in rm_issues], Decimal("0.00"))

        # 2. Packaging Material Cost
        pm_issues = db.query(ProductionMaterialIssue).filter(
            ProductionMaterialIssue.production_run_id == run.id,
            ProductionMaterialIssue.material_type == "packaging"
        ).all()
        pm_cost = sum([Decimal(str(item.total_cost)) for item in pm_issues], Decimal("0.00"))

        # 3. Direct Expenses (Labour, Power/Gas, etc.)
        expenses = db.query(Expense).filter(Expense.production_run_id == run.id).all()
        labour_cost = sum([Decimal(str(e.amount)) for e in expenses if e.expense_type == "labour"], Decimal("0.00"))
        power_gas_cost = sum([Decimal(str(e.amount)) for e in expenses if e.expense_type == "power_gas"], Decimal("0.00"))
        other_overhead = sum([Decimal(str(e.amount)) for e in expenses if e.expense_type not in ["labour", "power_gas"]], Decimal("0.00"))
        total_direct_expenses = labour_cost + power_gas_cost + other_overhead

        # 4. Total Batch Cost
        total_batch_cost = rm_cost + pm_cost + total_direct_expenses

        # 5. Output quantities
        actual_good_pkts = Decimal(str(run.actual_good_quantity))
        damaged_pkts = Decimal(str(run.damaged_quantity))

        cost_per_good_packet = Decimal("0.00")
        if actual_good_pkts > 0:
            cost_per_good_packet = (total_batch_cost / actual_good_pkts).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # 6. Product Selling Price & Margins
        product = db.query(Product).filter(Product.id == run.product_id).first()
        selling_price = Decimal(str(product.selling_price)) if product else Decimal("50.00")
        
        gross_margin_per_packet = selling_price - cost_per_good_packet
        gross_margin_percent = Decimal("0.00")
        if selling_price > 0:
            gross_margin_percent = ((gross_margin_per_packet / selling_price) * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "batch_number": run.batch_number,
            "product_name": product.name if product else "Unknown",
            "planned_quantity": Decimal(str(run.planned_quantity)),
            "actual_good_quantity": actual_good_pkts,
            "damaged_quantity": damaged_pkts,
            "yield_variance_percent": Decimal(str(run.yield_variance_percent)),
            "oil_variance_percent": Decimal(str(run.oil_variance_percent)),
            "is_variance_alert": bool(run.is_variance_alert),
            "raw_material_cost": rm_cost.quantize(Decimal("0.01")),
            "packaging_cost": pm_cost.quantize(Decimal("0.01")),
            "labour_cost": labour_cost.quantize(Decimal("0.01")),
            "power_gas_cost": power_gas_cost.quantize(Decimal("0.01")),
            "other_overhead": other_overhead.quantize(Decimal("0.01")),
            "total_batch_cost": total_batch_cost.quantize(Decimal("0.01")),
            "cost_per_good_packet": cost_per_good_packet,
            "selling_price": selling_price.quantize(Decimal("0.01")),
            "gross_margin_per_packet": gross_margin_per_packet.quantize(Decimal("0.01")),
            "gross_margin_percent": gross_margin_percent
        }

