import React, { useState, useEffect } from 'react';
import {
  Boxes, Layers, FileSpreadsheet, Download, RefreshCw,
  Search, ArrowDownRight, ArrowUpRight, ShieldCheck, History
} from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { api } from '../../services/api';
import { StockDashboard, StockMovement } from '../../types';

export const InventoryManagement: React.FC = () => {
  const [dashboard, setDashboard] = useState<StockDashboard | null>(null);
  const [ledger, setLedger] = useState<StockMovement[]>([]);
  const [activeTab, setActiveTab] = useState<'summary' | 'ledger' | 'raw' | 'packaging' | 'finished'>('summary');
  const [itemTypeFilter, setItemTypeFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [dashRes, ledgerRes] = await Promise.all([
        api.getStockDashboard(),
        api.getStockLedger(itemTypeFilter || undefined),
      ]);
      setDashboard(dashRes);
      setLedger(ledgerRes);
    } catch (e) {
      console.error('Failed to load inventory', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [itemTypeFilter]);

  if (!dashboard) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Export */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Inventory & Transaction Stock Ledger</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Strict transaction-sourced double-entry ledger. Zero manual balance overrides allowed.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <a
            href={api.getStockLedgerCsvUrl()}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 shadow-2xs"
          >
            <Download className="w-3.5 h-3.5 text-brand-900" /> Export Stock Ledger (CSV)
          </a>
        </div>
      </div>

      {/* Valuation Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-xs font-medium text-slate-500 uppercase">Raw Materials Valuation</p>
          <p className="text-xl font-bold font-mono text-slate-900 mt-1">
            ₹ {Number(dashboard.total_raw_valuation).toLocaleString()}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5">Weighted-average valuation</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-xs font-medium text-slate-500 uppercase">Packaging Valuation</p>
          <p className="text-xl font-bold font-mono text-slate-900 mt-1">
            ₹ {Number(dashboard.total_packaging_valuation).toLocaleString()}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5">Pouches & Cartons</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-xs font-medium text-slate-500 uppercase">Finished Goods Valuation</p>
          <p className="text-xl font-bold font-mono text-brand-900 mt-1">
            ₹ {Number(dashboard.total_fg_valuation).toLocaleString()}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5">Murukku 200g @ ₹50</p>
        </div>
        <div className="bg-brand-950 text-white rounded-xl p-4 shadow-sm">
          <p className="text-xs font-medium text-slate-300 uppercase">Total Inventory Asset Value</p>
          <p className="text-xl font-bold font-mono text-amber-400 mt-1">
            ₹ {Number(dashboard.total_inventory_valuation).toLocaleString()}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5">Consolidated book value</p>
        </div>
      </div>

      {/* Module Tabs */}
      <div className="border-b border-slate-200 flex gap-4 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('summary')}
          className={`pb-2.5 transition-colors ${
            activeTab === 'summary' ? 'border-b-2 border-brand-900 text-brand-900' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Warehouse Stock Levels
        </button>
        <button
          onClick={() => setActiveTab('ledger')}
          className={`pb-2.5 transition-colors flex items-center gap-1.5 ${
            activeTab === 'ledger' ? 'border-b-2 border-brand-900 text-brand-900' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          <History className="w-3.5 h-3.5" />
          Audit Stock Ledger ({ledger.length})
        </button>
      </div>

      {activeTab === 'summary' && (
        <div className="space-y-6">
          {/* Raw Materials Table */}
          <Card title="Raw Materials Inventory" subtitle="Flour, Cooking Oil, Salt & Spices">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Item Name</th>
                    <th className="py-2.5 px-3">Code</th>
                    <th className="py-2.5 px-3">Current Stock</th>
                    <th className="py-2.5 px-3">Weighted Avg Cost</th>
                    <th className="py-2.5 px-3">Valuation (₹)</th>
                    <th className="py-2.5 px-3">Stock Health</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {dashboard.raw_materials.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-50">
                      <td className="py-3 px-3 font-semibold text-slate-900">{r.name}</td>
                      <td className="py-3 px-3 font-mono text-slate-500">{r.code}</td>
                      <td className="py-3 px-3 font-mono font-bold text-slate-900">
                        {r.current_stock} {r.unit}
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-600">₹ {Number(r.unit_valuation).toFixed(4)}</td>
                      <td className="py-3 px-3 font-mono font-semibold">₹ {Number(r.total_valuation).toLocaleString()}</td>
                      <td className="py-3 px-3">
                        <Badge variant={r.is_low_stock ? 'danger' : 'success'}>
                          {r.is_low_stock ? 'LOW STOCK' : 'ADEQUATE'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Packaging Materials Table */}
          <Card title="Packaging Materials Inventory" subtitle="Pouches & Cartons">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Item Name</th>
                    <th className="py-2.5 px-3">Code</th>
                    <th className="py-2.5 px-3">Current Stock</th>
                    <th className="py-2.5 px-3">Unit Cost</th>
                    <th className="py-2.5 px-3">Valuation (₹)</th>
                    <th className="py-2.5 px-3">Stock Health</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {dashboard.packaging_materials.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-50">
                      <td className="py-3 px-3 font-semibold text-slate-900">{p.name}</td>
                      <td className="py-3 px-3 font-mono text-slate-500">{p.code}</td>
                      <td className="py-3 px-3 font-mono font-bold text-slate-900">
                        {p.current_stock} {p.unit}
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-600">₹ {Number(p.unit_valuation).toFixed(2)}</td>
                      <td className="py-3 px-3 font-mono font-semibold">₹ {Number(p.total_valuation).toLocaleString()}</td>
                      <td className="py-3 px-3">
                        <Badge variant={p.is_low_stock ? 'danger' : 'success'}>
                          {p.is_low_stock ? 'LOW STOCK' : 'ADEQUATE'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Finished Goods Table */}
          <Card title="Finished Goods Inventory" subtitle="Packaged goods ready for delivery">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 uppercase font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Product Name</th>
                    <th className="py-2.5 px-3">SKU</th>
                    <th className="py-2.5 px-3">Current Stock</th>
                    <th className="py-2.5 px-3">Selling Price</th>
                    <th className="py-2.5 px-3">Inventory Valuation (₹)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {dashboard.finished_goods.map((fg) => (
                    <tr key={fg.id} className="hover:bg-slate-50">
                      <td className="py-3 px-3 font-semibold text-slate-900">{fg.name}</td>
                      <td className="py-3 px-3 font-mono text-slate-500">{fg.code}</td>
                      <td className="py-3 px-3 font-mono font-bold text-brand-900 text-sm">
                        {fg.current_stock} packets
                      </td>
                      <td className="py-3 px-3 font-mono">₹ {Number(fg.unit_valuation).toFixed(2)}</td>
                      <td className="py-3 px-3 font-mono font-bold">₹ {Number(fg.total_valuation).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'ledger' && (
        <Card title="Transaction Stock Movement Ledger" subtitle="Immutable audit trail of every inventory movement">
          <div className="mb-4 flex items-center gap-3">
            <span className="text-xs text-slate-500">Filter by category:</span>
            <select
              value={itemTypeFilter}
              onChange={(e) => setItemTypeFilter(e.target.value)}
              className="text-xs border border-slate-300 rounded-md p-1.5 bg-white"
            >
              <option value="">All Categories</option>
              <option value="raw">Raw Materials Only</option>
              <option value="packaging">Packaging Materials Only</option>
              <option value="finished_good">Finished Goods Only</option>
            </select>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 uppercase font-semibold text-[11px] border-b border-slate-200">
                <tr>
                  <th className="py-3 px-3">Timestamp</th>
                  <th className="py-3 px-3">Item Description</th>
                  <th className="py-3 px-3">Type</th>
                  <th className="py-3 px-3">Movement</th>
                  <th className="py-3 px-3">Qty</th>
                  <th className="py-3 px-3">Source Document</th>
                  <th className="py-3 px-3">Running Balance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {ledger.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3 text-slate-500 text-[11px]">
                      {new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-900">{m.item_name}</td>
                    <td className="py-3 px-3 text-slate-500 uppercase text-[10px]">{m.item_type}</td>
                    <td className="py-3 px-3">
                      <span
                        className={`inline-flex items-center gap-1 font-bold ${
                          m.movement_type === 'in' ? 'text-emerald-700' : 'text-rose-700'
                        }`}
                      >
                        {m.movement_type === 'in' ? <ArrowDownRight className="w-3.5 h-3.5" /> : <ArrowUpRight className="w-3.5 h-3.5" />}
                        {m.movement_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-slate-900">{m.quantity}</td>
                    <td className="py-3 px-3 font-mono text-slate-600">
                      {m.source_document_type} ({m.source_document_id || 'Direct'})
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-brand-900">{m.running_balance}</td>
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

