import React from 'react';
import { 
  LayoutDashboard, 
  FileEdit, 
  ShieldAlert, 
  GitBranch, 
  Network, 
  BarChart3,
  CheckCircle2,
  AlertCircle,
  School,
  Wifi
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, backendHealth }) {
  const navItems = [
    { id: 'user_dashboard', label: 'User Dashboard', icon: LayoutDashboard, tag: 'Live' },
    { id: 'report_submission', label: 'Report Submission', icon: FileEdit, tag: 'TOC DFA' },
    { id: 'handler_dashboard', label: 'Handler Dashboard', icon: ShieldAlert, tag: 'Dispatch' },
    { id: 'routing_management', label: 'Routing Management', icon: GitBranch, tag: 'Rules' },
    { id: 'network_management', label: 'Network Management', icon: Network, tag: 'CN LPM' },
    { id: 'analytics_dashboard', label: 'Analytics Dashboard', icon: BarChart3, tag: 'Trends' },
  ];

  const isOnline = backendHealth?.status === 'healthy';

  return (
    <aside className="w-64 bg-white border-r border-slate-200/90 flex flex-col fixed inset-y-0 left-0 z-30 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-5 border-b border-slate-200/80 gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-orange-600 to-amber-500 flex items-center justify-center text-white shadow-sm shadow-orange-500/20">
          <School className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-slate-900 tracking-tight text-sm">IRIS</span>
            <span className="text-[10px] font-semibold bg-orange-100 text-orange-800 px-1.5 py-0.2 rounded-md">v1.0</span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">Exam Irregularity Dispatch</p>
        </div>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-2 pb-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
          Modules & Controls
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                isActive 
                  ? 'bg-orange-50 text-orange-700 font-semibold border border-orange-200/60 shadow-xs' 
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <div className="flex items-center gap-2.5 truncate">
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-orange-600' : 'text-slate-400'}`} />
                <span className="truncate">{item.label}</span>
              </div>
              <span className={`text-[9.5px] font-mono px-1.5 py-0.5 rounded ${
                isActive ? 'bg-orange-100/80 text-orange-800 font-bold' : 'bg-slate-100 text-slate-500'
              }`}>
                {item.tag}
              </span>
            </button>
          );
        })}
      </div>

      {/* System Status & Session Footer */}
      <div className="p-3 border-t border-slate-200/80 bg-slate-50/50 space-y-2">
        <div className="bg-white rounded-lg p-2.5 border border-slate-200/70 shadow-2xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs font-medium text-slate-700">
              <Wifi className="w-3.5 h-3.5 text-slate-400" />
              <span>Backend API</span>
            </div>
            <div className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
              <span className={`text-[11px] font-mono font-medium ${isOnline ? 'text-emerald-700' : 'text-rose-700'}`}>
                {isOnline ? 'Connected' : 'Offline'}
              </span>
            </div>
          </div>
          <div className="mt-1 text-[10px] text-slate-400 font-mono">
            {backendHealth?.database ? `DB: ${backendHealth.database}` : 'SQLite: Initializing'}
          </div>
        </div>

        <div className="px-2 py-1 text-[11px] text-slate-500 flex items-center justify-between">
          <span>Active Session</span>
          <span className="font-semibold text-slate-700 font-mono">NOV-2026-EXAM</span>
        </div>
      </div>
    </aside>
  );
}

