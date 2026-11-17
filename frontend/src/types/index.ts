export type UserRole = 'owner' | 'admin' | 'salesman' | 'production' | 'auditor';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string;
  is_active: boolean;
}

export interface Customer {
  id: number;
  name: string;
  code: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  billing_address?: string;
  shipping_address?: string;
  state: string;
  state_code: string;
  gstin?: string;
  credit_limit: number;
  balance_outstanding: number;
  is_active: boolean;
}

export interface Product {
  id: number;
  name: string;
  sku: string;
  category: string;
  unit: string;
  weight_grams: number;
  hsn_code: string;
  selling_price: number;
  gst_rate: number;
  current_stock: number;
  reorder_level: number;
  is_active: boolean;
}

export interface RawMaterial {
  id: number;
  name: string;
  code: string;
  unit: string;
  current_stock: number;
  reorder_level: number;
  weighted_average_cost: number;
  is_active: boolean;
}

export interface PackagingMaterial {
  id: number;
  name: string;
  code: string;
  unit: string;
  current_stock: number;
  reorder_level: number;
  unit_cost: number;
  is_active: boolean;
}

export interface OrderItem {
  id?: number;
  product_id: number;
  product_name?: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface Order {
  id: number;
  order_number: string;
  customer_id: number;
  customer_name?: string;
  salesman_id: number;
  salesman_name?: string;
  order_date: string;
  status: 'draft' | 'submitted' | 'approved' | 'rejected' | 'invoiced' | 'dispatched' | 'cancelled';
  total_amount: number;
  notes?: string;
  rejection_reason?: string;
  items: OrderItem[];
  created_at: string;
}

export interface InvoiceItem {
  id: number;
  product_id: number;
  product_name?: string;
  hsn_code: string;
  quantity: number;
  unit_price: number;
  taxable_value: number;
  cgst_rate: number;
  cgst_amount: number;
  sgst_rate: number;
  sgst_amount: number;
  igst_rate: number;
  igst_amount: number;
  total_item_amount: number;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  order_id?: number;
  customer_id: number;
  customer_name?: string;
  invoice_date: string;
  due_date?: string;
  place_of_supply: string;
  is_interstate: boolean;
  taxable_amount: number;
  cgst_rate: number;
  cgst_amount: number;
  sgst_rate: number;
  sgst_amount: number;
  igst_rate: number;
  igst_amount: number;
  total_amount: number;
  amount_paid: number;
  balance_due: number;
  status: 'unpaid' | 'partially_paid' | 'paid' | 'cancelled';
  dispatch_status: 'pending' | 'dispatched';
  dispatched_at?: string;
  notes?: string;
  items: InvoiceItem[];
  created_at: string;
}

export interface ProductionMaterialIssue {
  id: number;
  material_type: 'raw' | 'packaging';
  material_name?: string;
  standard_qty: number;
  actual_qty: number;
  unit: string;
  unit_cost: number;
  total_cost: number;
  variance_percent: number;
}

export interface ProductionRun {
  id: number;
  batch_number: string;
  product_id: number;
  product_name?: string;
  planned_quantity: number;
  actual_good_quantity: number;
  damaged_quantity: number;
  cartons_used: number;
  yield_variance_percent: number;
  oil_variance_percent: number;
  is_variance_alert: number;
  status: string;
  supervisor_name?: string;
  start_time: string;
  end_time?: string;
  notes?: string;
  material_issues: ProductionMaterialIssue[];
  created_at: string;
}

export interface StockMovement {
  id: number;
  timestamp: string;
  item_type: 'raw' | 'packaging' | 'finished_good';
  item_name?: string;
  item_code?: string;
  movement_type: 'in' | 'out';
  quantity: number;
  source_document_type: string;
  source_document_id?: string;
  batch_number?: string;
  unit_cost: number;
  running_balance: number;
  notes?: string;
  created_by?: string;
}

export interface StockSummaryItem {
  id: number;
  name: string;
  code: string;
  category?: string;
  unit: string;
  current_stock: number;
  reorder_level: number;
  unit_valuation: number;
  total_valuation: number;
  is_low_stock: boolean;
}

export interface StockDashboard {
  raw_materials: StockSummaryItem[];
  packaging_materials: StockSummaryItem[];
  finished_goods: StockSummaryItem[];
  total_raw_valuation: number;
  total_packaging_valuation: number;
  total_fg_valuation: number;
  total_inventory_valuation: number;
}

export interface Payment {
  id: number;
  payment_number: string;
  invoice_id?: number;
  invoice_number?: string;
  customer_id: number;
  customer_name?: string;
  payment_date: string;
  amount: number;
  payment_mode: string;
  reference_number?: string;
  notes?: string;
  created_at: string;
}

export interface Supplier {
  id: number;
  name: string;
  code: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  state: string;
  gstin?: string;
  is_active: boolean;
}

export interface BenchmarkReport {
  status: string;
  message: string;
  closing_balances: {
    flour_kg: number;
    flour_expected: number;
    flour_weighted_cost: number;
    oil_litres: number;
    oil_expected: number;
    spice_mix_kg: number;
    spice_mix_expected: number;
    pouches_pcs: number;
    pouches_expected: number;
    cartons_pcs: number;
    cartons_expected: number;
    finished_goods_pkts: number;
    finished_goods_expected_after_dispatch: number;
    finished_goods_after_production: number;
  };
  production_variances: {
    yield_variance_percent: number;
    yield_variance_expected: number;
    oil_variance_percent: number;
    oil_variance_expected: number;
    variance_alert_flagged: boolean;
  };
  retailer_a_gst_invoice: {
    invoice_number: string;
    taxable_amount: number;
    taxable_expected: number;
    cgst_amount: number;
    cgst_expected: number;
    sgst_amount: number;
    sgst_expected: number;
    total_amount: number;
    total_expected: number;
    amount_paid: number;
    amount_paid_expected: number;
    outstanding_balance: number;
    outstanding_expected: number;
  };
  distributor_b_shortage: {
    requested_quantity: number;
    available_stock: number;
    shortage_quantity: number;
    shortage_expected: number;
  };
  unit_costing: {
    batch_number: string;
    product_name: string;
    planned_quantity: number;
    actual_good_quantity: number;
    damaged_quantity: number;
    yield_variance_percent: number;
    oil_variance_percent: number;
    is_variance_alert: boolean;
    raw_material_cost: number;
    packaging_cost: number;
    labour_cost: number;
    power_gas_cost: number;
    other_overhead: number;
    total_batch_cost: number;
    cost_per_good_packet: number;
    selling_price: number;
    gross_margin_per_packet: number;
    gross_margin_percent: number;
  };
}

