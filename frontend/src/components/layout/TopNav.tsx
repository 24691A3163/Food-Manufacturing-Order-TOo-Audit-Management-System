import React from 'react';
import { UserCheck, Sparkles, Shield, User as UserIcon, RefreshCw } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';

interface TopNavProps {
  onRunBenchmark: () => void;
  isBenchmarkRunning: boolean;
}

export const TopNav: React.FC<TopNavProps> = ({ onRunBenchmark, isBenchmarkRunning }) => {
  const { user, role, switchRole } = useAuth();

  const rolesList: { role: UserRole; label: string; desc: string }[] = [
    { role: 'owner', label: 'Owner (Executive)', desc: '360° analytics, margins, stock' },
    { role: 'admin', label: 'Admin (Operations)', desc: 'Order approvals, GST, dispatch' },
    { role: 'salesman', label: 'Salesman (Mobile)', desc: 'Field order booking & status' },
    { role: 'production', label: 'Production Supervisor', desc: 'BOM, batches, variance' },
    { role: 'auditor', label: 'Accountant / Auditor', desc: 'Read-only ledger & reports' },
  ];

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Left: Role Indicator & Context */}
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500">
          <span className="font-semibold text-slate-800">Manufacturing Plant:</span>
          <span>Trichy Unit 1</span>
          <span className="text-slate-300">•</span>
          <span className="font-semibold text-slate-800">Current Period:</span>
          <span>Nov 2026</span>
        </div>
      </div>

      {/* Right: Quick Benchmark Trigger & Role Switcher */}
      <div className="flex items-center gap-4">
        {/* Fast Benchmark Run Action */}
        <button
          onClick={onRunBenchmark}
          disabled={isBenchmarkRunning}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/10 text-amber-800 border border-amber-300 hover:bg-amber-500/20 transition-all shadow-xs disabled:opacity-50"
        >
          <Sparkles className={`w-3.5 h-3.5 text-amber-600 ${isBenchmarkRunning ? 'animate-spin' : ''}`} />
          <span>{isBenchmarkRunning ? 'Executing 16 Steps...' : 'Run Benchmark (1-Click)'}</span>
        </button>

        {/* Interactive Role Switcher for Interview / Evaluation */}
        <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-lg border border-slate-200">
          <Shield className="w-4 h-4 text-slate-500 ml-1.5" />
          <span className="text-xs font-medium text-slate-600 hidden md:inline">Active Role:</span>
          <select
            value={role}
            onChange={(e) => switchRole(e.target.value as UserRole)}
            className="bg-white text-xs font-semibold text-brand-900 border border-slate-200 rounded-md py-1 px-2.5 shadow-2xs focus:outline-none focus:ring-1 focus:ring-brand-500 cursor-pointer"
          >
            {rolesList.map((r) => (
              <option key={r.role} value={r.role}>
                {r.label}
              </option>
            ))}
          </select>
        </div>

        {/* User Identity Pill */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-brand-900 text-white flex items-center justify-center font-bold text-xs">
            {user?.full_name ? user.full_name[0] : 'U'}
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-semibold text-slate-800 leading-tight">{user?.full_name}</p>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-medium">{role}</p>
          </div>
        </div>
      </div>
    </header>
  );
};

