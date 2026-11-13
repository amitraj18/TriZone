import React, { useState } from 'react';
import { 
  Send, 
  AlertCircle, 
  CheckCircle2, 
  ShieldAlert, 
  Cpu, 
  Network, 
  Clock, 
  ArrowRight,
  FileCheck2,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  Zap,
  Sliders
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import DfaVisualizer from '../components/DfaVisualizer';
import { submitReport, validateIdentifiers } from '../api/client';

export default function ReportSubmission({ categories, onReportSubmitted }) {
  const [formData, setFormData] = useState({
    invigilator_id: 'INVCSE0001',
    irregularity_code: 'IR01',
    hall_id: 'HALL-401',
    student_roll: '21CS042',
    severity: 'HIGH',
    description: 'Student attempting unauthorized communication during Distributed Systems session.',
    source_ip: '192.168.10.45',
    is_emergency: false,
    override_reason: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [submissionError, setSubmissionError] = useState(null);
  const [prevalResult, setPrevalResult] = useState(null);
  const [showDfaTrace, setShowDfaTrace] = useState(false);
  const [showInteractiveDfa, setShowInteractiveDfa] = useState(true);

  const presets = [
    {
      label: 'Preset 1: CSE Hall (IR01 Malpractice)',
      data: {
        invigilator_id: 'INVCSE0001',
        irregularity_code: 'IR01',
        hall_id: 'HALL-401',
        student_roll: '21CS042',
        severity: 'HIGH',
        description: 'Micro-cheat sheet hidden inside calculator casing during Computer Architecture examination.',
        source_ip: '192.168.10.45',
        is_emergency: false,
        override_reason: ''
      }
    },
    {
      label: 'Preset 2: Specialized Lab (IR04 Technical /25 Subnet)',
      data: {
        invigilator_id: 'INVCSE0002',
        irregularity_code: 'IR04',
        hall_id: 'LAB-3',
        student_roll: '',
        severity: 'MEDIUM',
        description: 'Terminal 14 monitor flicker and intermittent keyboard disconnect in Specialized Lab.',
        source_ip: '192.168.10.134',
        is_emergency: false,
        override_reason: ''
      }
    },
    {
      label: 'Preset 3: ECE Hall (IR03 Medical Emergency)',
      data: {
        invigilator_id: 'INVECE0001',
        irregularity_code: 'IR03',
        hall_id: 'HALL-204',
        student_roll: '21EC019',
        severity: 'CRITICAL',
        description: 'Candidate suffered acute breathing distress requiring immediate medical attention.',
        source_ip: '192.168.20.12',
        is_emergency: true,
        override_reason: 'Severe medical emergency in exam room'
      }
    },
    {
      label: 'Preset 4: EEE Hall (IR05 Missing-Script Audit)',
      data: {
        invigilator_id: 'INVEEE0001',
        irregularity_code: 'IR05',
        hall_id: 'HALL-102',
        student_roll: '21EE088',
        severity: 'HIGH',
        description: 'Discrepancy in collected main booklet serial counts vs attendance sheet.',
        source_ip: '192.168.30.8',
        is_emergency: false,
        override_reason: ''
      }
    }
  ];

  const handleLiveCheck = async () => {
    try {
      const res = await validateIdentifiers(formData.invigilator_id, formData.irregularity_code);
      setPrevalResult(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmissionError(null);
    setSubmissionResult(null);

    try {
      const res = await submitReport(formData);
      setSubmissionResult(res);
      if (onReportSubmitted) onReportSubmitted();
    } catch (err) {
      console.error('Submission failed:', err);
      setSubmissionError(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Info */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-orange-50 border border-orange-100 text-orange-600">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900">Exam Hall Irregularity Intake Terminal</h2>
              <p className="text-xs text-slate-500">
                End-to-End Pipeline: TOC Automata Validation &rarr; CN Longest Prefix Match Routing &rarr; Deterministic Dispatch
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowInteractiveDfa(!showInteractiveDfa)}
              className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 flex items-center gap-1.5"
            >
              <Cpu className="w-3.5 h-3.5 text-orange-600" />
              <span>{showInteractiveDfa ? 'Hide' : 'Show'} Interactive DFA Simulator</span>
            </button>
            <span className="text-[11px] font-mono px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md font-semibold">
              Pipeline: 100% Active
            </span>
          </div>
        </div>
      </div>

      {/* Interactive Automata Theory DFA State Machine Visualizer */}
      {showInteractiveDfa && (
        <DfaVisualizer 
          initialInvigilatorId={formData.invigilator_id} 
          initialIrregularityCode={formData.irregularity_code} 
        />
      )}

      {/* Preset Fillers */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-slate-400 font-medium">Quick Presets:</span>
        {presets.map((p, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setFormData(p.data);
              setSubmissionResult(null);
              setSubmissionError(null);
              setPrevalResult(null);
            }}
            className="text-xs font-medium px-2.5 py-1 bg-white border border-slate-200 rounded-md hover:bg-slate-50 text-slate-700 shadow-2xs transition-colors"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit} className="bg-white border border-slate-200/80 rounded-xl p-6 shadow-xs space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Invigilator ID */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-700">
                Invigilator ID <span className="text-orange-600">*</span>
              </label>
              <button
                type="button"
                onClick={handleLiveCheck}
                className="text-[10px] text-orange-600 hover:text-orange-700 font-medium flex items-center gap-1"
              >
                <Cpu className="w-3 h-3" /> Test TOC Validation
              </button>
            </div>
            <input
              type="text"
              required
              value={formData.invigilator_id}
              onChange={(e) => setFormData({ ...formData, invigilator_id: e.target.value.toUpperCase() })}
              placeholder="e.g. INVCSE0001, INVECE0001, INVME0001"
              className="w-full text-xs font-mono px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-900"
            />
            <p className="mt-1 text-[11px] text-slate-400">
              Grammar: <span className="font-mono font-semibold text-slate-600">INV(CSE|ECE|EEE|CIV|ME|MECH)[0-9]{4}</span>
            </p>
          </div>

          {/* Irregularity Code */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Irregularity Code <span className="text-orange-600">*</span>
            </label>
            <select
              value={formData.irregularity_code}
              onChange={(e) => setFormData({ ...formData, irregularity_code: e.target.value })}
              className="w-full text-xs font-mono px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-900"
            >
              <option value="IR01">IR01 – Malpractice (Chief Superintendent)</option>
              <option value="IR02">IR02 – Disturbance (Centre Superintendent)</option>
              <option value="IR03">IR03 – Medical Emergency (Chief Superintendent)</option>
              <option value="IR04">IR04 – Technical Interruption (Centre Superintendent)</option>
              <option value="IR05">IR05 – Missing-Script Audit (Controller of Examinations)</option>
            </select>
            <p className="mt-1 text-[11px] text-slate-400">
              Restricted to authorized set <span className="font-mono font-semibold text-slate-600">&#123;IR01, IR02, IR03, IR04, IR05&#125;</span>
            </p>
          </div>

          {/* Hall ID */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Examination Zone / Hall <span className="text-orange-600">*</span>
            </label>
            <select
              value={formData.hall_id}
              onChange={(e) => {
                const h = e.target.value;
                let ip = formData.source_ip;
                if (h === 'HALL-401' || h === 'HALL-302') ip = '192.168.10.45';
                if (h === 'LAB-3') ip = '192.168.10.134';
                if (h === 'HALL-204') ip = '192.168.20.12';
                if (h === 'HALL-102') ip = '192.168.30.8';
                if (h === 'ADMIN-01') ip = '192.168.40.15';
                setFormData({ ...formData, hall_id: h, source_ip: ip });
              }}
              className="w-full text-xs font-mono px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-900"
            >
              <option value="HALL-401">HALL-401 (CSE Main Hall &mdash; 192.168.10.0/24)</option>
              <option value="HALL-302">HALL-302 (CSE Upper Hall &mdash; 192.168.10.0/24)</option>
              <option value="LAB-3">LAB-3 (Specialized Lab &mdash; 192.168.10.128/25 Overlap)</option>
              <option value="HALL-204">HALL-204 (ECE Exam Hall &mdash; 192.168.20.0/24)</option>
              <option value="HALL-102">HALL-102 (EEE Ground Hall &mdash; 192.168.30.0/24)</option>
              <option value="ADMIN-01">ADMIN-01 (Administration Control &mdash; 192.168.40.0/24)</option>
            </select>
          </div>

          {/* Source IP */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Simulated Terminal Source IP (CN Verification) <span className="text-orange-600">*</span>
            </label>
            <input
              type="text"
              required
              value={formData.source_ip}
              onChange={(e) => setFormData({ ...formData, source_ip: e.target.value })}
              placeholder="e.g. 192.168.10.45"
              className="w-full text-xs font-mono px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-900"
            />
            <p className="mt-1 text-[11px] text-slate-400">
              Validated against hall subnet using standard Python <span className="font-mono font-semibold text-slate-600">ipaddress</span>
            </p>
          </div>

          {/* Student Roll */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Candidate Roll Number (Optional)
            </label>
            <input
              type="text"
              value={formData.student_roll}
              onChange={(e) => setFormData({ ...formData, student_roll: e.target.value })}
              placeholder="e.g. 21CS042"
              className="w-full text-xs font-mono px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-900"
            />
          </div>

          {/* Severity & Emergency Flag */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Declared Severity Level
            </label>
            <div className="flex items-center gap-3">
              <select
                value={formData.severity}
                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                className="flex-1 text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-900"
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical (Immediate Dispatch)</option>
              </select>

              <label className="flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700 bg-slate-50 px-3 py-2.5 rounded-lg border border-slate-200">
                <input
                  type="checkbox"
                  checked={formData.is_emergency}
                  onChange={(e) => setFormData({ ...formData, is_emergency: e.target.checked })}
                  className="rounded text-orange-600 focus:ring-orange-500 h-4 w-4"
                />
                <span className="flex items-center gap-1 text-rose-700 font-bold">
                  <Zap className="w-3.5 h-3.5 text-rose-600 fill-rose-600" /> Emergency
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Emergency Reason (Conditional) */}
        {formData.is_emergency && (
          <div>
            <label className="block text-xs font-semibold text-rose-700 mb-1.5">
              Emergency Priority Override Justification <span className="text-rose-600">*</span>
            </label>
            <input
              type="text"
              required={formData.is_emergency}
              value={formData.override_reason}
              onChange={(e) => setFormData({ ...formData, override_reason: e.target.value })}
              placeholder="State justification for elevating to top priority queue (e.g. violent disturbance, medical emergency)"
              className="w-full text-xs px-3.5 py-2 bg-rose-50/40 border border-rose-200 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-rose-500/20"
            />
          </div>
        )}

        {/* Incident Description */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1.5">
            Factual Summary & Evidence Log <span className="text-orange-600">*</span>
          </label>
          <textarea
            required
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Record factual observations, seized materials, or hall disruption summary..."
            className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-900 leading-relaxed"
          />
        </div>

        {/* Pre-validation Live Panel */}
        {prevalResult && (
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-2">
            <div className="flex items-center justify-between font-bold">
              <span className="flex items-center gap-1.5 text-slate-800">
                <Cpu className="w-4 h-4 text-orange-600" /> TOC Live Automata Verification
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                prevalResult.is_valid ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
              }`}>
                {prevalResult.is_valid ? 'Formal Agreement: VALID' : 'REJECTED'}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              {/* Invigilator DFA vs Regex */}
              <div className="p-2.5 bg-white rounded border border-slate-200 space-y-1">
                <div className="text-[11px] font-bold text-slate-700">Invigilator ID ({prevalResult.invigilator.input})</div>
                <div className="text-[11px] text-slate-500">
                  DFA: <span className="font-mono font-bold text-slate-800">{prevalResult.invigilator.dfa.final_state}</span> ({prevalResult.invigilator.dfa.execution_time_ns} ns)
                </div>
                <div className="text-[11px] text-slate-500">
                  Regex: <span className="font-mono font-bold text-slate-800">{prevalResult.invigilator.regex.matched ? 'MATCH' : 'MISMATCH'}</span> ({prevalResult.invigilator.regex.execution_time_ns} ns)
                </div>
                <div className="text-[10px] text-emerald-600 font-semibold">
                  Agreement: {prevalResult.invigilator.agreement ? '100% Consistent' : 'Conflict'}
                </div>
              </div>

              {/* Irregularity Code DFA vs Regex */}
              <div className="p-2.5 bg-white rounded border border-slate-200 space-y-1">
                <div className="text-[11px] font-bold text-slate-700">Irregularity Code ({prevalResult.irregularity.input})</div>
                <div className="text-[11px] text-slate-500">
                  DFA: <span className="font-mono font-bold text-slate-800">{prevalResult.irregularity.dfa.final_state}</span> ({prevalResult.irregularity.dfa.execution_time_ns} ns)
                </div>
                <div className="text-[11px] text-slate-500">
                  Regex: <span className="font-mono font-bold text-slate-800">{prevalResult.irregularity.regex.matched ? 'MATCH' : 'MISMATCH'}</span> ({prevalResult.irregularity.regex.execution_time_ns} ns)
                </div>
                <div className="text-[10px] text-emerald-600 font-semibold">
                  Agreement: {prevalResult.irregularity.agreement ? '100% Consistent' : 'Conflict'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Notification */}
        {submissionError && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 space-y-2">
            <div className="flex items-center gap-2 font-bold text-rose-900">
              <AlertCircle className="w-4 h-4 text-rose-600" />
              <span>Submission Rejected at Stage: {submissionError.stage || 'VALIDATION'}</span>
            </div>
            <p className="leading-relaxed">
              {submissionError.error || (submissionError.errors && submissionError.errors.join(' | ')) || 'An unexpected rejection occurred.'}
            </p>
          </div>
        )}

        {/* Success Confirmation Card */}
        {submissionResult && submissionResult.success && (
          <div className="p-5 bg-emerald-50/60 border border-emerald-200 rounded-xl text-xs space-y-4 shadow-xs">
            <div className="flex items-center justify-between pb-3 border-b border-emerald-200/80">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <div>
                  <span className="font-bold text-emerald-950 text-sm">Incident Dispatched & Verified</span>
                  <div className="font-mono text-emerald-800 text-[11px]">Report UID: {submissionResult.report_uid}</div>
                </div>
              </div>
              <StatusBadge status={submissionResult.status} />
            </div>

            {/* Verification Receipts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Authority & Priority */}
              <div className="p-3 bg-white rounded-lg border border-emerald-200 space-y-1">
                <div className="text-[10px] font-bold text-slate-400 uppercase">Assigned Authority</div>
                <div className="font-bold text-slate-800 text-xs">{submissionResult.target_authority}</div>
                <div className="text-[11px] text-slate-600">Category: <span className="font-semibold">{submissionResult.category}</span></div>
                <div className="text-[11px] text-orange-700 font-bold">Priority: {submissionResult.priority.effective_priority}</div>
              </div>

              {/* Handler Allocation */}
              <div className="p-3 bg-white rounded-lg border border-emerald-200 space-y-1">
                <div className="text-[10px] font-bold text-slate-400 uppercase">Handler Dispatch</div>
                {submissionResult.assigned_handler ? (
                  <>
                    <div className="font-bold text-slate-800 text-xs">{submissionResult.assigned_handler.name}</div>
                    <div className="text-[11px] text-slate-600">Dept: {submissionResult.assigned_handler.department}</div>
                    <div className="text-[11px] text-slate-500 font-mono">
                      Load: {submissionResult.assigned_handler.current_load} / {submissionResult.assigned_handler.capacity} max
                    </div>
                  </>
                ) : (
                  <div className="text-amber-700 font-semibold">
                    Enqueued in Priority Queue (Handlers at Capacity)
                  </div>
                )}
              </div>

              {/* Layer-3 LPM Packet Forwarding */}
              <div className="p-3 bg-white rounded-lg border border-emerald-200 space-y-1">
                <div className="text-[10px] font-bold text-slate-400 uppercase">CN Routing Decision</div>
                <div className="font-mono text-slate-800 font-bold text-xs">{submissionResult.network_routing.matched_network}</div>
                <div className="text-[11px] text-slate-600">
                  Next-Hop: <span className="font-mono font-semibold">{submissionResult.network_routing.next_hop}</span>
                </div>
                <div className="text-[11px] text-slate-500">
                  Interface: <span className="font-mono font-semibold">{submissionResult.network_routing.interface}</span> (Metric: {submissionResult.network_routing.metric})
                </div>
              </div>
            </div>

            {/* DFA Transition Trace Toggle */}
            <div className="pt-2">
              <button
                type="button"
                onClick={() => setShowDfaTrace(!showDfaTrace)}
                className="text-[11px] font-bold text-slate-700 hover:text-slate-900 flex items-center gap-1.5"
              >
                <span>{showDfaTrace ? 'Hide' : 'Inspect'} Formal DFA State Transition Trace</span>
                {showDfaTrace ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showDfaTrace && submissionResult.validation_audit && (
                <div className="mt-2 overflow-x-auto bg-slate-900 text-slate-200 p-3 rounded-lg font-mono text-[11px]">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-slate-700 text-slate-400">
                        <th className="py-1 px-2">Step</th>
                        <th className="py-1 px-2">Char</th>
                        <th className="py-1 px-2">Current State</th>
                        <th className="py-1 px-2">&rarr; Next State</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {submissionResult.validation_audit.invigilator.dfa.trace.map((t, i) => (
                        <tr key={i}>
                          <td className="py-1 px-2 text-slate-500">{t.step}</td>
                          <td className="py-1 px-2 font-bold text-orange-400">'{t.char}'</td>
                          <td className="py-1 px-2 text-slate-300">{t.from_state}</td>
                          <td className="py-1 px-2 text-emerald-400 font-bold">{t.to_state}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex items-center gap-2 px-6 py-2.5 bg-orange-600 hover:bg-orange-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{isSubmitting ? 'Validating & Routing...' : 'Submit to Examination Authority'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
