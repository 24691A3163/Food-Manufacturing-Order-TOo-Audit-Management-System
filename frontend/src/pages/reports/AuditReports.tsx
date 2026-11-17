import React, { useState, useEffect } from 'react';
import {
  FileText, Download, BarChart3, CheckCircle2,
  FileSpreadsheet, ShieldCheck, Printer
} from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { api } from '../../services/api';

export const AuditReports: React.FC = () => {
  const [gstr1, setGstr1] = useState<any>(null);
  const [salesSummary, setSalesSummary] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      try {
        const [gstRes, salesRes] = await Promise.all([
          api.getGSTR1(),
          api.getSalesSummary(),
        ]);
        setGstr1(gstRes);
        setSalesSummary(salesRes);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header with Export buttons */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Auditor Desk & Monthly Statutory Reports</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            GSTR-1 tax compliance schedule, B2B sales summaries, and Excel/CSV download reports.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <a
            href={api.getProductionExcelUrl()}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-300 hover:bg-emerald-100 shadow-2xs"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-700" /> Export Production Excel (.xlsx)
          </a>
          <a
            href={api.getStockLedgerCsvUrl()}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 shadow-2xs"
          >
            <Download className="w-3.5 h-3.5 text-brand-900" /> Export Stock Ledger (.csv)
          </a>
        </div>
      </div>

      {/* GSTR-1 Monthly Summary */}
      {gstr1 && (
        <Card
          title="GSTR-1 Statutory Return Summary (Current Tax Period)"
          subtitle={`Filing GSTIN: ${gstr1.gstin} | State: Tamil Nadu (33)`}
        >
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-500 uppercase font-medium">Total Taxable Value</span>
              <p className="text-xl font-bold font-mono text-slate-900 mt-1">
                ₹ {Number(gstr1.summary.total_taxable).toLocaleString()}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
              <span className="text-xs text-blue-700 uppercase font-medium">CGST Total</span>
              <p className="text-xl font-bold font-mono text-blue-950 mt-1">
                ₹ {Number(gstr1.summary.total_cgst).toLocaleString()}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
              <span className="text-xs text-blue-700 uppercase font-medium">SGST Total</span>
              <p className="text-xl font-bold font-mono text-blue-950 mt-1">
                ₹ {Number(gstr1.summary.total_sgst).toLocaleString()}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-brand-950 text-white">
              <span className="text-xs text-slate-300 uppercase font-medium">Total Tax Liability</span>
              <p className="text-xl font-bold font-mono text-amber-400 mt-1">
                ₹ {Number(gstr1.summary.total_tax).toLocaleString()}
              </p>
            </div>
          </div>

          {/* B2B Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 uppercase font-semibold text-[11px] border-b border-slate-200">
                <tr>
                  <th className="py-3 px-3">Invoice #</th>
                  <th className="py-3 px-3">Date</th>
                  <th className="py-3 px-3">Customer & GSTIN</th>
                  <th className="py-3 px-3">Place of Supply</th>
                  <th className="py-3 px-3">Taxable Value</th>
                  <th className="py-3 px-3">CGST (₹)</th>
                  <th className="py-3 px-3">SGST (₹)</th>
                  <th className="py-3 px-3">IGST (₹)</th>
                  <th className="py-3 px-3">Total Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {gstr1.b2b_invoices.map((inv: any, i: number) => (
                  <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-brand-900">{inv.invoice_number}</td>
                    <td className="py-3 px-3 text-slate-600">{inv.invoice_date}</td>
                    <td className="py-3 px-3 text-slate-800">
                      <span className="font-semibold block">{inv.customer_name}</span>
                      <span className="text-[10px] text-slate-500 font-mono">{inv.customer_gstin}</span>
                    </td>
                    <td className="py-3 px-3">{inv.place_of_supply}</td>
                    <td className="py-3 px-3 font-mono font-semibold">₹ {Number(inv.taxable_value).toLocaleString()}</td>
                    <td className="py-3 px-3 font-mono">₹ {Number(inv.cgst_amount).toFixed(2)}</td>
                    <td className="py-3 px-3 font-mono">₹ {Number(inv.sgst_amount).toFixed(2)}</td>
                    <td className="py-3 px-3 font-mono">
                      {inv.is_interstate ? `₹ ${Number(inv.igst_amount).toFixed(2)}` : '—'}
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-slate-900">
                      ₹ {Number(inv.invoice_total).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Customer Wise Receivables & Audit Trail */}
      {salesSummary && (
        <Card title="Customer Accounts & Collections Ledger" subtitle="Outstanding debt balance reconciliation">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Customer Name</th>
                  <th className="py-2.5 px-3">State</th>
                  <th className="py-2.5 px-3">Total Billed Sales</th>
                  <th className="py-2.5 px-3">Balance Outstanding</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {salesSummary.customer_breakdown.map((c: any) => (
                  <tr key={c.customer_id} className="hover:bg-slate-50">
                    <td className="py-3 px-3 font-semibold text-slate-900">{c.customer_name}</td>
                    <td className="py-3 px-3">{c.state}</td>
                    <td className="py-3 px-3 font-mono">₹ {Number(c.total_purchases).toLocaleString()}</td>
                    <td className="py-3 px-3 font-mono font-bold text-amber-700">
                      ₹ {Number(c.balance_outstanding).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};

