import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  UserCheck, 
  Clock, 
  AlertTriangle, 
  Layers, 
  UserPlus, 
  Power, 
  Plus, 
  Minus, 
  ListOrdered,
  RefreshCw
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { 
  updateHandlerAvailability, 
  updateHandlerCapacity, 
  fetchDispatchQueue,
  fetchDispatchLogs 
} from '../api/client';

export default function HandlerDashboard({ handlers, onDataChanged }) {
  const handlerList = handlers && handlers.length > 0 ? handlers : [];
  const [queue, setQueue] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState(null);

  const loadQueueAndLogs = async () => {
    try {
      const [q, l] = await Promise.all([
        fetchDispatchQueue(),
        fetchDispatchLogs()
      ]);
      setQueue(q);
      setLogs(l);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadQueueAndLogs();
  }, []);

  const handleToggleAvailability = async (handlerId, currentVal) => {
    try {
      setIsLoading(true);
      const res = await updateHandlerAvailability(handlerId, !currentVal);
      setActionMessage(res.message);
      if (onDataChanged) onDataChanged();
      loadQueueAndLogs();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdjustCapacity = async (handlerId, currentCap, delta) => {
    const newCap = Math.max(1, currentCap + delta);
    try {
      setIsLoading(true);
      const res = await updateHandlerCapacity(handlerId, newCap);
      setActionMessage(res.message);
      if (onDataChanged) onDataChanged();
      loadQueueAndLogs();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-orange-50 border border-orange-100 text-orange-600">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900">Incident Dispatch, Handler Capacity & Priority Queue</h2>
              <p className="text-xs text-slate-500">
                Real-time workload management, operational availability switches, and deterministic queue processor
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => { loadQueueAndLogs(); if (onDataChanged) onDataChanged(); }}
              className="text-xs px-2.5 py-1.5 bg-slate-50 border border-slate-200 hover:bg-slate-100 text-slate-700 rounded-md font-medium flex items-center gap-1.5 shadow-2xs"
            >
              <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
              <span>Refresh Queue</span>
            </button>
          </div>
        </div>

        {actionMessage && (
          <div className="mt-3 p-2 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium">
            {actionMessage}
          </div>
        )}
      </div>

      {/* Handlers Capacity Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {handlerList.map((h) => {
          const loadPercent = Math.min(100, Math.round((h.current_load / (h.capacity || 1)) * 100));
          const isFull = h.current_load >= h.capacity;

          return (
            <div key={h.id} className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-xs space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-1.5">
                    <h3 className="text-xs font-bold text-slate-900">{h.name}</h3>
                    <span className="text-[10px] font-mono text-slate-400">({h.handler_uid})</span>
                  </div>
                  <p className="text-[11px] text-orange-700 font-medium mt-0.5">{h.role}</p>
                </div>

                {/* Availability Toggle */}
                <button
                  onClick={() => handleToggleAvailability(h.id, Boolean(h.is_available))}
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium transition-colors ${
                    h.is_available && !isFull 
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100' 
                      : !h.is_available
                      ? 'bg-slate-100 text-slate-600 border border-slate-200 hover:bg-slate-200'
                      : 'bg-rose-50 text-rose-700 border border-rose-200'
                  }`}
                  title="Click to toggle availability"
                >
                  <Power className="w-3 h-3" />
                  <span>{h.is_available ? (isFull ? 'Full' : 'Online') : 'Offline'}</span>
                </button>
              </div>

              {/* Department & Contact */}
              <div className="text-[11px] text-slate-500 flex items-center justify-between">
                <span>Dept: <span className="font-semibold text-slate-700">{h.department}</span></span>
                <span className="font-mono text-slate-400">{h.contact || 'Internal'}</span>
              </div>

              {/* Load Bar */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-500 font-medium">Active Incidents</span>
                  <span className="font-mono font-bold text-slate-800">
                    {h.current_load} / {h.capacity} max
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${
                      loadPercent >= 90 ? 'bg-rose-500' : loadPercent >= 60 ? 'bg-amber-500' : 'bg-orange-500'
                    }`}
                    style={{ width: `${loadPercent}%` }}
                  />
                </div>
              </div>

              {/* Capacity Adjusters */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px]">
                <span className="text-slate-400">Max Capacity:</span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleAdjustCapacity(h.id, h.capacity, -1)}
                    disabled={h.capacity <= 1}
                    className="p-1 rounded bg-slate-50 border border-slate-200 hover:bg-slate-100 text-slate-600 disabled:opacity-30"
                    title="Decrease capacity limit"
                  >
                    <Minus className="w-3 h-3" />
                  </button>
                  <span className="font-mono font-bold px-2 text-slate-800">{h.capacity}</span>
                  <button
                    onClick={() => handleAdjustCapacity(h.id, h.capacity, 1)}
                    className="p-1 rounded bg-slate-50 border border-slate-200 hover:bg-slate-100 text-slate-600"
                    title="Increase capacity limit"
                  >
                    <Plus className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Deterministic Priority Queue Display */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ListOrdered className="w-4 h-4 text-orange-600" />
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">Deterministic Priority Dispatch Queue</h3>
              <p className="text-xs text-slate-400">Ordered by Priority (CRITICAL &gt; HIGH &gt; MEDIUM &gt; LOW), then Submission Timestamp</p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-orange-100 text-orange-800">
            {queue.length} Pending
          </span>
        </div>

        {queue.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-400">
            No incidents currently waiting in queue. All incoming reports have been allocated to available handlers.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
                <tr>
                  <th className="py-2 px-4">Position</th>
                  <th className="py-2 px-4">Report UID</th>
                  <th className="py-2 px-4">Target Authority</th>
                  <th className="py-2 px-4">Category</th>
                  <th className="py-2 px-4">Priority Tier</th>
                  <th className="py-2 px-4">Zone / Hall</th>
                  <th className="py-2 px-4">Submitted At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {queue.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-2.5 px-4 font-mono font-bold text-orange-600">#{item.queue_position}</td>
                    <td className="py-2.5 px-4 font-mono font-bold text-slate-900">{item.report_uid}</td>
                    <td className="py-2.5 px-4 font-semibold text-slate-800">{item.target_authority}</td>
                    <td className="py-2.5 px-4">{item.category_name || item.irregularity_code}</td>
                    <td className="py-2.5 px-4"><StatusBadge status={item.severity} /></td>
                    <td className="py-2.5 px-4 font-mono text-slate-600">{item.hall_id}</td>
                    <td className="py-2.5 px-4 font-mono text-slate-400 text-[11px]">{item.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
