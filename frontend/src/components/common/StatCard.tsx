import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  color?: 'blue' | 'emerald' | 'amber' | 'rose' | 'purple';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = 'blue',
}) => {
  const colorStyles = {
    blue: 'bg-blue-50 text-brand-900 border-blue-100',
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    amber: 'bg-amber-50 text-amber-700 border-amber-100',
    rose: 'bg-rose-50 text-rose-700 border-rose-100',
    purple: 'bg-purple-50 text-purple-700 border-purple-100',
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow transition-shadow">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{title}</p>
        <div className={`p-2 rounded-lg border ${colorStyles[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3">
        <h4 className="text-2xl font-bold text-slate-900">{value}</h4>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        {trend && (
          <div className="flex items-center gap-1 mt-2 text-xs">
            <span className={trend.isPositive ? 'text-emerald-600 font-semibold' : 'text-rose-600 font-semibold'}>
              {trend.value}
            </span>
            <span className="text-slate-400">vs benchmark target</span>
          </div>
        )}
      </div>
    </div>
  );
};

