import React from 'react';
import {
  LayoutDashboard, ShoppingBag, FileText, Factory,
  Boxes, Truck, IndianRupee, BarChart3, ShieldCheck,
  ChevronRight, Sparkles, AlertTriangle
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  varianceAlertCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, varianceAlertCount = 0 }) => {
  const { role } = useAuth();

  const navItems = [
    { id: 'dashboard', label: 'Executive Overview', icon: LayoutDashboard, roles: ['owner', 'admin', 'production', 'auditor'] },
    { id: 'salesman-portal', label: 'Salesman Portal', icon: ShoppingBag, roles: ['salesman', 'owner', 'admin'] },
    { id: 'orders', label: 'Sales Orders', icon: ShoppingBag, roles: ['admin', 'owner', 'auditor'] },
    { id: 'invoices', label: 'GST Invoices & Dispatch', icon: FileText, roles: ['admin', 'owner', 'auditor'] },
    { id: 'production', label: 'Production & BOM', icon: Factory, roles: ['production', 'owner', 'admin', 'auditor'], badge: varianceAlertCount > 0 ? `${varianceAlertCount} Alert` : undefined },
    { id: 'inventory', label: 'Stock & Double Ledger', icon: Boxes, roles: ['production', 'admin', 'owner', 'auditor'] },
    { id: 'purchases', label: 'Purchases & Suppliers', icon: Truck, roles: ['admin', 'owner', 'auditor'] },
    { id: 'costing', label: 'Batch Costing & Margins', icon: IndianRupee, roles: ['owner', 'admin', 'auditor'] },
    { id: 'payments', label: 'Payments & Receivables', icon: IndianRupee, roles: ['admin', 'owner', 'auditor'] },
    { id: 'reports', label: 'Audit & GSTR-1 Reports', icon: BarChart3, roles: ['auditor', 'owner', 'admin'] },
    { id: 'benchmark', label: 'NIT Benchmark Suite', icon: Sparkles, roles: ['owner', 'admin', 'salesman', 'production', 'auditor'], highlight: true },
  ];

  const visibleItems = navItems.filter((item) => item.roles.includes(role));

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col flex-shrink-0 min-h-screen border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold text-lg shadow-sm">
            A
          </div>
          <div>
            <h1 className="font-bold text-white text-sm tracking-wide leading-none">AACHI FOODS</h1>
            <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider font-medium">Order-to-Audit ERP</p>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Core ERP Modules
        </div>
        {visibleItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-brand-600 text-white shadow-sm font-semibold'
                  : item.highlight
                  ? 'bg-amber-500/10 text-amber-300 hover:bg-amber-500/20 border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : item.highlight ? 'text-amber-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="bg-rose-500/20 text-rose-300 text-[10px] font-bold px-1.5 py-0.5 rounded border border-rose-500/30 flex items-center gap-1">
                  <AlertTriangle className="w-2.5 h-2.5" />
                  {item.badge}
                </span>
              )}
              {item.highlight && !isActive && (
                <span className="text-[10px] bg-amber-400 text-slate-950 font-bold px-1.5 py-0.2 rounded">
                  1-Click
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Company GST Metadata Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/60 text-[11px] space-y-1">
        <div className="flex items-center justify-between text-slate-400">
          <span>GSTIN:</span>
          <span className="font-mono text-slate-200 font-medium">33AABCS9876Q1Z2</span>
        </div>
        <div className="flex items-center justify-between text-slate-400">
          <span>State:</span>
          <span className="text-slate-300">Tamil Nadu (33)</span>
        </div>
        <div className="flex items-center justify-between text-slate-400">
          <span>Location:</span>
          <span className="text-slate-300">Thuvakudi, Trichy</span>
        </div>
      </div>
    </aside>
  );
};

