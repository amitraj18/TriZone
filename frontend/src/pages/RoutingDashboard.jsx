import React, { useState, useEffect } from 'react';
import { 
  GitBranch, 
  Shield, 
  ArrowRight, 
  CheckCircle2, 
  Edit3, 
  History, 
  Save, 
  X, 
  AlertTriangle,
  Server
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { updateRoutingRule, fetchRoutingRuleHistory } from '../api/client';

export default function RoutingDashboard({ routingRules, categories, onDataChanged }) {
  const rules = routingRules && routingRules.length > 0 ? routingRules : [];
  const catList = categories && categories.length > 0 ? categories : [];
  const [history, setHistory] = useState([]);
  const [editingRule, setEditingRule] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(null);

  const loadHistory = async () => {
    try {
      const h = await fetchRoutingRuleHistory();
      setHistory(h);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleOpenEdit = (rule) => {
    setEditingRule({
      id: rule.id,
      code: rule.irregularity_code,
      target_authority: rule.target_authority,
      escalation_authority: rule.escalation_authority || 'Chief Superintendent',
      priority: rule.priority,
      reason: ''
    });
    setSaveSuccess(null);
  };

  const handleSaveRule = async (e) => {
    e.preventDefault();
    if (!editingRule) return;
    setIsSaving(true);
    try {
      await updateRoutingRule(editingRule.id, {
        target_authority: editingRule.target_authority,
        escalation_authority: editingRule.escalation_authority,
        priority: editingRule.priority,
        reason: editingRule.reason || 'Administrative routing adjustment.'
      });
      setSaveSuccess(`Rule for ${editingRule.code} updated successfully.`);
      setEditingRule(null);
      if (onDataChanged) onDataChanged();
      loadHistory();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  };

  const authorityDestIps = {
    'Chief Superintendent': '192.168.40.10',
    'Centre Superintendent': '192.168.40.20',
    'Controller of Examinations': '192.168.40.30'
  };

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-orange-50 border border-orange-100 text-orange-600">
              <GitBranch className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900">Examination Authority Routing Architecture (O(1) Explicit Lookup)</h2>
              <p className="text-xs text-slate-500">
                Deterministic statutory jurisdiction table, backup escalation policy, and administrative rule manager
              </p>
            </div>
          </div>
          <span className="text-[11px] font-mono px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md font-semibold">
            Dynamic SQLite Rules
          </span>
        </div>

        {saveSuccess && (
          <div className="mt-3 p-2 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium">
            {saveSuccess}
          </div>
        )}
      </div>

      {/* Explicit Lookup Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Authoritative Routing Table (SQLite routing_rules)</h3>
            <p className="text-xs text-slate-400">Explicit hash key lookup for incident jurisdiction</p>
          </div>
          <span className="text-[11px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            Hash Key: irregularity_code
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
              <tr>
                <th className="py-2.5 px-4">Code</th>
                <th className="py-2.5 px-4">Incident Category</th>
                <th className="py-2.5 px-4">Primary Authority</th>
                <th className="py-2.5 px-4">Destination IP</th>
                <th className="py-2.5 px-4">Escalation Backup</th>
                <th className="py-2.5 px-4">Default Priority</th>
                <th className="py-2.5 px-4 text-right">Admin Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {rules.map((rule) => (
                <tr key={rule.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-orange-600">{rule.irregularity_code}</td>
                  <td className="py-3 px-4 font-semibold text-slate-800">{rule.category_name || rule.irregularity_code}</td>
                  <td className="py-3 px-4">
                    <span className="font-bold text-slate-900">{rule.target_authority}</span>
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-600 text-[11px]">
                    {authorityDestIps[rule.target_authority] || '192.168.40.10'}
                  </td>
                  <td className="py-3 px-4 text-slate-500 font-medium">{rule.escalation_authority || 'Chief Superintendent'}</td>
                  <td className="py-3 px-4">
                    <StatusBadge status={rule.priority} />
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleOpenEdit(rule)}
                      className="px-2.5 py-1 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded text-[11px] font-medium shadow-2xs flex items-center gap-1 ml-auto"
                    >
                      <Edit3 className="w-3 h-3 text-orange-600" />
                      <span>Edit Rule</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit Rule Modal */}
      {editingRule && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <form onSubmit={handleSaveRule} className="bg-white rounded-xl shadow-xl border border-slate-200 max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <h3 className="text-sm font-bold text-slate-900">Modify Routing Rule: {editingRule.code}</h3>
              <button type="button" onClick={() => setEditingRule(null)} className="p-1 text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Primary Target Authority:</label>
                <select
                  value={editingRule.target_authority}
                  onChange={(e) => setEditingRule({ ...editingRule, target_authority: e.target.value })}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900"
                >
                  <option value="Chief Superintendent">Chief Superintendent</option>
                  <option value="Centre Superintendent">Centre Superintendent</option>
                  <option value="Controller of Examinations">Controller of Examinations</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Escalation Backup Authority:</label>
                <select
                  value={editingRule.escalation_authority}
                  onChange={(e) => setEditingRule({ ...editingRule, escalation_authority: e.target.value })}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900"
                >
                  <option value="Chief Superintendent">Chief Superintendent</option>
                  <option value="Centre Superintendent">Centre Superintendent</option>
                  <option value="Controller of Examinations">Controller of Examinations</option>
                  <option value="Campus Medical Officer">Campus Medical Officer</option>
                  <option value="Technical Support Lead">Technical Support Lead</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Default Priority:</label>
                <select
                  value={editingRule.priority}
                  onChange={(e) => setEditingRule({ ...editingRule, priority: e.target.value })}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900"
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Audit Justification / Reason:</label>
                <input
                  type="text"
                  required
                  value={editingRule.reason}
                  onChange={(e) => setEditingRule({ ...editingRule, reason: e.target.value })}
                  placeholder="e.g. Session policy adjustment"
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setEditingRule(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSaving}
                className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-xs font-semibold rounded-lg shadow-sm"
              >
                {isSaving ? 'Updating...' : 'Save Rule'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Modification Audit History */}
      {history.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-5 space-y-3">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-orange-600" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Routing Rule Modification Audit Trail (routing_rule_history)
            </h3>
          </div>

          <div className="overflow-x-auto bg-slate-50 rounded-lg border border-slate-200 text-[11px] font-mono">
            <table className="w-full text-left">
              <thead className="bg-slate-100 text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="py-2 px-3">Timestamp</th>
                  <th className="py-2 px-3">Code</th>
                  <th className="py-2 px-3">Old &rarr; New Target Authority</th>
                  <th className="py-2 px-3">Modified By</th>
                  <th className="py-2 px-3">Justification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {history.map((h, i) => (
                  <tr key={i} className="hover:bg-slate-100/50">
                    <td className="py-2 px-3 text-slate-400">{h.timestamp}</td>
                    <td className="py-2 px-3 font-bold text-orange-600">{h.irregularity_code}</td>
                    <td className="py-2 px-3">
                      <span className="text-slate-500">{h.old_target_authority}</span> &rarr; <strong className="text-slate-900">{h.new_target_authority}</strong>
                    </td>
                    <td className="py-2 px-3 text-slate-700">{h.modified_by}</td>
                    <td className="py-2 px-3 text-slate-600">{h.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Irregularity Categories Catalogue */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3">Institutional Irregularity Classification Standard</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          {catList.map((cat) => (
            <div key={cat.code} className="p-3 rounded-lg border border-slate-100 bg-slate-50/60 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-orange-600">{cat.code}</span>
                  <span className="font-bold text-slate-800">{cat.name}</span>
                </div>
                <p className="text-slate-500 mt-1 text-[11px] leading-relaxed">{cat.description}</p>
              </div>
              <StatusBadge status={cat.default_priority} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
