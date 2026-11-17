import React, { useState, useEffect } from 'react';
import {
  IndianRupee, TrendingUp, AlertTriangle, Boxes,
  Factory, ShoppingBag, ArrowUpRight, CheckCircle2, Clock
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  Tooltip, Legend, CartesianGrid, PieChart, Pie, Cell
} from 'recharts';
import { StatCard } from '../../components/common/StatCard';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { api } from '../../services/api';

export const OwnerDashboard: React.FC<{ onNavigate: (tab: string) => void }> = ({ onNavigate }) => {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await api.getOwnerDashboard();
        setData(res);
      } catch (e) {
        console.error('Dashboard load failed', e);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (isLoading || !data) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-900"></div>
      </div>
    );
  }

  const PIE_COLORS = ['#1e3a8a', '#0284c7', '#10b981', '#f59e0b'];

  return (
    <div className="space-y-6">
      {/* Executive Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Invoiced (MTD)"
          value={`₹ ${Number(data.total_invoiced_mtd).toLocaleString()}`}
          subtitle="Tax invoices posted"
          icon={IndianRupee}
          color="blue"
          trend={{ value: '₹7,875', isPositive: true }}
        />
        <StatCard
          title="Collections Received"
          value={`₹ ${Number(data.total_collections_mtd).toLocaleString()}`}
          subtitle="Direct bank / cash remittances"
          icon={TrendingUp}
          color="emerald"
        />
        <StatCard
          title="Outstanding Receivables"
          value={`₹ ${Number(data.total_outstanding_ar).toLocaleString()}`}
          subtitle="Retailer balance due"
          icon={IndianRupee}
          color="amber"
        />
        <StatCard
          title="Finished Goods Stock"
          value={`${Number(data.finished_goods_packets).toLocaleString()} pkts`}
          subtitle="Murukku 200g in warehouse"
          icon={Boxes}
          color="purple"
        />
      </div>

      {/* Alerts Row */}
      {data.active_variance_alerts_count > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-100 rounded-lg text-amber-700">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-amber-900">
                {data.active_variance_alerts_count} Production Yield Variance Alert(s) Detected
              </h4>
              <p className="text-xs text-amber-700 mt-0.5">
                Batch <strong>BATCH-2026-0001</strong> produced 188 good packets vs 200 standard planned (-6.0% yield variance, +5.0% oil variance).
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigate('production')}
            className="text-xs font-semibold px-3 py-1.5 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors shadow-xs"
          >
            Inspect Batch
          </button>
        </div>
      )}

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sales vs Production Trend (2 cols) */}
        <Card
          className="lg:col-span-2"
          title="Operational Performance Trend"
          subtitle="Monthly Comparison: Revenue vs Production Cost vs Collections"
        >
          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.sales_trend}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} tickFormatter={(val) => `₹${val / 1000}k`} />
                <Tooltip
                  formatter={(value: any) => [`₹ ${Number(value).toLocaleString()}`, '']}
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                />
                <Legend />
                <Bar dataKey="sales" name="Invoiced Sales" fill="#1e3a8a" radius={[4, 4, 0, 0]} />
                <Bar dataKey="production" name="Production Cost" fill="#0284c7" radius={[4, 4, 0, 0]} />
                <Bar dataKey="collections" name="Collections" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Product Category Mix */}
        <Card title="Product Category Mix" subtitle="Production volume distribution">
          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.category_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {data.category_distribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-100 text-xs">
            {data.category_distribution.map((item: any, idx: number) => (
              <div key={idx} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[idx % PIE_COLORS.length] }}></span>
                <span className="text-slate-600">{item.name}:</span>
                <span className="font-semibold text-slate-800">{item.value}%</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Operational Queues */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Orders Queue */}
        <Card
          title="Recent Field Orders"
          subtitle="Orders placed by sales representatives"
          action={
            <button onClick={() => onNavigate('orders')} className="text-xs text-brand-900 font-semibold hover:underline">
              View All Orders
            </button>
          }
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase font-medium">
                <tr>
                  <th className="py-2.5 px-3">Order #</th>
                  <th className="py-2.5 px-3">Customer</th>
                  <th className="py-2.5 px-3">Amount</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {data.recent_orders.map((ord: any) => (
                  <tr key={ord.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-mono font-semibold text-brand-900">{ord.order_number}</td>
                    <td className="py-2.5 px-3 text-slate-700">{ord.customer_name}</td>
                    <td className="py-2.5 px-3 font-mono">₹ {Number(ord.total_amount).toLocaleString()}</td>
                    <td className="py-2.5 px-3">
                      <Badge
                        variant={
                          ord.status === 'dispatched'
                            ? 'success'
                            : ord.status === 'approved' || ord.status === 'invoiced'
                            ? 'info'
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

        {/* Recent Production Batches */}
        <Card
          title="Recent Production Runs"
          subtitle="Batch yield and variance performance"
          action={
            <button onClick={() => onNavigate('production')} className="text-xs text-brand-900 font-semibold hover:underline">
              View All Batches
            </button>
          }
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase font-medium">
                <tr>
                  <th className="py-2.5 px-3">Batch #</th>
                  <th className="py-2.5 px-3">Product</th>
                  <th className="py-2.5 px-3">Good Output</th>
                  <th className="py-2.5 px-3">Yield Variance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {data.recent_batches.map((b: any) => (
                  <tr key={b.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-mono font-semibold text-slate-900">{b.batch_number}</td>
                    <td className="py-2.5 px-3 text-slate-700">{b.product_name}</td>
                    <td className="py-2.5 px-3 font-mono">{b.actual_good} pkts</td>
                    <td className="py-2.5 px-3">
                      <span className={`font-mono font-semibold ${b.is_alert ? 'text-amber-600' : 'text-emerald-600'}`}>
                        {b.yield_variance > 0 ? `+${b.yield_variance}%` : `${b.yield_variance}%`}
                      </span>
                      {b.is_alert && (
                        <span className="ml-1 text-[10px] bg-amber-100 text-amber-800 px-1 py-0.2 rounded font-bold">
                          ALERT
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
};

