from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal

from backend.app.api.deps import get_db, get_current_user, require_roles
from backend.app.models.order import Order, OrderItem
from backend.app.models.customer import Customer
from backend.app.models.product import Product
from backend.app.models.user import User, UserRole
from backend.app.schemas.order import OrderCreate, OrderResponse, OrderApproveReject

router = APIRouter()

@router.get("", response_model=List[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Order).order_by(Order.id.desc())
    
    # If salesman, only see own orders
    user_role_str = str(current_user.role.value if hasattr(current_user.role, "value") else current_user.role)
    if user_role_str == "salesman":
        query = query.filter(Order.salesman_id == current_user.id)
        
    orders = query.all()
    results = []
    for ord in orders:
        items = []
        for itm in ord.items:
            items.append({
                "id": itm.id,
                "product_id": itm.product_id,
                "product_name": itm.product.name if itm.product else None,
                "quantity": itm.quantity,
                "unit_price": itm.unit_price,
                "subtotal": itm.subtotal
            })
        results.append({
            "id": ord.id,
            "order_number": ord.order_number,
            "customer_id": ord.customer_id,
            "customer_name": ord.customer.name if ord.customer else None,
            "salesman_id": ord.salesman_id,
            "salesman_name": ord.salesman.full_name if ord.salesman else None,
            "order_date": ord.order_date,
            "status": ord.status,
            "total_amount": ord.total_amount,
            "notes": ord.notes,
            "rejection_reason": ord.rejection_reason,
            "items": items,
            "created_at": ord.created_at
        })
    return results

@router.post("", response_model=OrderResponse)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.id == order_in.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not order_in.items:
        raise HTTPException(status_code=400, detail="Order must have at least one product item")

    # Generate Order Number: ORD-YYYY-XXXX
    year = datetime.now(timezone.utc).year
    prefix = f"ORD-{year}-"
    last_order = db.query(Order).filter(Order.order_number.like(f"{prefix}%")).order_by(Order.id.desc()).first()
    next_seq = 1
    if last_order:
        try:
            next_seq = int(last_order.order_number.split("-")[-1]) + 1
        except Exception:
            next_seq = 1
    order_number = f"{prefix}{next_seq:04d}"

    total_amount = Decimal("0.00")
    order = Order(
        order_number=order_number,
        customer_id=customer.id,
        salesman_id=current_user.id,
        status="submitted",
        total_amount=Decimal("0.00"),
        notes=order_in.notes
    )
    db.add(order)
    db.flush()

    order_items = []
    for itm in order_in.items:
        product = db.query(Product).filter(Product.id == itm.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {itm.product_id} not found")
        
        price = Decimal(str(itm.unit_price)) if itm.unit_price is not None else Decimal(str(product.selling_price))
        qty = Decimal(str(itm.quantity))
        subtotal = qty * price
        total_amount += subtotal

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            unit_price=price,
            subtotal=subtotal
        )
        db.add(order_item)
        order_items.append(order_item)

    order.total_amount = total_amount
    db.commit()
    db.refresh(order)

    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_id": order.customer_id,
        "customer_name": customer.name,
        "salesman_id": order.salesman_id,
        "salesman_name": current_user.full_name,
        "order_date": order.order_date,
        "status": order.status,
        "total_amount": order.total_amount,
        "notes": order.notes,
        "rejection_reason": None,
        "items": [
            {
                "id": itm.id,
                "product_id": itm.product_id,
                "product_name": itm.product.name if itm.product else None,
                "quantity": itm.quantity,
                "unit_price": itm.unit_price,
                "subtotal": itm.subtotal
            }
            for itm in order.items
        ],
        "created_at": order.created_at
    }

@router.get("/{order_id}/stock-check")
def check_order_stock(order_id: int, db: Session = Depends(get_db)):
    """
    Checks available stock for every line item in the order.
    Returns available vs requested, shortage, and status flag.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    stock_status = []
    has_shortage = False

    for itm in order.items:
        product = itm.product
        available = Decimal(str(product.current_stock))
        requested = Decimal(str(itm.quantity))
        shortage = requested - available if available < requested else Decimal("0.00")
        is_sufficient = available >= requested
        if not is_sufficient:
            has_shortage = True

        stock_status.append({
            "product_id": product.id,
            "product_name": product.name,
            "requested_quantity": requested,
            "available_stock": available,
            "shortage": shortage,
            "is_sufficient": is_sufficient
        })

    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "has_shortage": has_shortage,
        "items": stock_status
    }

@router.post("/{order_id}/decision")
def approve_or_reject_order(
    order_id: int,
    decision: OrderApproveReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "owner"]))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if decision.action.lower() == "approve":
        order.status = "approved"
        order.rejection_reason = None
    elif decision.action.lower() == "reject":
        order.status = "rejected"
        order.rejection_reason = decision.rejection_reason or "Rejected by Admin"
    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    db.commit()
    return {"message": f"Order {order.order_number} marked as {order.status}", "status": order.status}

