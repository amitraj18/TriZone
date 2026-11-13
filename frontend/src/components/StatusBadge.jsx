import React from 'react';

export default function StatusBadge({ status, type = 'status' }) {
  const norm = (status || '').toUpperCase().replace('-', '_');

  const getStyle = () => {
    switch (norm) {
      case 'CRITICAL':
        return 'bg-red-50 text-red-700 border-red-200 ring-red-600/10';
      case 'HIGH':
        return 'bg-orange-50 text-orange-700 border-orange-200 ring-orange-600/10';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-700 border-amber-200 ring-amber-600/10';
      case 'LOW':
        return 'bg-slate-100 text-slate-700 border-slate-200 ring-slate-600/10';
      case 'RESOLVED':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200 ring-emerald-600/10';
      case 'IN_PROGRESS':
        return 'bg-blue-50 text-blue-700 border-blue-200 ring-blue-600/10';
      case 'ASSIGNED':
        return 'bg-purple-50 text-purple-700 border-purple-200 ring-purple-600/10';
      case 'SUBMITTED':
      default:
        return 'bg-slate-100 text-slate-800 border-slate-300 ring-slate-600/10';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStyle()}`}>
      <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-current opacity-70"></span>
      {status || 'Unknown'}
    </span>
  );
}

