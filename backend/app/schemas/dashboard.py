from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from decimal import Decimal

class OwnerDashboardResponse(BaseModel):
    total_sales_mtd: Decimal
    total_invoiced_mtd: Decimal
    total_collections_mtd: Decimal
    total_outstanding_ar: Decimal
    finished_goods_packets: Decimal
    active_variance_alerts_count: int
    recent_batches_count: int
    low_stock_items_count: int
    sales_trend: List[Dict[str, Any]]
    category_distribution: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]
    recent_batches: List[Dict[str, Any]]

class SalesmanDashboardResponse(BaseModel):
    salesman_name: str
    total_orders_count: int
    total_sales_value: Decimal
    pending_orders_count: int
    approved_orders_count: int
    customers: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]

