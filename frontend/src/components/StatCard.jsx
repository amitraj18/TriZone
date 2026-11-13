import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export default function StatCard({ title, value, change, trend = 'neutral', subtext, icon: Icon, color = 'orange' }) {
  const getAccent = () => {
    switch (color) {
      case 'orange':
        return 'text-orange-600 bg-orange-50 border-orange-100';
      case 'rose':
        return 'text-rose-600 bg-rose-50 border-rose-100';
      case 'blue':
        return 'text-blue-600 bg-blue-50 border-blue-100';
      case 'emerald':
        return 'text-emerald-600 bg-emerald-50 border-emerald-100';
      default:
        return 'text-slate-600 bg-slate-50 border-slate-100';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm p-5 hover:shadow transition-shadow duration-150">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${getAccent()}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-slate-900">{value}</span>
        {change && (
          <span className={`inline-flex items-center text-xs font-medium ${
            trend === 'up' ? 'text-emerald-600' : trend === 'warning' ? 'text-amber-600' : 'text-slate-500'
          }`}>
            {trend === 'up' && <ArrowUpRight className="w-3 h-3 mr-0.5" />}
            {trend === 'warning' && <ArrowDownRight className="w-3 h-3 mr-0.5" />}
            {trend === 'neutral' && <Minus className="w-3 h-3 mr-0.5" />}
            {change}
          </span>
        )}
      </div>

      {subtext && (
        <p className="mt-1 text-xs text-slate-400">{subtext}</p>
      )}
    </div>
  );
}

