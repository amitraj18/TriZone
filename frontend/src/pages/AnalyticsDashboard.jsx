import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { BarChart3, TrendingUp, PieChart as PieIcon, ShieldAlert, Database } from 'lucide-react';

export default function AnalyticsDashboard({ stats, reports }) {
  const reportList = reports || [];

  // Compute category counts directly from live SQLite reports
  const categoryCounts = {
    'IR01': 0,
    'IR02': 0,
    'IR03': 0,
    'IR04': 0,
    'IR05': 0
  };

  reportList.forEach((r) => {
    if (r.irregularity_code in categoryCounts) {
      categoryCounts[r.irregularity_code]++;
    }
  });

  const categoryChartData = [
    { name: 'IR01 Malpractice', count: categoryCounts['IR01'], color: '#ea580c' },
    { name: 'IR02 Disturbance', count: categoryCounts['IR02'], color: '#eab308' },
    { name: 'IR03 Medical', count: categoryCounts['IR03'], color: '#ef4444' },
    { name: 'IR04 Technical', count: categoryCounts['IR04'], color: '#3b82f6' },
    { name: 'IR05 Missing-Script', count: categoryCounts['IR05'], color: '#8b5cf6' },
  ];

  // Compute status distribution from live SQLite reports
  const statusCounts = {};
  reportList.forEach((r) => {
    const s = r.status || 'SUBMITTED';
    statusCounts[s] = (statusCounts[s] || 0) + 1;
  });

  const statusBarData = Object.keys(statusCounts).map((status) => ({
    status,
    count: statusCounts[status]
  }));

  const hasReports = reportList.length > 0;

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-orange-50 border border-orange-100 text-orange-600">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900">Examination Integrity Telemetry & Distribution Analytics</h2>
              <p className="text-xs text-slate-500">
                Computed directly from live SQLite database records (reports & status history)
              </p>
            </div>
          </div>
          <span className="text-[11px] font-mono px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md flex items-center gap-1.5 font-semibold">
            <Database className="w-3.5 h-3.5 text-orange-600" />
            Source: SQLite Live
          </span>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status Distribution Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Incident Lifecycle Distribution (SQLite)</h3>
              <p className="text-xs text-slate-400">Total volume grouped by current operational status</p>
            </div>
            <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-orange-50 text-orange-700 border border-orange-200">
              {reportList.length} Total Incidents
            </span>
          </div>

          <div className="h-64 w-full">
            {hasReports ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statusBarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="status" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#ffffff', 
                      borderRadius: '8px', 
                      border: '1px solid #e2e8f0', 
                      fontSize: '12px' 
                    }} 
                  />
                  <Bar dataKey="count" fill="#ea580c" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No reports currently recorded in database.
              </div>
            )}
          </div>
        </div>

        {/* Category Breakdown (Pie/Donut) */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Category Proportion</h3>
                <p className="text-xs text-slate-400">Distribution across IR01 &ndash; IR05</p>
              </div>
              <PieIcon className="w-4 h-4 text-slate-400" />
            </div>

            <div className="h-44 w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryChartData}
                    dataKey="count"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={65}
                    paddingAngle={3}
                  >
                    {categoryChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#ffffff', 
                      borderRadius: '8px', 
                      border: '1px solid #e2e8f0', 
                      fontSize: '11px' 
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-1.5 border-t border-slate-100 pt-3">
            {categoryChartData.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-600 font-medium">{item.name}</span>
                </div>
                <span className="font-mono font-bold text-slate-800">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
