import React, { useState, useEffect } from 'react';
import { Truck, Plus, CheckCircle, Boxes, ArrowRight, DollarSign } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { api } from '../../services/api';
import { Supplier, RawMaterial } from '../../types';

export const PurchasesManagement: React.FC = () => {
  const [purchases, setPurchases] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [rawMaterials, setRawMaterials] = useState<RawMaterial[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSupplierId, setSelectedSupplierId] = useState<number | ''>('');
  const [selectedRmId, setSelectedRmId] = useState<number | ''>('');
  const [qty, setQty] = useState<number>(60);
  const [rate, setRate] = useState<number>(45);
  const [invoiceNo, setInvoiceNo] = useState<string>('MAD-AGRO-789');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const load = async () => {
    try {
      const [pRes, sRes, rmRes] = await Promise.all([
        api.getPurchases(),
        api.getSuppliers(),
        api.getRawMaterials(),
      ]);
      setPurchases(pRes);
      setSuppliers(sRes);
      setRawMaterials(rmRes);

      if (sRes.length > 0 && selectedSupplierId === '') setSelectedSupplierId(sRes[0].id);
      if (rmRes.length > 0 && selectedRmId === '') setSelectedRmId(rmRes[0].id);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreatePurchase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSupplierId || !selectedRmId || qty <= 0 || rate <= 0) return;

    setIsSubmitting(true);
    try {
      const rm = rawMaterials.find((r) => r.id === Number(selectedRmId));
      await api.createPurchase({
        supplier_id: Number(selectedSupplierId),
        supplier_invoice_no: invoiceNo,
        items: [
          {
            item_type: 'raw',
            raw_material_id: Number(selectedRmId),
            quantity: Number(qty),
            unit_price: Number(rate),
            unit: rm?.unit || 'kg',
          },
        ],
        notes: `Purchase of ${qty} ${rm?.unit} ${rm?.name} @ ₹${rate}/${rm?.unit}`,
      });

      setStatusMessage('Purchase recorded! Inventory and weighted-average cost updated.');
      setIsModalOpen(false);
      load();
    } catch (err: any) {
      alert(err.message || 'Failed to create purchase');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Purchases & Supplier Procurement</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Record raw material & packaging supplier shipments. Automatically recalibrates weighted-average inventory valuation.
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-1.5" /> Record Material Purchase
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

      {/* Suppliers Card */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {suppliers.map((s) => (
          <div key={s.id} className="bg-white rounded-xl border border-slate-200 p-4">
            <p className="font-semibold text-slate-900 text-sm">{s.name}</p>
            <p className="text-xs text-slate-500 mt-0.5">{s.address}</p>
            <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-mono">GSTIN: {s.gstin || 'Unregistered'}</span>
              <Badge variant="success">Active Vendor</Badge>
            </div>
          </div>
        ))}
      </div>

      {/* Purchases List */}
      <Card title="Supplier Purchase Orders & Deliveries" subtitle="Transaction history">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-700 uppercase font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-3">PO Number</th>
                <th className="py-3 px-3">Supplier</th>
                <th className="py-3 px-3">Vendor Invoice #</th>
                <th className="py-3 px-3">Materials Received</th>
                <th className="py-3 px-3">Total Cost</th>
                <th className="py-3 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {purchases.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-3 font-mono font-bold text-brand-900">{p.purchase_number}</td>
                  <td className="py-3 px-3 text-slate-800">{p.supplier_name}</td>
                  <td className="py-3 px-3 font-mono text-slate-600">{p.supplier_invoice_no}</td>
                  <td className="py-3 px-3 text-slate-700">
                    {p.items.map((i: any, idx: number) => (
                      <span key={idx} className="block">
                        {i.item_name} × {i.quantity} {i.unit} @ ₹{i.unit_price}/{i.unit}
                      </span>
                    ))}
                  </td>
                  <td className="py-3 px-3 font-mono font-bold text-slate-900">
                    ₹ {Number(p.total_amount).toLocaleString()}
                  </td>
                  <td className="py-3 px-3">
                    <Badge variant="success">{p.status.toUpperCase()}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Record Purchase Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Record Material Inward Purchase">
        <form onSubmit={handleCreatePurchase} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Select Supplier</label>
            <select
              value={selectedSupplierId}
              onChange={(e) => setSelectedSupplierId(Number(e.target.value))}
              className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white"
              required
            >
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Vendor Bill / Invoice Number</label>
            <input
              type="text"
              value={invoiceNo}
              onChange={(e) => setInvoiceNo(e.target.value)}
              className="w-full text-xs border border-slate-300 rounded-lg p-2.5 font-mono"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Material Item</label>
            <select
              value={selectedRmId}
              onChange={(e) => setSelectedRmId(Number(e.target.value))}
              className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-white"
              required
            >
              {rawMaterials.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} (Current: {r.current_stock} {r.unit} @ ₹{Number(r.weighted_average_cost).toFixed(2)}/unit)
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Purchase Quantity</label>
              <input
                type="number"
                value={qty}
                onChange={(e) => setQty(Number(e.target.value))}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 font-mono"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Purchase Rate (₹ / unit)</label>
              <input
                type="number"
                value={rate}
                onChange={(e) => setRate(Number(e.target.value))}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 font-mono"
                required
              />
            </div>
          </div>

          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-900">
            <span className="font-semibold block">Total Invoice Cost: ₹ {(qty * rate).toLocaleString()}</span>
            <span className="text-[11px] text-blue-700">
              Upon receipt, system automatically recalibrates weighted-average inventory valuation.
            </span>
          </div>

          <div className="pt-2 flex justify-end gap-3 border-t border-slate-100">
            <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Post Inward Receipt
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

