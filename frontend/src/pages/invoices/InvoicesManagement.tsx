import React, { useState, useEffect } from 'react';
import {
  FileText, Download, Truck, CheckCircle2, AlertTriangle,
  FileCheck, Printer, ShieldAlert, ArrowRight, Eye
} from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { api } from '../../services/api';
import { Invoice, Order } from '../../types';

export const InvoicesManagement: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [invRes, ordRes] = await Promise.all([
        api.getInvoices(),
        api.getOrders(),
      ]);
      setInvoices(invRes);
      setOrders(ordRes);
    } catch (e: any) {
      console.error('Failed to load invoices', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApproveOrder = async (orderId: number) => {
    try {
      await api.decideOrder(orderId, { action: 'approve' });
      setActionMessage(`Order approved! You can now generate the GST invoice.`);
      loadData();
    } catch (e: any) {
      alert(e.message || 'Failed to approve order');
    }
  };

  const handleGenerateInvoice = async (orderId: number) => {
    try {
      await api.generateInvoice(orderId);
      setActionMessage('GST Tax Invoice generated successfully with sequential numbering.');
      loadData();
    } catch (e: any) {
      alert(e.message || 'Failed to generate invoice');
    }
  };

  const handleDispatch = async (invoiceId: number) => {
    try {
      await api.dispatchInvoice(invoiceId);
      setActionMessage('Goods dispatched! Finished goods stock ledger atomically deducted.');
      loadData();
    } catch (e: any) {
      alert(e.message || 'Dispatch failed');
    }
  };

  const pendingOrders = orders.filter((o) => o.status === 'submitted');
  const approvedOrdersReadyForBilling = orders.filter((o) => o.status === 'approved');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Admin Verification, GST Invoicing & Dispatch</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Verify field orders, generate statutory GST tax invoices (CGST+SGST / IGST), download PDFs, and record dispatch.
          </p>
        </div>
      </div>

      {actionMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <span>{actionMessage}</span>
          </div>
          <button onClick={() => setActionMessage(null)} className="text-xs font-semibold text-emerald-900 hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Orders Awaiting Verification Queue */}
      {pendingOrders.length > 0 && (
        <Card title="Orders Awaiting Admin Verification" subtitle="Verify product quantities and customer terms">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Order #</th>
                  <th className="py-2.5 px-3">Customer</th>
                  <th className="py-2.5 px-3">Items & Qty</th>
                  <th className="py-2.5 px-3">Amount</th>
                  <th className="py-2.5 px-3 text-right">Verification Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {pendingOrders.map((ord) => (
                  <tr key={ord.id} className="hover:bg-slate-50">
                    <td className="py-3 px-3 font-mono font-bold text-brand-900">{ord.order_number}</td>
                    <td className="py-3 px-3 text-slate-800">{ord.customer_name}</td>
                    <td className="py-3 px-3 text-slate-600">
                      {ord.items.map((i, idx) => (
                        <span key={idx} className="block">
                          {i.product_name || 'Murukku 200g'} × {i.quantity} pkts
                        </span>
                      ))}
                    </td>
                    <td className="py-3 px-3 font-mono font-semibold">₹ {Number(ord.total_amount).toLocaleString()}</td>
                    <td className="py-3 px-3 text-right space-x-2">
                      <Button size="sm" onClick={() => handleApproveOrder(ord.id)} variant="success">
                        Approve Order
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Approved Orders Ready for Billing */}
      {approvedOrdersReadyForBilling.length > 0 && (
        <Card title="Approved Orders Pending GST Billing" subtitle="Generate GST Tax Invoice">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Order #</th>
                  <th className="py-2.5 px-3">Customer</th>
                  <th className="py-2.5 px-3">Taxable Value</th>
                  <th className="py-2.5 px-3 text-right">Billing Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {approvedOrdersReadyForBilling.map((ord) => (
                  <tr key={ord.id} className="hover:bg-slate-50">
                    <td className="py-3 px-3 font-mono font-bold text-brand-900">{ord.order_number}</td>
                    <td className="py-3 px-3 text-slate-800">{ord.customer_name}</td>
                    <td className="py-3 px-3 font-mono font-semibold">₹ {Number(ord.total_amount).toLocaleString()}</td>
                    <td className="py-3 px-3 text-right">
                      <Button size="sm" onClick={() => handleGenerateInvoice(ord.id)}>
                        <FileText className="w-3.5 h-3.5 mr-1" /> Generate GST Invoice
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Generated GST Invoices & Dispatch Queue */}
      <Card title="Posted GST Tax Invoices" subtitle="Full statutory tax breakdown, printable PDF invoices and physical dispatch">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-700 uppercase font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-3">Invoice #</th>
                <th className="py-3 px-3">Customer & State</th>
                <th className="py-3 px-3">Taxable (₹)</th>
                <th className="py-3 px-3">CGST / SGST</th>
                <th className="py-3 px-3">IGST</th>
                <th className="py-3 px-3">Total (₹)</th>
                <th className="py-3 px-3">Dispatch Status</th>
                <th className="py-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {invoices.map((inv) => (
                <tr key={inv.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-3 font-mono font-bold text-brand-900">{inv.invoice_number}</td>
                  <td className="py-3 px-3 text-slate-800">
                    <span className="font-semibold block">{inv.customer_name}</span>
                    <span className="text-[10px] text-slate-500">
                      {inv.place_of_supply} • {inv.is_interstate ? 'Interstate' : 'Intrastate'}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono">₹ {Number(inv.taxable_amount).toLocaleString()}</td>
                  <td className="py-3 px-3 font-mono text-slate-600">
                    {!inv.is_interstate ? (
                      <>
                        ₹ {Number(inv.cgst_amount).toFixed(2)} + ₹ {Number(inv.sgst_amount).toFixed(2)}
                      </>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-600">
                    {inv.is_interstate ? `₹ ${Number(inv.igst_amount).toFixed(2)}` : <span className="text-slate-400">—</span>}
                  </td>
                  <td className="py-3 px-3 font-mono font-bold text-slate-900">
                    ₹ {Number(inv.total_amount).toLocaleString()}
                  </td>
                  <td className="py-3 px-3">
                    <Badge variant={inv.dispatch_status === 'dispatched' ? 'success' : 'warning'}>
                      {inv.dispatch_status.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="py-3 px-3 text-right space-x-2">
                    {inv.dispatch_status !== 'dispatched' && (
                      <Button size="sm" variant="success" onClick={() => handleDispatch(inv.id)}>
                        <Truck className="w-3.5 h-3.5 mr-1" /> Dispatch
                      </Button>
                    )}
                    <a
                      href={api.getInvoicePdfUrl(inv.id)}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center justify-center px-2.5 py-1.5 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100 transition-colors shadow-2xs"
                    >
                      <Download className="w-3.5 h-3.5 mr-1 text-brand-900" /> PDF
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

