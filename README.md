# FOOD MANUFACTURING ORDER-TO-AUDIT MANAGEMENT SYSTEM
### Integrated ERP for Small-Scale South Indian Food Manufacturing
**Problem Statement**: "Order-to-Audit System for a Small Food Manufacturer" – Centre for Digital Infrastructure, NIT Tiruchirappalli.

---

## 1. Executive Summary

This enterprise web application provides an end-to-end, integrated management system for a small-scale packaged food manufacturer producing **Murukku (200g), Mixture, Chips, and Sweets**. 

Every business event is entered once and automatically cascades across modules:
$$\text{Salesman Order} \rightarrow \text{Admin Verification} \rightarrow \text{GST Tax Invoice} \rightarrow \text{Physical Dispatch} \rightarrow \text{Finished Goods Stock} \rightarrow \text{Production BOM} \rightarrow \text{Raw Material Stock} \rightarrow \text{Batch Costing} \rightarrow \text{Customer Receivables} \rightarrow \text{Statutory Audit Reports}$$

### Core Technical Highlights:
- **Transaction-Based Stock Ledger**: Implements double-entry inventory ledger movements (`in` / `out`) tied to immutable source documents (`purchase`, `production_issue`, `production_receipt`, `dispatch`). Direct manual overwriting of stock balances is forbidden by schema design.
- **Production Variance & Yield Engine**: Dynamic recipe calculation with automatic threshold flagging whenever yield variance or ingredient consumption deviates beyond **3.0%**.
- **Statutory GST Tax Engine**: Automatic identification of intra-state transactions (Tamil Nadu $\rightarrow$ Tamil Nadu: **2.5% CGST + 2.5% SGST**) vs inter-state transactions (Tamil Nadu $\rightarrow$ Karnataka: **5.0% IGST**) with HSN `21069099` support and downloadable ReportLab PDF invoices.
- **Weighted-Average Inventory Valuation (WAC)**: Continuous automatic recalibration of raw material unit valuation whenever inward purchase orders arrive.
- **Unit Economics & Costing Engine**: Absorbs raw materials, packaging materials, direct labour wages, and commercial power/gas expenses to compute true manufacturing cost per good packet and gross profit margins.

---

## 2. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React icons, Recharts (analytics & operational trends).
- **Backend**: Python 3.11+ / 3.13, FastAPI (high-performance REST APIs), Pydantic v2 (strict validation), SQLAlchemy 2.0 (normalized ORM).
- **Database**: PostgreSQL (Supabase / local PostgreSQL) with standard dialect-agnostic support and local SQLite zero-dependency fallback for instant development.
- **Authentication**: JWT tokens, bcrypt password hashing, role-based access control (RBAC).
- **Document Engines**: ReportLab (vector PDF GST invoices & audit summaries), Pandas & OpenPyXL (Excel & CSV export).

---

## 3. Demo User Accounts (5 Roles)

The application provides instant 1-click role switching in the navigation header, as well as password authentication (`password123` for all accounts):

| Role | Name | Email | Primary Responsibilities |
|---|---|---|---|
| **Owner** | Sundaram Ramakrishnan | `owner@fooderp.com` | 360° analytics, sales trends, stock health, variance alerts, gross profit margins. |
| **Admin** | Meenakshi Sundaram | `admin@fooderp.com` | Verify orders, approve/reject, generate GST invoices, dispatch, log payments, manage vendors. |
| **Salesman A** | Karthik Raj | `salesman.a@fooderp.com` | Mobile order booking (Tamil Nadu territory - Retailer A), live stock check. |
| **Salesman B** | Venkatesh Iyer | `salesman.b@fooderp.com` | Mobile order booking (Karnataka territory - Distributor B), shortage detection. |
| **Production Supervisor**| Muthukumar S. | `supervisor@fooderp.com` | Manage BOM recipes, log batch runs, record damaged pouches, monitor yield variances. |
| **Auditor / Accountant** | Ranganathan FCA | `auditor@fooderp.com` | Read-only ledger, GSTR-1 tax compliance, balance reconciliation, Excel/CSV audit export. |

---

## 4. Benchmark Execution & Verification (NIT Trichy Problem Statement)

The system includes a dedicated **1-Click Benchmark Runner** that executes and verifies the 16 exact transactions specified in the assignment:

```
Product: Murukku 200 g | Selling Price: ₹50.00 pre-GST | GST Rate: 5% (HSN: 21069099)
Opening Inventory: Flour: 100 kg (@ ₹42/kg), Cooking Oil: 30 L (@ ₹140/L), Spices: 5 kg (@ ₹200/kg), Pouches: 500 pcs (@ ₹2.50), Cartons: 30 pcs (@ ₹15), Murukku: 50 pkts
Standard BOM (200 pkts): Flour: 40 kg, Oil: 10 L, Spices: 1.2 kg, Pouches: 200 pcs, Cartons: 10 pcs
```

### Exact Results Comparison:

| Metric | Target Specification | System Result | Status |
|---|:---:|:---:|:---:|
| **Flour Closing Balance** | 120.00 kg | **120.00 kg** | ✅ Verified |
| **Flour Weighted Average Cost** | ₹43.125 / kg | **₹43.125 / kg** | ✅ Verified |
| **Cooking Oil Closing Balance** | 19.50 L | **19.50 L** | ✅ Verified |
| **Spice Mix Closing Balance** | 3.80 kg | **3.80 kg** | ✅ Verified |
| **200g Pouches Closing Balance** | 306 pcs | **306 pcs** | ✅ Verified |
| **Cartons Closing Balance** | 21 pcs | **21 pcs** | ✅ Verified |
| **Finished Goods (Post-Production)** | 238 packets | **238 packets** | ✅ Verified |
| **Finished Goods (Post-Dispatch)** | 88 packets | **88 packets** | ✅ Verified |
| **Production Yield Variance** | -6.00 % | **-6.00 %** (>3% Alert) | ✅ Verified |
| **Cooking Oil Variance** | +5.00 % | **+5.00 %** (>3% Alert) | ✅ Verified |
| **Retailer A Taxable Amount** | ₹7,500.00 | **₹7,500.00** | ✅ Verified |
| **Tamil Nadu CGST (2.5%)** | ₹187.50 | **₹187.50** | ✅ Verified |
| **Tamil Nadu SGST (2.5%)** | ₹187.50 | **₹187.50** | ✅ Verified |
| **Retailer A Invoice Grand Total** | ₹7,875.00 | **₹7,875.00** | ✅ Verified |
| **Retailer A Outstanding Balance**| ₹3,875.00 | **₹3,875.00** (after ₹4k pay) | ✅ Verified |
| **Distributor B Stock Shortage** | 32 packets shortage | **32 packets shortage** | ✅ Verified |
| **Batch Cost Per Good Packet** | ₹31.14 | **₹31.14** | ✅ Verified |
| **Gross Profit Margin** | ₹18.86 / 37.71% | **₹18.86 / 37.71%** | ✅ Verified |

---

## 5. Quickstart & Local Execution

### Backend (Python FastAPI)
```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Run automated test suite (all 9 unit tests)
python -m pytest tests -v

# 4. Start the FastAPI development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation will be available at: `http://localhost:8000/api/v1/docs`

### Frontend (React + Vite + TypeScript)
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Build & verify TypeScript compilation
npm run build

# 4. Start the Vite dev server
npm run dev
```
Open your browser at `http://localhost:5173` to explore the ERP application.

---

## 6. Project Architecture & Documentation

- [System Design Note & ER Diagram](docs/DESIGN_NOTE_AND_ERD.md)
- [16-Step Benchmark Verification Audit](docs/BENCHMARK_VERIFICATION.md)
- [Production Deployment Guide](docs/DEPLOYMENT.md)

