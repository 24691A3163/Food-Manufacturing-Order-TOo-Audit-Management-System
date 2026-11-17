import React, { useState, useEffect } from 'react';
import {
  Factory, Plus, AlertTriangle, CheckCircle, Boxes,
  Clock, ArrowRight, ShieldAlert, Sparkles, Layers
} from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { api } from '../../services/api';
import { ProductionRun, Product, RawMaterial, PackagingMaterial } from '../../types';

export const ProductionManagement: React.FC = () => {
  const [runs, setRuns] = useState<ProductionRun[]>([]);
  const [boms, setBoms] = useState<any[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [rawMaterials, setRawMaterials] = useState<RawMaterial[]>([]);
  const [packMaterials, setPackMaterials] = useState<PackagingMaterial[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // New batch form state
  const [plannedQty, setPlannedQty] = useState<number>(200);
  const [actualGoodQty, setActualGoodQty] = useState<number>(188);
  const [damagedQty, setDamagedQty] = useState<number>(6);
  const [cartonsUsed, setCartonsUsed] = useState<number>(9);
  const [flourActual, setFlourActual] = useState<number>(40);
  const [oilActual, setOilActual] = useState<number>(10.5);
  const [spiceActual, setSpiceActual] = useState<number>(1.2);
  const [labourExpense, setLabourExpense] = useState<number>(1200);
  const [powerExpense, setPowerExpense] = useState<number>(600);

  const loadData = async () => {
    try {
      const [runRes, bomRes, prodRes, rmRes, pmRes] = await Promise.all([
        api.getProductionRuns(),
        api.getBOMs(),
        api.getProducts(),
        api.getRawMaterials(),
        api.getPackagingMaterials(),
      ]);
      setRuns(runRes);
      setBoms(bomRes);
      setProducts(prodRes);
      setRawMaterials(rmRes);
      setPackMaterials(pmRes);
    } catch (e) {
      console.error('Failed to load production data', e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Real-time variance preview
  const liveYieldVariance = plannedQty > 0 ? (((actualGoodQty - plannedQty) / plannedQty) * 100).toFixed(2) : '0.00';
  const liveOilVariance = (((oilActual - 10) / 10) * 100).toFixed(2);
  const isVarianceAlert = Math.abs(Number(liveYieldVariance)) > 3 || Math.abs(Number(liveOilVariance)) > 3;

  const handleRecordBatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (boms.length === 0 || products.length === 0) return;

    setIsSubmitting(true);
    try {
      const flourRm = rawMaterials.find((r) => r.name.toLowerCase().includes('flour'));
      const oilRm = rawMaterials.find((r) => r.name.toLowerCase().includes('oil'));
      const spiceRm = rawMaterials.find((r) => r.name.toLowerCase().includes('spice'));
      const pouchPm = packMaterials.find((p) => p.name.toLowerCase().includes('pouch'));
      const cartonPm = packMaterials.find((p) => p.name.toLowerCase().includes('carton'));

      await api.createProductionRun({
        bom_id: boms[0].id,
        product_id: products[0].id,
        planned_quantity: plannedQty,
        actual_good_quantity: actualGoodQty,
        damaged_quantity: damagedQty,
        cartons_used: cartonsUsed,
        material_issues: [
          { material_type: 'raw', raw_material_id: flourRm?.id, actual_qty: flourActual },
          { material_type: 'raw', raw_material_id: oilRm?.id, actual_qty: oilActual },
          { material_type: 'raw', raw_material_id: spiceRm?.id, actual_qty: spiceActual },
          { material_type: 'packaging', packaging_material_id: pouchPm?.id, actual_qty: actualGoodQty + damagedQty },
          { material_type: 'packaging', packaging_material_id: cartonPm?.id, actual_qty: cartonsUsed },
        ],
        labour_expense: labourExpense,
        power_gas_expense: powerExpense,
        notes: `Production Batch: Murukku 200g`,
      });

      setStatusMessage('Production batch recorded! Raw materials issued and Finished Goods inventory increased.');
      setIsModalOpen(false);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to record batch');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Production Management & Recipe BOM</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Record batch production runs, issue materials, monitor yield variances, and flag deviations exceeding 3%.
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} className="shadow-md">
          <Plus className="w-4 h-4 mr-1.5" /> Record Production Batch
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

      {/* Standard BOM Recipe Reference */}
      <Card title="Standard Bill of Materials (BOM) — Murukku 200g" subtitle="Standard input requirement for 200 packets">
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-slate-500 font-medium block">Flour</span>
            <span className="text-base font-bold font-mono text-slate-900 mt-1 block">40.0 kg</span>
            <span className="text-[10px] text-slate-400">@ ₹42.00 - ₹45.00/kg</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-slate-500 font-medium block">Cooking Oil</span>
            <span className="text-base font-bold font-mono text-slate-900 mt-1 block">10.0 L</span>
            <span className="text-[10px] text-slate-400">@ ₹140.00/L</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-slate-500 font-medium block">Salt & Spice Mix</span>
            <span className="text-base font-bold font-mono text-slate-900 mt-1 block">1.2 kg</span>
            <span className="text-[10px] text-slate-400">@ ₹200.00/kg</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-slate-500 font-medium block">200g Pouches</span>
            <span className="text-base font-bold font-mono text-slate-900 mt-1 block">200 pcs</span>
            <span className="text-[10px] text-slate-400">@ ₹2.50/pouch</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-slate-500 font-medium block">Cartons</span>
            <span className="text-base font-bold font-mono text-slate-900 mt-1 block">10 pcs</span>
            <span className="text-[10px] text-slate-400">@ ₹15.00/carton</span>
          </div>
        </div>
      </Card>

      {/* Production Batches History */}
      <Card title="Executed Production Batches" subtitle="Yield efficiency and variance tracking">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-700 uppercase font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-3">Batch #</th>
                <th className="py-3 px-3">Product</th>
                <th className="py-3 px-3">Planned Qty</th>
                <th className="py-3 px-3">Good Output</th>
                <th className="py-3 px-3">Damaged Pouches</th>
                <th className="py-3 px-3">Yield Variance</th>
                <th className="py-3 px-3">Oil Variance</th>
                <th className="py-3 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {runs.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-3 font-mono font-bold text-brand-900">{r.batch_number}</td>
                  <td className="py-3 px-3 text-slate-800">{r.product_name}</td>
                  <td className="py-3 px-3 font-mono">{r.planned_quantity} pkts</td>
                  <td className="py-3 px-3 font-mono font-semibold text-slate-900">{r.actual_good_quantity} pkts</td>
                  <td className="py-3 px-3 font-mono text-rose-600">{r.damaged_quantity} pcs</td>
                  <td className="py-3 px-3 font-mono font-bold">
                    <span className={r.yield_variance_percent < 0 ? 'text-amber-600' : 'text-emerald-600'}>
                      {r.yield_variance_percent > 0 ? `+${r.yield_variance_percent}%` : `${r.yield_variance_percent}%`}
                    </span>
                    {r.is_variance_alert === 1 && (
                      <span className="ml-1 text-[10px] bg-amber-100 text-amber-800 px-1 py-0.2 rounded font-bold">
                        ALERT
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-3 font-mono font-bold">
                    <span className={r.oil_variance_percent > 0 ? 'text-amber-600' : 'text-slate-600'}>
                      {r.oil_variance_percent > 0 ? `+${r.oil_variance_percent}%` : `${r.oil_variance_percent}%`}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <Badge variant="success">{r.status.toUpperCase()}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Record Production Batch Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Record Production Batch Run" maxWidth="lg">
        <form onSubmit={handleRecordBatch} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Target Planned Quantity</label>
              <input
                type="number"
                value={plannedQty}
                onChange={(e) => setPlannedQty(Number(e.target.value))}
                className="w-full text-xs font-mono font-medium border border-slate-300 rounded-lg p-2"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Actual Good Packets Produced</label>
              <input
                type="number"
                value={actualGoodQty}
                onChange={(e) => setActualGoodQty(Number(e.target.value))}
                className="w-full text-xs font-mono font-medium border border-slate-300 rounded-lg p-2"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Damaged Pouches / Wastage</label>
              <input
                type="number"
                value={damagedQty}
                onChange={(e) => setDamagedQty(Number(e.target.value))}
                className="w-full text-xs font-mono font-medium border border-slate-300 rounded-lg p-2"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Cartons Consumed</label>
              <input
                type="number"
                value={cartonsUsed}
                onChange={(e) => setCartonsUsed(Number(e.target.value))}
                className="w-full text-xs font-mono font-medium border border-slate-300 rounded-lg p-2"
                required
              />
            </div>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-3">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Raw Material Actual Issues</h4>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] text-slate-600 mb-1">Flour Issue (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  value={flourActual}
                  onChange={(e) => setFlourActual(Number(e.target.value))}
                  className="w-full text-xs font-mono border border-slate-300 rounded p-1.5"
                  required
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-600 mb-1">Cooking Oil (L)</label>
                <input
                  type="number"
                  step="0.1"
                  value={oilActual}
                  onChange={(e) => setOilActual(Number(e.target.value))}
                  className="w-full text-xs font-mono border border-slate-300 rounded p-1.5"
                  required
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-600 mb-1">Spice Mix (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  value={spiceActual}
                  onChange={(e) => setSpiceActual(Number(e.target.value))}
                  className="w-full text-xs font-mono border border-slate-300 rounded p-1.5"
                  required
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Direct Labour Wages (₹)</label>
              <input
                type="number"
                value={labourExpense}
                onChange={(e) => setLabourExpense(Number(e.target.value))}
                className="w-full text-xs font-mono border border-slate-300 rounded-lg p-2"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Power & Commercial Gas (₹)</label>
              <input
                type="number"
                value={powerExpense}
                onChange={(e) => setPowerExpense(Number(e.target.value))}
                className="w-full text-xs font-mono border border-slate-300 rounded-lg p-2"
              />
            </div>
          </div>

          {/* Real-time Variance Alert Preview */}
          <div
            className={`p-3 rounded-lg border text-xs ${
              isVarianceAlert
                ? 'bg-amber-50 border-amber-300 text-amber-900'
                : 'bg-emerald-50 border-emerald-200 text-emerald-900'
            }`}
          >
            <div className="flex items-center justify-between font-semibold">
              <span>Calculated Yield Variance: {liveYieldVariance}%</span>
              <span>Oil Variance: {Number(liveOilVariance) > 0 ? `+${liveOilVariance}%` : `${liveOilVariance}%`}</span>
            </div>
            {isVarianceAlert && (
              <p className="mt-1 text-[11px] text-amber-700">
                ⚠️ Variance exceeds the 3.0% quality threshold. An audit variance alert will be flagged on the batch.
              </p>
            )}
          </div>

          <div className="pt-2 flex justify-end gap-3 border-t border-slate-100">
            <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Complete & Post Batch
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

