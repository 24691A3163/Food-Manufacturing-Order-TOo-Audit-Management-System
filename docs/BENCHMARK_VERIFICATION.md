# BENCHMARK VERIFICATION SPECIFICATION
## Centre for Digital Infrastructure, NIT Tiruchirappalli Internship Problem Statement

---

### Benchmark Product Baseline
- **Product**: Murukku 200 g
- **Selling Price**: ₹50.00 per packet (pre-GST)
- **GST Rate**: 5.0% (HSN: 21069099)
- **Opening Inventory**:
  - Flour: 100 kg (@ ₹42.00 opening valuation)
  - Cooking oil: 30 litres (@ ₹140.00/litre)
  - Salt and spice mix: 5 kg (@ ₹200.00/kg)
  - 200 g pouches: 500 pieces (@ ₹2.50 each)
  - Cartons: 30 pieces (@ ₹15.00 each)
  - Finished Murukku: 50 packets

---

### Step-by-Step Execution & Audit Breakdown

| Step # | Operation Executed | Input Parameters | System Mathematical Computation | Closing Result | Verification Status |
|:---:|:---|:---|:---|:---|:---:|
| **1** | Purchase Flour | 60 kg @ ₹45/kg from Madurai Agro Mills | Weighted Average: $\frac{(100 \times 42) + (60 \times 45)}{160} = \frac{4200 + 2700}{160} = \mathbf{₹43.125/\text{kg}}$ | Flour balance: **160 kg** | ✅ VERIFIED |
| **2** | Initiate Production Run | Standard BOM for 200 pkts | Standard requirements loaded: Flour 40kg, Oil 10L, Spices 1.2kg, Pouches 200, Cartons 10 | Status: In-Progress | ✅ VERIFIED |
| **3** | Issue Flour to Batch | 40 kg Flour | $160\text{ kg} - 40\text{ kg} = \mathbf{120.00\text{ kg}}$ | Flour balance: **120 kg** | ✅ VERIFIED |
| **4** | Issue Cooking Oil | 10.50 L Cooking Oil | $30\text{ L} - 10.5\text{ L} = \mathbf{19.50\text{ L}}$. Oil Variance: $\frac{10.5 - 10.0}{10.0} \times 100 = \mathbf{+5.00\%}$ | Oil balance: **19.5 L** | ✅ VERIFIED |
| **5** | Issue Salt & Spice Mix | 1.20 kg Spice Mix | $5.0\text{ kg} - 1.2\text{ kg} = \mathbf{3.80\text{ kg}}$ | Spice balance: **3.8 kg** | ✅ VERIFIED |
| **6** | Record Good Packets Output | 188 Good Packets | Yield Variance: $\frac{188 - 200}{200} \times 100 = \mathbf{-6.00\%}$. Flagged alert (exceeds 3.0%) | FG Stock: $50 + 188 = \mathbf{238\text{ pkts}}$ | ✅ VERIFIED |
| **7** | Record Damaged Pouches | 6 Damaged Pouches | Total Pouches Consumed: $188\text{ good} + 6\text{ damaged} = 194\text{ pcs}$. Balance: $500 - 194 = \mathbf{306\text{ pcs}}$ | Pouches balance: **306 pcs** | ✅ VERIFIED |
| **8** | Record Cartons Consumed | 9 Cartons Used | $30\text{ pcs} - 9\text{ pcs} = \mathbf{21\text{ pcs}}$ | Cartons balance: **21 pcs** | ✅ VERIFIED |
| **9** | Salesman A Books Order | 150 pkts for Retailer A (TN) | Stock Available: 238 pkts. Order Approved. | Order: ORD-2026-0001 | ✅ VERIFIED |
| **10** | Admin Generates GST Invoice | Retailer A (Tamil Nadu) | Taxable: $150 \times 50 = \mathbf{₹7,500.00}$. CGST (2.5%): $\mathbf{₹187.50}$. SGST (2.5%): $\mathbf{₹187.50}$. Grand Total: $\mathbf{₹7,875.00}$ | Invoice: INV-2026-0001 | ✅ VERIFIED |
| **11** | Record Physical Dispatch | 150 pkts dispatched to Retailer A | $238\text{ pkts} - 150\text{ pkts} = \mathbf{88\text{ packets}}$ remaining in warehouse | FG Stock: **88 pkts** | ✅ VERIFIED |
| **12** | Salesman B Books Order | 120 pkts for Distributor B (KA) | State: Karnataka (Interstate IGST 5%). Requested: 120 pkts | Order: ORD-2026-0002 | ✅ VERIFIED |
| **13** | Stock Check & Shortage | Stock Check for Distributor B | Available: 88 pkts. Requested: 120 pkts. $\text{Shortage} = 120 - 88 = \mathbf{32\text{ packets}}$ | Shortage: **32 packets** | ✅ VERIFIED |
| **14** | Record Customer Payment | Retailer A pays ₹4,000 | Balance Outstanding: $₹7,875.00 - ₹4,000.00 = \mathbf{₹3,875.00}$ | Outstanding: **₹3,875.00** | ✅ VERIFIED |
| **15** | Record Direct Expenses | Direct Labour: ₹1,200, Power/Gas: ₹600 | Total Direct Expenses: $₹1,200 + ₹600 = \mathbf{₹1,800.00}$ | Expenses Logged | ✅ VERIFIED |
| **16** | Batch Costing & Final Audit | Batch 1 Absorption Costing | RM: ₹3,435 + PM: ₹620 + Labour: ₹1,200 + Power: ₹600 = ₹5,855. $\frac{5855}{188} = \mathbf{₹31.14/\text{pkt}}$. Margin: $\mathbf{37.71\%}$ | Costing Verified | ✅ VERIFIED |

---

### Automated Verification Command
To verify the entire benchmark suite at any time, run:
```bash
python -m pytest backend/tests -v
```
All 9 unit tests validate these exact numbers with `Decimal` precision.

