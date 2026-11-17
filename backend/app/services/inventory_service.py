from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.models.material import RawMaterial, PackagingMaterial
from backend.app.models.product import Product
from backend.app.models.inventory import StockMovement

class InventoryService:
    @staticmethod
    def record_raw_material_movement(
        db: Session,
        raw_material_id: int,
        movement_type: str,  # "in" or "out"
        quantity: Decimal,
        source_document_type: str,
        source_document_id: Optional[str] = None,
        batch_number: Optional[str] = None,
        unit_cost: Optional[Decimal] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = "System"
    ) -> StockMovement:
        rm = db.query(RawMaterial).filter(RawMaterial.id == raw_material_id).first()
        if not rm:
            raise ValueError(f"Raw material with ID {raw_material_id} not found")

        qty = Decimal(str(quantity))
        curr_stock = Decimal(str(rm.current_stock))
        
        if movement_type == "in":
            new_stock = curr_stock + qty
            # Update weighted average cost if unit_cost is provided and new_stock > 0
            if unit_cost is not None and qty > 0:
                cost = Decimal(str(unit_cost))
                if curr_stock <= 0:
                    rm.weighted_average_cost = cost
                else:
                    curr_val = curr_stock * Decimal(str(rm.weighted_average_cost))
                    in_val = qty * cost
                    rm.weighted_average_cost = (curr_val + in_val) / new_stock
        elif movement_type == "out":
            if curr_stock < qty:
                raise ValueError(f"Insufficient stock for {rm.name}: available {curr_stock}, requested {qty}")
            new_stock = curr_stock - qty
        else:
            raise ValueError(f"Invalid movement type: {movement_type}")

        rm.current_stock = new_stock
        actual_unit_cost = Decimal(str(unit_cost)) if unit_cost is not None else Decimal(str(rm.weighted_average_cost))

        movement = StockMovement(
            item_type="raw",
            raw_material_id=rm.id,
            movement_type=movement_type,
            quantity=qty,
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            batch_number=batch_number,
            unit_cost=actual_unit_cost,
            running_balance=new_stock,
            notes=notes,
            created_by=created_by
        )
        db.add(movement)
        db.flush()
        return movement

    @staticmethod
    def record_packaging_movement(
        db: Session,
        packaging_material_id: int,
        movement_type: str,  # "in" or "out"
        quantity: Decimal,
        source_document_type: str,
        source_document_id: Optional[str] = None,
        batch_number: Optional[str] = None,
        unit_cost: Optional[Decimal] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = "System"
    ) -> StockMovement:
        pm = db.query(PackagingMaterial).filter(PackagingMaterial.id == packaging_material_id).first()
        if not pm:
            raise ValueError(f"Packaging material with ID {packaging_material_id} not found")

        qty = Decimal(str(quantity))
        curr_stock = Decimal(str(pm.current_stock))

        if movement_type == "in":
            new_stock = curr_stock + qty
            if unit_cost is not None and qty > 0:
                cost = Decimal(str(unit_cost))
                if curr_stock <= 0:
                    pm.unit_cost = cost
                else:
                    curr_val = curr_stock * Decimal(str(pm.unit_cost))
                    in_val = qty * cost
                    pm.unit_cost = (curr_val + in_val) / new_stock
        elif movement_type == "out":
            if curr_stock < qty:
                raise ValueError(f"Insufficient stock for {pm.name}: available {curr_stock}, requested {qty}")
            new_stock = curr_stock - qty
        else:
            raise ValueError(f"Invalid movement type: {movement_type}")

        pm.current_stock = new_stock
        actual_cost = Decimal(str(unit_cost)) if unit_cost is not None else Decimal(str(pm.unit_cost))

        movement = StockMovement(
            item_type="packaging",
            packaging_material_id=pm.id,
            movement_type=movement_type,
            quantity=qty,
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            batch_number=batch_number,
            unit_cost=actual_cost,
            running_balance=new_stock,
            notes=notes,
            created_by=created_by
        )
        db.add(movement)
        db.flush()
        return movement

    @staticmethod
    def record_product_movement(
        db: Session,
        product_id: int,
        movement_type: str,  # "in" or "out"
        quantity: Decimal,
        source_document_type: str,
        source_document_id: Optional[str] = None,
        batch_number: Optional[str] = None,
        unit_cost: Optional[Decimal] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = "System"
    ) -> StockMovement:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

        qty = Decimal(str(quantity))
        curr_stock = Decimal(str(product.current_stock))

        if movement_type == "in":
            new_stock = curr_stock + qty
        elif movement_type == "out":
            if curr_stock < qty:
                raise ValueError(f"Insufficient finished goods stock for {product.name}: available {curr_stock}, requested {qty}")
            new_stock = curr_stock - qty
        else:
            raise ValueError(f"Invalid movement type: {movement_type}")

        product.current_stock = new_stock
        cost = Decimal(str(unit_cost)) if unit_cost is not None else Decimal(str(product.selling_price))

        movement = StockMovement(
            item_type="finished_good",
            product_id=product.id,
            movement_type=movement_type,
            quantity=qty,
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            batch_number=batch_number,
            unit_cost=cost,
            running_balance=new_stock,
            notes=notes,
            created_by=created_by
        )
        db.add(movement)
        db.flush()
        return movement
