const API_BASE = 'http://localhost:8000/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const err = await response.json();
      errorDetail = err.detail || JSON.stringify(err);
    } catch {
      errorDetail = await response.text();
    }
    throw new Error(errorDetail);
  }

  // Handle binary downloads or empty responses
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return response.json();
  }
  return response.blob() as unknown as T;
}

export const api = {
  // Auth
  login: (data: any) => request<any>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => request<any>('/auth/me'),
  getDemoUsers: () => request<any[]>('/auth/demo-users'),

  // Dashboards
  getOwnerDashboard: () => request<any>('/dashboard/owner'),
  getSalesmanDashboard: () => request<any>('/dashboard/salesman'),

  // Customers & Suppliers
  getCustomers: () => request<any[]>('/customers'),
  createCustomer: (data: any) => request<any>('/customers', { method: 'POST', body: JSON.stringify(data) }),
  getSuppliers: () => request<any[]>('/purchases/suppliers'),
  createSupplier: (data: any) => request<any>('/purchases/suppliers', { method: 'POST', body: JSON.stringify(data) }),

  // Products & Materials
  getProducts: () => request<any[]>('/products'),
  createProduct: (data: any) => request<any>('/products', { method: 'POST', body: JSON.stringify(data) }),
  getRawMaterials: () => request<any[]>('/materials/raw'),
  createRawMaterial: (data: any) => request<any>('/materials/raw', { method: 'POST', body: JSON.stringify(data) }),
  getPackagingMaterials: () => request<any[]>('/materials/packaging'),
  createPackagingMaterial: (data: any) => request<any>('/materials/packaging', { method: 'POST', body: JSON.stringify(data) }),

  // BOM
  getBOMs: () => request<any[]>('/bom'),
  createBOM: (data: any) => request<any>('/bom', { method: 'POST', body: JSON.stringify(data) }),

  // Orders
  getOrders: () => request<any[]>('/orders'),
  createOrder: (data: any) => request<any>('/orders', { method: 'POST', body: JSON.stringify(data) }),
  checkOrderStock: (orderId: number) => request<any>(`/orders/${orderId}/stock-check`),
  decideOrder: (orderId: number, data: { action: string; rejection_reason?: string }) =>
    request<any>(`/orders/${orderId}/decision`, { method: 'POST', body: JSON.stringify(data) }),

  // Invoices & Dispatch
  getInvoices: () => request<any[]>('/invoices'),
  generateInvoice: (orderId: number) => request<any>(`/invoices/generate-from-order/${orderId}`, { method: 'POST' }),
  dispatchInvoice: (invoiceId: number) => request<any>(`/invoices/${invoiceId}/dispatch`, { method: 'POST' }),
  getInvoicePdfUrl: (invoiceId: number) => `${API_BASE}/invoices/${invoiceId}/pdf`,

  // Production & Variance
  getProductionRuns: () => request<any[]>('/production'),
  createProductionRun: (data: any) => request<any>('/production', { method: 'POST', body: JSON.stringify(data) }),
  getVarianceAlerts: () => request<any[]>('/production/variance-alerts'),

  // Inventory & Ledger
  getStockDashboard: () => request<any>('/inventory/dashboard'),
  getStockLedger: (itemType?: string, docType?: string) => {
    const params = new URLSearchParams();
    if (itemType) params.append('item_type', itemType);
    if (docType) params.append('source_document_type', docType);
    return request<any[]>(`/inventory/ledger?${params.toString()}`);
  },

  // Purchases
  getPurchases: () => request<any[]>('/purchases'),
  createPurchase: (data: any) => request<any>('/purchases', { method: 'POST', body: JSON.stringify(data) }),

  // Costing
  getAllBatchCostings: () => request<any[]>('/costing/all-batches'),
  getBatchCosting: (batchId: number) => request<any>(`/costing/batch/${batchId}`),

  // Payments
  getPayments: () => request<any[]>('/payments'),
  recordPayment: (data: any) => request<any>('/payments', { method: 'POST', body: JSON.stringify(data) }),

  // Reports & Exports
  getSalesSummary: () => request<any>('/reports/sales-summary'),
  getGSTR1: () => request<any>('/reports/gst-gstr1'),
  getStockLedgerCsvUrl: () => `${API_BASE}/reports/export/stock-ledger-csv`,
  getProductionExcelUrl: () => `${API_BASE}/reports/export/production-excel`,

  // Benchmark
  runBenchmark: () => request<any>('/benchmark/run', { method: 'POST' }),
  getBenchmarkStatus: () => request<any>('/benchmark/status'),
};

