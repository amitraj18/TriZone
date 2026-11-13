import React, { useState } from 'react';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import { 
  AlertTriangle, 
  Clock, 
  FileCheck2, 
  Activity, 
  CheckCircle,
  Eye,
  X,
  ListOrdered
} from 'lucide-react';
import { updateReportStatus, fetchReportDetails } from '../api/client';

export default function UserDashboard({ reports, stats, backendHealth, setActiveTab, onDataChanged }) {
  const [filterCategory, setFilterCategory] = useState('ALL');
  const [selectedReport, setSelectedReport] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  const displayReports = reports && reports.length > 0 ? reports : [];
  const filteredList = displayReports.filter((r) => {
    if (filterCategory === 'ALL') return true;
    if (filterCategory === 'QUEUED') return r.status === 'QUEUED';
    return r.irregularity_code === filterCategory;
  });

  const handleOpenDetails = async (reportId) => {
    try {
      const details = await fetchReportDetails(reportId);
      setSelectedReport(details);
      setDetailModalOpen(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAdvanceStatus = async (reportId, newStatus) => {
    try {
      setIsUpdatingStatus(true);
      await updateReportStatus(reportId, newStatus, 'SUPERINTENDENT', `Incident transitioned to ${newStatus}.`);
      if (onDataChanged) onDataChanged();
      if (selectedReport && selectedReport.id === reportId) {
        const refreshed = await fetchReportDetails(reportId);
        setSelectedReport(refreshed);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-gradient-to-r from-orange-50 via-amber-50 to-white border border-orange-200/80 rounded-xl p-4 flex items-start justify-between shadow-xs">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-orange-500 text-white rounded-lg mt-0.5 shadow-sm">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900">Institutional Examination Incident Operations (Live Production)</h2>
            <p className="text-xs text-slate-600 mt-0.5">
              Live SQLite repository, deterministic priority queues, and statutory authority dispatch pipeline.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setActiveTab('report_submission')}
            className="px-3 py-1.5 bg-orange-600 hover:bg-orange-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
          >
            Submit Incident
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Incidents"
          value={stats ? String(stats.active_incidents).padStart(2, '0') : '00'}
          change="Pending authority action"
          trend="warning"
          subtext="In Progress or Assigned"
          icon={AlertTriangle}
          color="orange"
        />
        <StatCard
          title="Total Reports Logged"
          value={stats ? String(stats.total_reports).padStart(2, '0') : '00'}
          change="Database records"
          trend="neutral"
          subtext="Complete session repository"
          icon={FileCheck2}
          color="blue"
        />
        <StatCard
          title="Critical Alerts"
          value={stats ? String(stats.critical_alerts).padStart(2, '0') : '00'}
          change="High priority tier"
          trend="warning"
          subtext="Medical / Missing script"
          icon={Activity}
          color="rose"
        />
        <StatCard
          title="Resolved Cases"
          value={stats ? String(stats.resolved_incidents).padStart(2, '0') : '00'}
          change="Closed & Verified"
          trend="up"
          subtext="Integrity sealed"
          icon={Clock}
          color="emerald"
        />
      </div>

      {/* Incident Feed Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs flex flex-col">
        <div className="p-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Exam Hall Incidents (Live SQLite Feed)</h3>
            <p className="text-xs text-slate-400">All reports processed through TOC DFA and CN LPM routing</p>
          </div>

          {/* Filter Tabs */}
          <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg text-xs">
            {['ALL', 'IR01', 'IR02', 'IR03', 'IR04', 'IR05', 'QUEUED'].map((code) => (
              <button
                key={code}
                onClick={() => setFilterCategory(code)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${
                  filterCategory === code 
                    ? 'bg-white text-slate-800 shadow-2xs font-semibold' 
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                {code === 'ALL' ? 'All Codes' : code}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
              <tr>
                <th className="py-2.5 px-4">UID</th>
                <th className="py-2.5 px-4">Invigilator</th>
                <th className="py-2.5 px-4">Category</th>
                <th className="py-2.5 px-4">Zone / Hall</th>
                <th className="py-2.5 px-4">Authority & Handler</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filteredList.map((rep) => (
                <tr key={rep.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-slate-800">{rep.report_uid}</td>
                  <td className="py-3 px-4">
                    <div className="text-slate-800 font-semibold">{rep.invigilator_id}</div>
                    <div className="text-[10px] text-slate-400">{rep.invigilator_name || 'Invigilator'}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-semibold text-slate-700">{rep.category_name || rep.irregularity_code}</span>
                    <span className="ml-1 text-[10px] font-mono text-slate-400">({rep.irregularity_code})</span>
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-600">{rep.hall_id}</td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-800">{rep.target_authority || 'Chief Superintendent'}</div>
                    <div className="text-[10px] text-slate-500">{rep.handler_name ? `${rep.handler_name} (${rep.assignment_type || 'PRIMARY'})` : 'Waiting in Queue'}</div>
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={rep.status} />
                  </td>
                  <td className="py-3 px-4 text-right space-x-1.5">
                    <button
                      onClick={() => handleOpenDetails(rep.id)}
                      className="px-2 py-1 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded text-[11px] font-medium shadow-2xs"
                      title="Inspect full details"
                    >
                      Inspect
                    </button>
                    {rep.status === 'ASSIGNED' && (
                      <button
                        onClick={() => handleAdvanceStatus(rep.id, 'IN_PROGRESS')}
                        disabled={isUpdatingStatus}
                        className="px-2 py-1 bg-blue-50 border border-blue-200 hover:bg-blue-100 text-blue-700 rounded text-[11px] font-medium"
                      >
                        Start
                      </button>
                    )}
                    {rep.status === 'IN_PROGRESS' && (
                      <button
                        onClick={() => handleAdvanceStatus(rep.id, 'RESOLVED')}
                        disabled={isUpdatingStatus}
                        className="px-2 py-1 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 text-emerald-700 rounded text-[11px] font-medium"
                      >
                        Resolve
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Inspection Modal */}
      {detailModalOpen && selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl shadow-xl border border-slate-200 max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Incident Dossier: {selectedReport.report_uid}</h3>
                <p className="text-xs text-slate-500">Submitted at {selectedReport.created_at}</p>
              </div>
              <button onClick={() => setDetailModalOpen(false)} className="p-1 rounded-md text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Status</div>
                <div className="pt-1"><StatusBadge status={selectedReport.status} /></div>
              </div>
              <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Severity</div>
                <div className="font-bold text-slate-800 mt-1">{selectedReport.severity}</div>
              </div>
              <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Zone & Terminal</div>
                <div className="font-mono font-bold text-slate-800 mt-1">{selectedReport.hall_id}</div>
              </div>
              <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Source IP</div>
                <div className="font-mono text-slate-700 mt-1">{selectedReport.source_ip}</div>
              </div>
            </div>

            {/* Factual Description */}
            <div className="text-xs space-y-1">
              <div className="font-bold text-slate-700">Description:</div>
              <p className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-slate-800 leading-relaxed">
                {selectedReport.description}
              </p>
            </div>

            {/* Status Transition History */}
            {selectedReport.status_history && (
              <div className="text-xs space-y-1.5">
                <div className="font-bold text-slate-700">Audit Trail (status_history):</div>
                <div className="space-y-1 bg-slate-50 p-2.5 rounded-lg border border-slate-200 font-mono text-[11px]">
                  {selectedReport.status_history.map((h, i) => (
                    <div key={i} className="flex items-center justify-between py-0.5 border-b border-slate-100 last:border-none">
                      <span>{h.old_status} &rarr; <strong className="text-slate-900">{h.new_status}</strong></span>
                      <span className="text-slate-400">{h.timestamp}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Close Button */}
            <div className="flex justify-end pt-3 border-t border-slate-100">
              <button
                onClick={() => setDetailModalOpen(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-lg"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
