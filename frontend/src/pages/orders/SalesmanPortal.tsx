import React, { useState, useEffect } from 'react';
import {
  ShoppingBag, Plus, CheckCircle, AlertCircle, Clock,
  Truck, ArrowRight, UserCheck, ShieldAlert
} from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { api } from '../../services/api';
import { Customer, Product, Order } from '../../types';

export const SalesmanPortal: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [isNewOrderOpen, setIsNewOrderOpen] = useState(false);
  const [selectedCustomerId, setSelectedCustomerId] = useState<number | ''>('');
  const [selectedProductId, setSelectedProductId] = useState<number | ''>('');
  const [quantity, setQuantity] = useState<number>(150);
  const [notes, setNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadData = async () => {
    try {
      const [custRes, prodRes, ordRes] = await Promise.all([
        api.getCustomers(),
        api.getProducts(),
        api.getOrders(),
      ]);
      setCustomers(custRes);
      setProducts(prodRes);
      setOrders(ordRes);

      if (custRes.length > 0 && selectedCustomerId === '') {
        setSelectedCustomerId(custRes[0].id);
      }
      if (prodRes.length > 0 && selectedProductId === '') {
        setSelectedProductId(prodRes[0].id);
      }
    } catch (e: any) {
      console.error('Error loading salesman data', e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const selectedProduct = products.find((p) => p.id === Number(selectedProductId));
  const availableStock = selectedProduct ? selectedProduct.current_stock : 0;
  const isStockShortage = selectedProduct && quantity > availableStock;
  const shortageQuantity = isStockShortage ? quantity - availableStock : 0;

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCustomerId || !selectedProductId || quantity <= 0) return;

    setIsSubmitting(true);
    setStatusMessage(null);
    try {
      await api.createOrder({
        customer_id: Number(selectedCustomerId),
        items: [
          {
            product_id: Number(selectedProductId),
            quantity: Number(quantity),
            unit_price: selectedProduct?.selling_price || 50,
          },
        ],
        notes,
      });

      setStatusMessage({
        type: 'success',
        text: `Order submitted successfully! ${isStockShortage ? `Note: Insufficient stock of ${shortageQuantity} packets flagged for Admin.` : ''}`,
      });
      setIsNewOrderOpen(false);
      loadData();
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to submit order' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Mobile-Friendly Salesman Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-brand-50 text-brand-900 rounded-full border border-brand-200">
            Field Sales Console
          </span>
          <h2 className="text-xl font-bold text-slate-900 mt-2">Mobile Order Booking</h2>
          <p className="text-xs text-slate-500 mt-0.5">Book retailer orders with real-time finished goods stock validation</p>
        </div>
        <Button
          onClick={() => {
            setIsNewOrderOpen(true);
            setStatusMessage(null);
          }}
          className="w-full sm:w-auto shadow-md"
        >
          <Plus className="w-4 h-4 mr-1.5" /> Book New Order
        </Button>
      </div>

      {statusMessage && (
        <div
          className={`p-4 rounded-xl text-sm flex items-center gap-3 border ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {statusMessage.type === 'success' ? (
            <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* Quick Customer Outstanding & Sales */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {customers.map((c) => (
          <div key={c.id} className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs hover:border-brand-300 transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-slate-900 text-sm">{c.name}</p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {c.state} ({c.state_code}) • {c.code}
                </p>
              </div>
              <Badge variant={c.state === 'Tamil Nadu' ? 'info' : 'purple'}>
                {c.state === 'Tamil Nadu' ? 'Intrastate (TN)' : 'Interstate (KA)'}
              </Badge>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-500">Balance Outstanding:</span>
              <span className="font-mono font-bold text-amber-700">₹ {Number(c.balance_outstanding).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Sales Orders History */}
      <Card title="Submitted Orders & Delivery Status" subtitle="Real-time order pipeline">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-3">Order Number</th>
                <th className="py-3 px-3">Customer</th>
                <th className="py-3 px-3">Products & Qty</th>
                <th className="py-3 px-3">Total Amount</th>
                <th className="py-3 px-3">Order Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {orders.map((ord) => (
                <tr key={ord.id} className="hover:bg-slate-50/80 transition-colors">
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
                  <td className="py-3 px-3">
                    <Badge
                      variant={
                        ord.status === 'dispatched'
                          ? 'success'
                          : ord.status === 'invoiced' || ord.status === 'approved'
                          ? 'info'
                          : ord.status === 'rejected'
                          ? 'danger'
                          : 'warning'
                      }
                    >
                      {ord.status.toUpperCase()}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Book New Order Modal */}
      <Modal isOpen={isNewOrderOpen} onClose={() => setIsNewOrderOpen(false)} title="Create New Sales Order">
        <form onSubmit={handleCreateOrder} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Select Customer</label>
            <select
              value={selectedCustomerId}
              onChange={(e) => setSelectedCustomerId(Number(e.target.value))}
              className="w-full text-xs font-medium border border-slate-300 rounded-lg p-2.5 bg-white focus:ring-1 focus:ring-brand-500"
              required
            >
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.state})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Select Finished Product</label>
            <select
              value={selectedProductId}
              onChange={(e) => setSelectedProductId(Number(e.target.value))}
              className="w-full text-xs font-medium border border-slate-300 rounded-lg p-2.5 bg-white focus:ring-1 focus:ring-brand-500"
              required
            >
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} — ₹{p.selling_price}/pkt (Stock: {p.current_stock} pkts)
                </option>
              ))}
            </select>
          </div>

          {/* Real-time Finished Goods Stock Indicator */}
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-600 font-medium">Available Warehouse Stock:</span>
              <span className="font-mono font-bold text-slate-900">{availableStock} packets</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Order Quantity (Packets)</label>
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              className="w-full text-xs font-mono font-medium border border-slate-300 rounded-lg p-2.5 focus:ring-1 focus:ring-brand-500"
              required
            />
          </div>

          {/* Shortage Alert Badge if requested > stock */}
          {isStockShortage && (
            <div className="p-3 rounded-lg bg-rose-50 border border-rose-300 text-rose-800 text-xs flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <div>
                <p className="font-bold">Insufficient Finished Goods Stock!</p>
                <p>
                  Requested {quantity} pkts exceeds available {availableStock} pkts. Shortage of{' '}
                  <strong>{shortageQuantity} packets</strong> will be flagged to Admin.
                </p>
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Delivery Notes / Terms</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Prompt delivery required for weekend retail rush"
              rows={2}
              className="w-full text-xs border border-slate-300 rounded-lg p-2.5 focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div className="pt-2 flex justify-end gap-3 border-t border-slate-100">
            <Button type="button" variant="outline" onClick={() => setIsNewOrderOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Submit Order
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

