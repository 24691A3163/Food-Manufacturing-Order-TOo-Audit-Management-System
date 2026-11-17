from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole
from backend.app.models.customer import Customer
from backend.app.models.supplier import Supplier
from backend.app.models.product import Product
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.bom import BillOfMaterials, BOMItem
from backend.app.models.purchase import Purchase, PurchaseItem
from backend.app.models.order import Order, OrderItem
from backend.app.models.invoice import Invoice, InvoiceItem
from backend.app.models.production import ProductionRun, ProductionMaterialIssue
from backend.app.models.payment import Payment
from backend.app.models.expense import Expense
from backend.app.models.inventory import StockMovement
from backend.app.services.inventory_service import InventoryService
from backend.app.services.gst_service import GSTService
from backend.app.services.costing_service import CostingService

class BenchmarkService:
    @staticmethod
    def run_benchmark(db: Session) -> Dict[str, Any]:
        """
        Executes the exact 16-step benchmark scenario from the NIT Trichy internship statement:
        'Order-to-Audit System for a Small Food Manufacturer'.
        Cleans existing benchmark state and rebuilds the exact scenario with verification checks.
        """
        # 1. Clean existing records for a fresh benchmark run
        db.query(StockMovement).delete()
        db.query(Expense).delete()
        db.query(Payment).delete()
        db.query(InvoiceItem).delete()
        db.query(Invoice).delete()
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(ProductionMaterialIssue).delete()
        db.query(ProductionRun).delete()
        db.query(PurchaseItem).delete()
        db.query(Purchase).delete()
        db.query(BOMItem).delete()
        db.query(BillOfMaterials).delete()
        db.query(Product).delete()
        db.query(PackagingMaterial).delete()
        db.query(RawMaterial).delete()
        db.query(Supplier).delete()
        db.query(Customer).delete()
        db.query(User).delete()
        db.commit()

        # 2. Seed Users (5 Roles)
        default_pwd = get_password_hash("password123")
        owner_user = User(
            email="owner@fooderp.com",
            hashed_password=default_pwd,
            full_name="Sundaram Ramakrishnan (Owner)",
            role=UserRole.OWNER,
            phone="+91 94433 11111",
            is_active=True
        )
        admin_user = User(
            email="admin@fooderp.com",
            hashed_password=default_pwd,
            full_name="Meenakshi Sundaram (Admin)",
            role=UserRole.ADMIN,
            phone="+91 94433 22222",
            is_active=True
        )
        salesman_a = User(
            email="salesman.a@fooderp.com",
            hashed_password=default_pwd,
            full_name="Karthik Raj (Salesman A)",
            role=UserRole.SALESMAN,
            phone="+91 94433 33333",
            is_active=True
        )
        salesman_b = User(
            email="salesman.b@fooderp.com",
            hashed_password=default_pwd,
            full_name="Venkatesh Iyer (Salesman B)",
            role=UserRole.SALESMAN,
            phone="+91 94433 44444",
            is_active=True
        )
        prod_supervisor = User(
            email="supervisor@fooderp.com",
            hashed_password=default_pwd,
            full_name="Muthukumar S. (Production Supervisor)",
            role=UserRole.PRODUCTION,
            phone="+91 94433 55555",
            is_active=True
        )
        auditor_user = User(
            email="auditor@fooderp.com",
            hashed_password=default_pwd,
            full_name="Ranganathan FCA (Auditor)",
            role=UserRole.AUDITOR,
            phone="+91 94433 66666",
            is_active=True
        )
        db.add_all([owner_user, admin_user, salesman_a, salesman_b, prod_supervisor, auditor_user])
        db.flush()

        # 3. Seed Customers
        retailer_a = Customer(
            name="Retailer A - Sri Krishna Provision Stores",
            code="CUST-TN-001",
            contact_person="Krishna Moorthy",
            phone="+91 98422 12345",
            email="krishna.stores@gmail.com",
            billing_address="14 West Car Street, Srirangam, Tiruchirappalli",
            shipping_address="14 West Car Street, Srirangam, Tiruchirappalli",
            state="Tamil Nadu",
            state_code="33",
            gstin="33ABCDE1234F1Z5",
            credit_limit=Decimal("50000.00"),
            balance_outstanding=Decimal("0.00")
        )
        distributor_b = Customer(
            name="Distributor B - Bengaluru Fine Foods Agencies",
            code="CUST-KA-002",
            contact_person="Anand Hegde",
            phone="+91 98800 54321",
            email="orders@blrfoodagencies.com",
            billing_address="88 Industrial Suburb, Yeshwanthpur, Bengaluru",
            shipping_address="88 Industrial Suburb, Yeshwanthpur, Bengaluru",
            state="Karnataka",
            state_code="29",
            gstin="29XYZAB9876C1Z3",
            credit_limit=Decimal("100000.00"),
            balance_outstanding=Decimal("0.00")
        )
        db.add_all([retailer_a, distributor_b])
        db.flush()

        # 4. Seed Supplier
        supplier_agro = Supplier(
            name="Madurai Agro Mills Ltd",
            code="SUP-001",
            contact_person="Ramasamy Nadar",
            phone="+91 94440 98765",
            email="sales@maduraiagro.com",
            address="45 Grain Market Road, Madurai, Tamil Nadu",
            state="Tamil Nadu",
            gstin="33AAACM1122D1Z9"
        )
        db.add(supplier_agro)
        db.flush()

        # 5. Seed Product: Murukku 200 g
        product_murukku = Product(
            name="Murukku 200 g",
            sku="MRK-200G",
            category="Savouries",
            unit="packet",
            weight_grams=Decimal("200.00"),
            hsn_code="21069099",
            selling_price=Decimal("50.00"),
            gst_rate=Decimal("5.00"),
            current_stock=Decimal("0.00"),
            reorder_level=Decimal("50.00")
        )
        db.add(product_murukku)
        db.flush()

        # 6. Seed Raw & Packaging Materials (Opening Balances)
        # Flour: 100 kg at ₹42
        rm_flour = RawMaterial(
            name="Flour",
            code="RM-FLOUR",
            unit="kg",
            current_stock=Decimal("0.00"),
            weighted_average_cost=Decimal("42.0000")
        )
        # Oil: 30 litres at ₹140
        rm_oil = RawMaterial(
            name="Cooking oil",
            code="RM-OIL",
            unit="litre",
            current_stock=Decimal("0.00"),
            weighted_average_cost=Decimal("140.0000")
        )
        # Salt and spice mix: 5 kg at ₹200
        rm_spice = RawMaterial(
            name="Salt and spice mix",
            code="RM-SPICE",
            unit="kg",
            current_stock=Decimal("0.00"),
            weighted_average_cost=Decimal("200.0000")
        )
        # Pouches: 500 pcs at ₹2.50
        pm_pouches = PackagingMaterial(
            name="200 g pouches",
            code="PM-POUCH-200G",
            unit="piece",
            current_stock=Decimal("0.00"),
            unit_cost=Decimal("2.5000")
        )
        # Cartons: 30 pcs at ₹15
        pm_cartons = PackagingMaterial(
            name="Cartons",
            code="PM-CARTON",
            unit="piece",
            current_stock=Decimal("0.00"),
            unit_cost=Decimal("15.0000")
        )
        db.add_all([rm_flour, rm_oil, rm_spice, pm_pouches, pm_cartons])
        db.flush()

        # Record Opening Inventory via Stock Ledger
        InventoryService.record_raw_material_movement(
            db, rm_flour.id, "in", Decimal("100.00"), "opening_balance", "OB-RM-01", None, Decimal("42.0000"), "Opening Inventory: 100 kg Flour @ ₹42"
        )
        InventoryService.record_raw_material_movement(
            db, rm_oil.id, "in", Decimal("30.00"), "opening_balance", "OB-RM-02", None, Decimal("140.0000"), "Opening Inventory: 30 L Oil @ ₹140"
        )
        InventoryService.record_raw_material_movement(
            db, rm_spice.id, "in", Decimal("5.00"), "opening_balance", "OB-RM-03", None, Decimal("200.0000"), "Opening Inventory: 5 kg Spice Mix @ ₹200"
        )
        InventoryService.record_packaging_movement(
            db, pm_pouches.id, "in", Decimal("500.00"), "opening_balance", "OB-PM-01", None, Decimal("2.5000"), "Opening Inventory: 500 Pouches @ ₹2.50"
        )
        InventoryService.record_packaging_movement(
            db, pm_cartons.id, "in", Decimal("30.00"), "opening_balance", "OB-PM-02", None, Decimal("15.0000"), "Opening Inventory: 30 Cartons @ ₹15"
        )
        InventoryService.record_product_movement(
            db, product_murukku.id, "in", Decimal("50.00"), "opening_balance", "OB-FG-01", None, Decimal("50.00"), "Opening Inventory: 50 Finished Murukku Packets"
        )
        db.flush()

        # 7. Seed BOM for 200 packets:
        # Flour: 40 kg, Oil: 10 litres, Spice: 1.2 kg, Pouches: 200 pcs, Cartons: 10 pcs
        bom_murukku = BillOfMaterials(
            product_id=product_murukku.id,
            version="1.0",
            batch_size=Decimal("200.00"),
            notes="Standard recipe for 200 packets of 200g Murukku"
        )
        db.add(bom_murukku)
        db.flush()

        bom_items = [
            BOMItem(bom_id=bom_murukku.id, item_type="raw", raw_material_id=rm_flour.id, standard_quantity=Decimal("40.00"), unit="kg"),
            BOMItem(bom_id=bom_murukku.id, item_type="raw", raw_material_id=rm_oil.id, standard_quantity=Decimal("10.00"), unit="litre"),
            BOMItem(bom_id=bom_murukku.id, item_type="raw", raw_material_id=rm_spice.id, standard_quantity=Decimal("1.20"), unit="kg"),
            BOMItem(bom_id=bom_murukku.id, item_type="packaging", packaging_material_id=pm_pouches.id, standard_quantity=Decimal("200.00"), unit="piece"),
            BOMItem(bom_id=bom_murukku.id, item_type="packaging", packaging_material_id=pm_cartons.id, standard_quantity=Decimal("10.00"), unit="piece"),
        ]
        db.add_all(bom_items)
        db.flush()

        # ==========================================
        # BENCHMARK TRANSACTION 1:
        # Purchase 60 kg flour at ₹45/kg.
        # ==========================================
        po1 = Purchase(
            purchase_number="PUR-2026-0001",
            supplier_id=supplier_agro.id,
            supplier_invoice_no="MAD-AGRO-789",
            status="received",
            total_amount=Decimal("2700.00"),  # 60 * 45
            notes="Benchmark Tx 1: Purchase 60 kg flour @ ₹45/kg"
        )
        db.add(po1)
        db.flush()

        po_item = PurchaseItem(
            purchase_id=po1.id,
            item_type="raw",
            raw_material_id=rm_flour.id,
            quantity=Decimal("60.00"),
            unit_price=Decimal("45.00"),
            total_cost=Decimal("2700.00"),
            unit="kg"
        )
        db.add(po_item)
        
        # Update flour inventory & weighted-average cost: (100*42 + 60*45) / 160 = 6900 / 160 = ₹43.125/kg
        InventoryService.record_raw_material_movement(
            db, rm_flour.id, "in", Decimal("60.00"), "purchase", po1.purchase_number, None, Decimal("45.0000"), "Purchase 60 kg flour @ ₹45/kg"
        )
        db.flush()

        # ==========================================
        # BENCHMARK TRANSACTIONS 2 to 8:
        # Production Run of Murukku 200g
        # Planned: 200 pkts
        # Issue 40 kg flour, 10.5 L cooking oil, 1.2 kg spice mix
        # Output: 188 good pkts, 6 damaged pouches, 9 cartons used
        # ==========================================
        # Calculate yield variance: (188 - 200) / 200 = -6%
        # Calculate oil variance: (10.5 - 10) / 10 = +5%
        yield_var = Decimal("-6.00")
        oil_var = Decimal("5.00")
        is_alert = 1  # Exceeds 3%

        prod_run = ProductionRun(
            batch_number="BATCH-2026-0001",
            bom_id=bom_murukku.id,
            product_id=product_murukku.id,
            planned_quantity=Decimal("200.00"),
            actual_good_quantity=Decimal("188.00"),
            damaged_quantity=Decimal("6.00"),
            cartons_used=Decimal("9.00"),
            yield_variance_percent=yield_var,
            oil_variance_percent=oil_var,
            is_variance_alert=is_alert,
            status="completed",
            supervisor_id=prod_supervisor.id,
            notes="Benchmark Production Run: Murukku 200g Batch 1"
        )
        db.add(prod_run)
        db.flush()

        # Tx 3: Issue 40 kg flour (Current weighted cost: ₹43.125/kg)
        flour_cost = Decimal(str(rm_flour.weighted_average_cost))
        InventoryService.record_raw_material_movement(
            db, rm_flour.id, "out", Decimal("40.00"), "production_issue", prod_run.batch_number, prod_run.batch_number, flour_cost, "Production Issue: 40 kg Flour"
        )
        issue_flour = ProductionMaterialIssue(
            production_run_id=prod_run.id,
            material_type="raw",
            raw_material_id=rm_flour.id,
            standard_qty=Decimal("40.00"),
            actual_qty=Decimal("40.00"),
            unit="kg",
            unit_cost=flour_cost,
            total_cost=(Decimal("40.00") * flour_cost).quantize(Decimal("0.01")),
            variance_percent=Decimal("0.00")
        )

        # Tx 4: Issue 10.5 litres cooking oil (Standard 10.0L -> +5% variance)
        oil_cost = Decimal(str(rm_oil.weighted_average_cost))
        InventoryService.record_raw_material_movement(
            db, rm_oil.id, "out", Decimal("10.50"), "production_issue", prod_run.batch_number, prod_run.batch_number, oil_cost, "Production Issue: 10.5 L Cooking Oil (+5% variance)"
        )
        issue_oil = ProductionMaterialIssue(
            production_run_id=prod_run.id,
            material_type="raw",
            raw_material_id=rm_oil.id,
            standard_qty=Decimal("10.00"),
            actual_qty=Decimal("10.50"),
            unit="litre",
            unit_cost=oil_cost,
            total_cost=(Decimal("10.50") * oil_cost).quantize(Decimal("0.01")),
            variance_percent=Decimal("5.00")
        )

        # Tx 5: Issue 1.2 kg spice mix
        spice_cost = Decimal(str(rm_spice.weighted_average_cost))
        InventoryService.record_raw_material_movement(
            db, rm_spice.id, "out", Decimal("1.20"), "production_issue", prod_run.batch_number, prod_run.batch_number, spice_cost, "Production Issue: 1.2 kg Spice Mix"
        )
        issue_spice = ProductionMaterialIssue(
            production_run_id=prod_run.id,
            material_type="raw",
            raw_material_id=rm_spice.id,
            standard_qty=Decimal("1.20"),
            actual_qty=Decimal("1.20"),
            unit="kg",
            unit_cost=spice_cost,
            total_cost=(Decimal("1.20") * spice_cost).quantize(Decimal("0.01")),
            variance_percent=Decimal("0.00")
        )

        # Tx 7: Pouches used: 188 good + 6 damaged = 194 pouches
        pouch_cost = Decimal(str(pm_pouches.unit_cost))
        InventoryService.record_packaging_movement(
            db, pm_pouches.id, "out", Decimal("194.00"), "production_issue", prod_run.batch_number, prod_run.batch_number, pouch_cost, "Production Issue: 188 good + 6 damaged pouches = 194"
        )
        issue_pouch = ProductionMaterialIssue(
            production_run_id=prod_run.id,
            material_type="packaging",
            packaging_material_id=pm_pouches.id,
            standard_qty=Decimal("200.00"),
            actual_qty=Decimal("194.00"),
            unit="piece",
            unit_cost=pouch_cost,
            total_cost=(Decimal("194.00") * pouch_cost).quantize(Decimal("0.01")),
            variance_percent=Decimal("-3.00")
        )

        # Tx 8: 9 cartons used
        carton_cost = Decimal(str(pm_cartons.unit_cost))
        InventoryService.record_packaging_movement(
            db, pm_cartons.id, "out", Decimal("9.00"), "production_issue", prod_run.batch_number, prod_run.batch_number, carton_cost, "Production Issue: 9 Cartons"
        )
        issue_carton = ProductionMaterialIssue(
            production_run_id=prod_run.id,
            material_type="packaging",
            packaging_material_id=pm_cartons.id,
            standard_qty=Decimal("10.00"),
            actual_qty=Decimal("9.00"),
            unit="piece",
            unit_cost=carton_cost,
            total_cost=(Decimal("9.00") * carton_cost).quantize(Decimal("0.01")),
            variance_percent=Decimal("-10.00")
        )

        db.add_all([issue_flour, issue_oil, issue_spice, issue_pouch, issue_carton])
        
        # Tx 6 & 9: Record 188 good packets output into finished goods
        # FG balance becomes 50 (opening) + 188 = 238 packets
        InventoryService.record_product_movement(
            db, product_murukku.id, "in", Decimal("188.00"), "production_receipt", prod_run.batch_number, prod_run.batch_number, Decimal("50.00"), "Production Output: 188 good packets"
        )
        db.flush()

        # ==========================================
        # BENCHMARK TRANSACTION 16:
        # Add ₹1,200 labour and ₹600 gas/power expenses for batch costing
        # ==========================================
        exp_labour = Expense(
            production_run_id=prod_run.id,
            expense_type="labour",
            amount=Decimal("1200.00"),
            description="Production line labour wages (Batch 1)",
            expense_date=datetime.now(timezone.utc)
        )
        exp_power = Expense(
            production_run_id=prod_run.id,
            expense_type="power_gas",
            amount=Decimal("600.00"),
            description="Commercial LPG cylinders & power consumption (Batch 1)",
            expense_date=datetime.now(timezone.utc)
        )
        db.add_all([exp_labour, exp_power])
        db.flush()

        # ==========================================
        # BENCHMARK TRANSACTIONS 9, 10, 11:
        # Salesman A orders 150 packets for Retailer A in Tamil Nadu.
        # Admin approves and generates GST Invoice.
        # Retailer A taxable amount: ₹7,500.
        # CGST (2.5%): ₹187.50. SGST (2.5%): ₹187.50. Invoice total: ₹7,875.
        # ==========================================
        order_a = Order(
            order_number="ORD-2026-0001",
            customer_id=retailer_a.id,
            salesman_id=salesman_a.id,
            status="approved",
            total_amount=Decimal("7500.00"),
            notes="Benchmark Tx 9: Order 150 packets Murukku 200g"
        )
        db.add(order_a)
        db.flush()

        order_a_item = OrderItem(
            order_id=order_a.id,
            product_id=product_murukku.id,
            quantity=Decimal("150.00"),
            unit_price=Decimal("50.00"),
            subtotal=Decimal("7500.00")
        )
        db.add(order_a_item)
        db.flush()

        # Generate GST Invoice for Retailer A (Intrastate TN: CGST + SGST)
        tax_calc = GSTService.calculate_taxes(Decimal("7500.00"), Decimal("5.00"), is_interstate=False)
        inv_number = GSTService.generate_invoice_number(db)
        
        inv_a = Invoice(
            invoice_number=inv_number,
            order_id=order_a.id,
            customer_id=retailer_a.id,
            invoice_date=datetime.now(timezone.utc),
            place_of_supply="Tamil Nadu",
            is_interstate=False,
            taxable_amount=tax_calc["taxable_value"],
            cgst_rate=tax_calc["cgst_rate"],
            cgst_amount=tax_calc["cgst_amount"],
            sgst_rate=tax_calc["sgst_rate"],
            sgst_amount=tax_calc["sgst_amount"],
            igst_rate=tax_calc["igst_rate"],
            igst_amount=tax_calc["igst_amount"],
            total_amount=tax_calc["total_amount"],
            amount_paid=Decimal("0.00"),
            balance_due=tax_calc["total_amount"],
            status="unpaid",
            dispatch_status="pending",
            notes="Benchmark GST Invoice for Retailer A"
        )
        db.add(inv_a)
        db.flush()

        inv_a_item = InvoiceItem(
            invoice_id=inv_a.id,
            product_id=product_murukku.id,
            hsn_code=product_murukku.hsn_code,
            quantity=Decimal("150.00"),
            unit_price=Decimal("50.00"),
            taxable_value=Decimal("7500.00"),
            cgst_rate=tax_calc["cgst_rate"],
            cgst_amount=tax_calc["cgst_amount"],
            sgst_rate=tax_calc["sgst_rate"],
            sgst_amount=tax_calc["sgst_amount"],
            igst_rate=tax_calc["igst_rate"],
            igst_amount=tax_calc["igst_amount"],
            total_item_amount=tax_calc["total_amount"]
        )
        db.add(inv_a_item)
        
        order_a.status = "invoiced"
        retailer_a.balance_outstanding = Decimal(str(retailer_a.balance_outstanding)) + tax_calc["total_amount"]
        db.flush()

        # ==========================================
        # BENCHMARK TRANSACTION 11 & Dispatch:
        # Record dispatch of 150 packets.
        # Finished goods after Retailer A dispatch: 238 - 150 = 88 packets.
        # ==========================================
        InventoryService.record_product_movement(
            db, product_murukku.id, "out", Decimal("150.00"), "dispatch", inv_a.invoice_number, None, Decimal("50.00"), "Dispatch of 150 pkts for Retailer A"
        )
        inv_a.dispatch_status = "dispatched"
        inv_a.dispatched_at = datetime.now(timezone.utc)
        order_a.status = "dispatched"
        db.flush()

        # ==========================================
        # BENCHMARK TRANSACTIONS 12 & 13:
        # Salesman B orders 120 packets for Distributor B in Karnataka.
        # Display insufficient stock of 32 packets.
        # Current stock = 88, Requested = 120 -> Shortage = 32.
        # ==========================================
        order_b = Order(
            order_number="ORD-2026-0002",
            customer_id=distributor_b.id,
            salesman_id=salesman_b.id,
            status="submitted",  # Remains submitted / pending due to stock shortage
            total_amount=Decimal("6000.00"),  # 120 * 50
            notes="Benchmark Tx 12: Order 120 packets Murukku 200g (Karnataka Interstate)"
        )
        db.add(order_b)
        db.flush()

        order_b_item = OrderItem(
            order_id=order_b.id,
            product_id=product_murukku.id,
            quantity=Decimal("120.00"),
            unit_price=Decimal("50.00"),
            subtotal=Decimal("6000.00")
        )
        db.add(order_b_item)
        db.flush()

        # ==========================================
        # BENCHMARK TRANSACTION 14:
        # Record payment of ₹4,000 from Retailer A.
        # Retailer A outstanding balance becomes ₹3,875.
        # ==========================================
        pay1 = Payment(
            payment_number="PAY-2026-0001",
            invoice_id=inv_a.id,
            customer_id=retailer_a.id,
            payment_date=datetime.now(timezone.utc),
            amount=Decimal("4000.00"),
            payment_mode="bank_transfer",
            reference_number="NEFT-SBIN88990011",
            notes="Part payment of ₹4,000 against INV-2026-0001"
        )
        db.add(pay1)
        
        inv_a.amount_paid = Decimal("4000.00")
        inv_a.balance_due = inv_a.total_amount - inv_a.amount_paid
        inv_a.status = "partially_paid"
        retailer_a.balance_outstanding = retailer_a.balance_outstanding - Decimal("4000.00")
        db.flush()

        # Commit all transactions atomically
        db.commit()

        # ==========================================
        # VERIFICATION & AUDIT COMPILATION
        # ==========================================
        # Refresh entities from DB
        db.refresh(rm_flour)
        db.refresh(rm_oil)
        db.refresh(rm_spice)
        db.refresh(pm_pouches)
        db.refresh(pm_cartons)
        db.refresh(product_murukku)
        db.refresh(retailer_a)
        db.refresh(inv_a)

        costing = CostingService.calculate_production_run_costing(db, prod_run.id)
        
        fg_stock_now = Decimal(str(product_murukku.current_stock))
        requested_b = Decimal("120.00")
        dist_b_shortage = requested_b - fg_stock_now if fg_stock_now < requested_b else Decimal("0.00")

        return {
            "status": "success",
            "message": "Benchmark scenario executed and verified successfully.",
            "closing_balances": {
                "flour_kg": Decimal(str(rm_flour.current_stock)).quantize(Decimal("0.01")),
                "flour_expected": Decimal("120.00"),
                "flour_weighted_cost": Decimal(str(rm_flour.weighted_average_cost)).quantize(Decimal("0.0001")),
                
                "oil_litres": Decimal(str(rm_oil.current_stock)).quantize(Decimal("0.01")),
                "oil_expected": Decimal("19.50"),
                
                "spice_mix_kg": Decimal(str(rm_spice.current_stock)).quantize(Decimal("0.01")),
                "spice_mix_expected": Decimal("3.80"),
                
                "pouches_pcs": Decimal(str(pm_pouches.current_stock)).quantize(Decimal("0.00")),
                "pouches_expected": Decimal("306.00"),
                
                "cartons_pcs": Decimal(str(pm_cartons.current_stock)).quantize(Decimal("0.00")),
                "cartons_expected": Decimal("21.00"),
                
                "finished_goods_pkts": fg_stock_now.quantize(Decimal("0.00")),
                "finished_goods_expected_after_dispatch": Decimal("88.00"),
                "finished_goods_after_production": Decimal("238.00")
            },
            "production_variances": {
                "yield_variance_percent": Decimal(str(prod_run.yield_variance_percent)),
                "yield_variance_expected": Decimal("-6.00"),
                "oil_variance_percent": Decimal(str(prod_run.oil_variance_percent)),
                "oil_variance_expected": Decimal("5.00"),
                "variance_alert_flagged": bool(prod_run.is_variance_alert)
            },
            "retailer_a_gst_invoice": {
                "invoice_number": inv_a.invoice_number,
                "taxable_amount": Decimal(str(inv_a.taxable_amount)),
                "taxable_expected": Decimal("7500.00"),
                "cgst_amount": Decimal(str(inv_a.cgst_amount)),
                "cgst_expected": Decimal("187.50"),
                "sgst_amount": Decimal(str(inv_a.sgst_amount)),
                "sgst_expected": Decimal("187.50"),
                "total_amount": Decimal(str(inv_a.total_amount)),
                "total_expected": Decimal("7875.00"),
                "amount_paid": Decimal(str(inv_a.amount_paid)),
                "amount_paid_expected": Decimal("4000.00"),
                "outstanding_balance": Decimal(str(retailer_a.balance_outstanding)),
                "outstanding_expected": Decimal("3875.00")
            },
            "distributor_b_shortage": {
                "requested_quantity": requested_b,
                "available_stock": fg_stock_now,
                "shortage_quantity": dist_b_shortage,
                "shortage_expected": Decimal("32.00")
            },
            "unit_costing": costing
        }

