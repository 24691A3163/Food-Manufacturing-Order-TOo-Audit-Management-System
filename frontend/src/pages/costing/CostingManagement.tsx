import React, { useState, useEffect } from 'react';
import { IndianRupee, PieChart, TrendingUp, ShieldCheck, FileSpreadsheet } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { api } from '../../services/api';

export const CostingManagement: React.FC = () => {
  const [costings, setCostings] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      try {
        const res = await api.getAllBatchCostings();
        setCostings(res);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const latest = costings[0];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Product Costing & Unit Economics</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Full batch cost breakdown: Raw materials + Packaging + Direct labour + Fuel/Gas overheads.
          </p>
        </div>
      </div>

      {latest && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <p className="text-xs font-medium text-slate-500 uppercase">Cost Per Good Packet</p>
            <p className="text-2xl font-bold font-mono text-slate-900 mt-1">₹ {latest.cost_per_good_packet}</p>
            <p className="text-[11px] text-slate-400 mt-0.5">Murukku 200g (Batch 1)</p>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <p className="text-xs font-medium text-slate-500 uppercase">Selling Price (Pre-GST)</p>
            <p className="text-2xl font-bold font-mono text-slate-900 mt-1">₹ {latest.selling_price}</p>
            <p className="text-[11px] text-slate-400 mt-0.5">Wholesale distributor price</p>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <p className="text-xs font-medium text-slate-500 uppercase">Gross Margin (₹/Pkt)</p>
            <p className="text-2xl font-bold font-mono text-emerald-700 mt-1">₹ {latest.gross_margin_per_packet}</p>
            <p className="text-[11px] text-slate-400 mt-0.5">Profit per packet</p>
          </div>
          <div className="bg-emerald-50 rounded-xl border border-emerald-200 p-4">
            <p className="text-xs font-bold text-emerald-800 uppercase">Gross Profit Margin</p>
            <p className="text-2xl font-black font-mono text-emerald-950 mt-1">{latest.gross_margin_percent} %</p>
            <p className="text-[11px] text-emerald-700 mt-0.5">Benchmark Target Achieved</p>
          </div>
        </div>
      )}

      {/* Batches Costing Table */}
      <Card title="Batch Costing Ledger" subtitle="Detailed absorption costing analysis">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-700 uppercase font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-3">Batch Number</th>
                <th className="py-3 px-3">Output (Pkts)</th>
                <th className="py-3 px-3">RM Cost (₹)</th>
                <th className="py-3 px-3">Packaging (₹)</th>
                <th className="py-3 px-3">Labour (₹)</th>
                <th className="py-3 px-3">Gas & Power (₹)</th>
                <th className="py-3 px-3">Total Batch (₹)</th>
                <th className="py-3 px-3">Unit Cost (₹)</th>
                <th className="py-3 px-3">Margin %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {costings.map((c, i) => (
                <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-3 font-mono font-bold text-brand-900">{c.batch_number}</td>
                  <td className="py-3 px-3 font-mono font-semibold">{c.actual_good_quantity}</td>
                  <td className="py-3 px-3 font-mono">₹ {c.raw_material_cost}</td>
                  <td className="py-3 px-3 font-mono">₹ {c.packaging_cost}</td>
                  <td className="py-3 px-3 font-mono">₹ {c.labour_cost}</td>
                  <td className="py-3 px-3 font-mono">₹ {c.power_gas_cost}</td>
                  <td className="py-3 px-3 font-mono font-bold text-slate-900">₹ {c.total_batch_cost}</td>
                  <td className="py-3 px-3 font-mono font-bold text-brand-900">₹ {c.cost_per_good_packet}</td>
                  <td className="py-3 px-3 font-mono font-bold text-emerald-700">{c.gross_margin_percent} %</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

