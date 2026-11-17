import React, { useState, useEffect } from 'react';
import { IndianRupee, Plus, CheckCircle, ArrowDownLeft, ShieldCheck } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { api } from '../../services/api';
import { Customer, Invoice, Payment } from '../../types';

export const PaymentsManagement: React.FC = () => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCustomerId, setSelectedCustomerId] = useState<number | ''>('');
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<number | ''>('');
  const [amount, setAmount] = useState<number>(4000);
  const [mode, setMode] = useState<string>('bank_transfer');
  const [refNo, setRefNo] = useState<string>('NEFT-SBIN88990011');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const load = async () => {
    try {
      const [pRes, cRes, invRes] = await Promise.all([
        api.getPayments(),
        api.getCustomers(),
        api.getInvoices(),
      ]);
      setPayments(pRes);
      setCustomers(cRes);
      setInvoices(invRes);

      if (cRes.length > 0 && selectedCustomerId === '') setSelectedCustomerId(cRes[0].id);
      if (invRes.length > 0 && selectedInvoiceId === '') setSelectedInvoiceId(invRes[0].id);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCustomerId || amount <= 0) return;

    setIsSubmitting(true);
    try {
      await api.recordPayment({
        customer_id: Number(selectedCustomerId),
        invoice_id: selectedInvoiceId ? Number(selectedInvoiceId) : undefined,
        amount: Number(amount),
        payment_mode: mode,
        reference_number: refNo,
        notes: `Customer collection via ${mode.toUpperCase()} (Ref: ${refNo})`,
      });

      setStatusMessage('Payment recorded! Customer balance outstanding automatically reconciled.');
      setIsModalOpen(false);
      load();
    } catch (err: any) {
      alert(err.message || 'Payment recording failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalOutstanding = customers.reduce((acc, c) => acc + Number(c.balance_outstanding), 0);
  const totalCollected = payments.reduce((acc, p) => acc + Number(p.amount), 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Payments & Customer Receivables (AR)</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Log bank remittances, UPI, cheques, and cash payments against customer accounts and GST invoices.
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-1.5" /> Log Customer Payment
        </Button>
      </div>

      {statusMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <span>{statusMessage}</span>
          </div>
          <button onClick={() => setStatusMessage(null)} className="text-xs font-semibold text-emerald-900 hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-xs font-medium text-slate-500 uppercase">Total Receivables Outstanding</p>
          <p className="text-2xl font-bold font-mono text-amber-700 mt-1">₹ {totalOutstanding.toLocaleString()}</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Pending collection from retailers</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-xs font-medium text-slate-500 uppercase">Total Payments Reconciled</p>
          <p className="text-2xl font-bold font-mono text-emerald-700 mt-1">₹ {totalCollected.toLocaleString()}</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Verified bank & UPI receipts</p>
        </div>
      </div>

      {/* Customers Balance Table */}
      <Card title="Customer Accounts Summary" subtitle="Credit limits and outstanding exposure">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
              <tr>
                <th className="py-2.5 px-3">Customer Name</th>
                <th className="py-2.5 px-3">State</th>
                <th className="py-2.5 px-3">Credit Limit</th>
                <th className="py-2.5 px-3">Balance Outstanding</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {customers.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50">
                  <td className="py-3 px-3 font-semibold text-slate-900">{c.name}</td>
                  <td className="py-3 px-3">{c.state}</td>
                  <td className="py-3 px-3 font-mono text-slate-600">₹ {Number(c.credit_limit).toLocaleString()}</td>
                  <td className="py-3 px-3 font-mono font-bold text-amber-700">
                    ₹ {Number(c.balance_outstanding).toLocaleString()}
                  </td>
                  <td className="py-3 px-3">
                    <Badge variant={c.balance_outstanding > 0 ? 'warning' : 'success'}>
                      {c.balance_outstanding > 0 ? 'DUE PENDING' : 'CLEAR'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Payments Log */}
      <Card title="Remittance & Payment Receipts Log" subtitle="Double-entry payment audit trail">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-700 uppercase font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-3">Receipt #</th>
                <th className="py-3 px-3">Customer</th>
                <th className="py-3 px-3">Invoice #</th>
                <th className="py-3 px-3">Mode & Ref</th>
                <th className="py-3 px-3">Amount Received</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {payments.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-3 font-mono font-bold text-brand-900">{p.payment_number}</td>
                  <td className="py-3 px-3 text-slate-800">{p.customer_name}</td>
                  <td className="py-3 px-3 font-mono text-slate-600">{p.invoice_number || 'On Account'}</td>
                  <td className="py-3 px-3 text-slate-600">
                    <span className="font-semibold block uppercase">{p.payment_mode}</span>
                    <span className="text-[10px] text-slate-400 font-mono">{p.reference_number || 'N/A'}</span>
                  </td>
                  <td className="py-3 px-3 font-mono font-bold text-emerald-700 text-sm">
                    ₹ {Number(p.amount).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Log Payment Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Record Customer Payment Receipt">
        <form onSubmit={handleRecordPayment} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Select Customer</label>
            <select
              value={selectedCustomerId}
              onChange={(e) => setSelectedCustomerId(Number(e.target.value))}
              className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white"
              required
            >
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} (Outstanding: ₹{Number(c.balance_outstanding).toLocaleString()})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Link to Invoice (Optional)</label>
            <select
              value={selectedInvoiceId}
              onChange={(e) => setSelectedInvoiceId(e.target.value ? Number(e.target.value) : '')}
              className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white font-mono"
            >
              <option value="">General On-Account Payment</option>
              {invoices.map((inv) => (
                <option key={inv.id} value={inv.id}>
                  {inv.invoice_number} — Total: ₹{inv.total_amount} (Balance Due: ₹{inv.balance_due})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Payment Amount (₹)</label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 font-mono"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Payment Mode</label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white"
              >
                <option value="bank_transfer">Bank Transfer (NEFT/RTGS)</option>
                <option value="upi">UPI / GPay</option>
                <option value="cheque">Cheque</option>
                <option value="cash">Cash Receipt</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Transaction Ref / UTR / Cheque #</label>
            <input
              type="text"
              value={refNo}
              onChange={(e) => setRefNo(e.target.value)}
              className="w-full text-xs border border-slate-300 rounded-lg p-2.5 font-mono"
            />
          </div>

          <div className="pt-2 flex justify-end gap-3 border-t border-slate-100">
            <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Reconcile Payment
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

