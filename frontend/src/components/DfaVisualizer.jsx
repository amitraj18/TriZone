import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  Play, 
  RotateCcw, 
  ChevronRight, 
  ChevronLeft, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Code2,
  Sparkles
} from 'lucide-react';
import { validateIdentifiers } from '../api/client';

export default function DfaVisualizer({ initialInvigilatorId = 'INVCSE0001', initialIrregularityCode = 'IR01' }) {
  const [testId, setTestId] = useState(initialInvigilatorId);
  const [testCode, setTestCode] = useState(initialIrregularityCode);
  const [validationData, setValidationData] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeMode, setActiveMode] = useState('invigilator'); // 'invigilator' | 'irregularity'

  const runValidation = async () => {
    try {
      const res = await validateIdentifiers(testId, testCode);
      setValidationData(res.data);
      setActiveStep(0);
      setIsPlaying(false);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    runValidation();
  }, [testId, testCode]);

  const activeEntityData = validationData ? validationData[activeMode] : null;
  const trace = activeEntityData?.dfa?.trace || [];

  // Auto-step player
  useEffect(() => {
    let interval = null;
    if (isPlaying && trace.length > 0) {
      interval = setInterval(() => {
        setActiveStep((prev) => {
          if (prev >= trace.length) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 700);
    }
    return () => clearInterval(interval);
  }, [isPlaying, trace]);

  const currentStepData = activeStep > 0 && activeStep <= trace.length ? trace[activeStep - 1] : null;
  const isComplete = activeStep === trace.length && trace.length > 0;

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-orange-100 text-orange-700">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Interactive Automata (TOC) State-Machine Visualizer
            </h3>
            <p className="text-[11px] text-slate-500">
              Real-time character-by-character DFA transition simulator & Regex timing benchmark
            </p>
          </div>
        </div>

        {/* Mode Selector */}
        <div className="flex items-center bg-slate-100 p-0.5 rounded-lg text-xs font-semibold">
          <button
            type="button"
            onClick={() => { setActiveMode('invigilator'); setActiveStep(0); setIsPlaying(false); }}
            className={`px-3 py-1 rounded-md transition-colors ${
              activeMode === 'invigilator' ? 'bg-white text-orange-700 shadow-2xs font-bold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Invigilator DFA
          </button>
          <button
            type="button"
            onClick={() => { setActiveMode('irregularity'); setActiveStep(0); setIsPlaying(false); }}
            className={`px-3 py-1 rounded-md transition-colors ${
              activeMode === 'irregularity' ? 'bg-white text-orange-700 shadow-2xs font-bold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Irregularity DFA
          </button>
        </div>
      </div>

      {/* Input & Quick Presets */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-[11px] font-bold text-slate-600 mb-1">
            {activeMode === 'invigilator' ? 'Input String (INV[DEPT][4-digit])' : 'Input Code (IR[2-digit])'}:
          </label>
          <input
            type="text"
            value={activeMode === 'invigilator' ? testId : testCode}
            onChange={(e) => {
              const val = e.target.value.toUpperCase();
              if (activeMode === 'invigilator') setTestId(val);
              else setTestCode(val);
            }}
            placeholder={activeMode === 'invigilator' ? 'e.g. INVCSE0001, INVECE0001' : 'e.g. IR01, IR03'}
            className="w-full text-xs font-mono font-bold px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 text-slate-900"
          />
        </div>

        {/* Quick Sample Chips */}
        <div className="space-y-1">
          <span className="text-[10px] text-slate-400 block font-semibold">Test Inputs:</span>
          <div className="flex items-center gap-1.5 flex-wrap">
            {activeMode === 'invigilator' ? (
              ['INVCSE0001', 'INVECE0001', 'INVCIV0001', 'INVME0001', 'INVBAD9999'].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setTestId(s)}
                  className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700"
                >
                  {s}
                </button>
              ))
            ) : (
              ['IR01', 'IR02', 'IR03', 'IR04', 'IR05', 'IR06', 'IR99'].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setTestCode(s)}
                  className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700"
                >
                  {s}
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Stepper & Controls */}
      <div className="p-4 bg-slate-900 text-white rounded-xl space-y-4 shadow-inner">
        <div className="flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Step:</span>
            <span className="font-bold text-orange-400">{activeStep} / {trace.length}</span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-400">Current State:</span>
            <span className={`px-2 py-0.5 rounded font-bold text-xs ${
              isComplete && activeEntityData?.dfa?.accepted 
                ? 'bg-emerald-500 text-white' 
                : currentStepData?.is_trap 
                ? 'bg-rose-500 text-white' 
                : 'bg-orange-500 text-white'
            }`}>
              {activeStep === 0 ? (activeMode === 'invigilator' ? 'q0' : 's0') : currentStepData ? currentStepData.to_state : 'DONE'}
            </span>
          </div>

          {/* Stepper Buttons */}
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => setActiveStep(0)}
              disabled={activeStep === 0}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30"
              title="Reset"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setActiveStep((prev) => Math.max(0, prev - 1))}
              disabled={activeStep === 0}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30"
              title="Step Back"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setIsPlaying(!isPlaying)}
              disabled={isComplete}
              className="px-2.5 py-1 rounded bg-orange-600 hover:bg-orange-500 text-white font-sans text-xs font-bold flex items-center gap-1 disabled:opacity-40"
            >
              <Play className="w-3 h-3 fill-current" />
              <span>{isPlaying ? 'Pause' : 'Play'}</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveStep((prev) => Math.min(trace.length, prev + 1))}
              disabled={activeStep >= trace.length}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30"
              title="Step Forward"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Character Tape */}
        <div className="space-y-1">
          <div className="text-[10px] text-slate-400 font-mono">INPUT TAPE HEAD:</div>
          <div className="flex items-center gap-1 overflow-x-auto pb-1 font-mono">
            {activeEntityData?.input.split('').map((ch, idx) => {
              const isCurrent = activeStep === idx + 1;
              const isPassed = activeStep > idx + 1;
              return (
                <div
                  key={idx}
                  className={`w-9 h-9 rounded flex flex-col items-center justify-center text-xs font-bold border transition-all ${
                    isCurrent
                      ? 'bg-orange-500 text-white border-orange-400 ring-2 ring-orange-300 scale-105'
                      : isPassed
                      ? 'bg-slate-800 text-slate-300 border-slate-700'
                      : 'bg-slate-900 text-slate-500 border-slate-800'
                  }`}
                >
                  <span>{ch}</span>
                  <span className="text-[8px] opacity-60">#{idx + 1}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Live Step Explanation */}
        <div className="p-3 bg-slate-800/90 rounded-lg text-xs font-mono border border-slate-700/80">
          {activeStep === 0 ? (
            <span className="text-slate-400">Press &quot;Step Forward&quot; or &quot;Play&quot; to begin character-by-character state traversal from initial state.</span>
          ) : currentStepData ? (
            <div className="space-y-1">
              <div className="text-orange-300">
                &delta;({currentStepData.from_state}, &apos;{currentStepData.char}&apos;) &rarr; <span className="text-emerald-400 font-bold">{currentStepData.to_state}</span>
              </div>
              <div className="text-slate-400 text-[11px]">
                {currentStepData.is_trap 
                  ? 'Illegal transition! Symbol rejected by DFA grammar &rarr; entering trap state.'
                  : `Consumed character '${currentStepData.char}', advancing state to ${currentStepData.to_state}.`}
              </div>
            </div>
          ) : (
            <span className="text-emerald-400 font-bold">Traversal complete.</span>
          )}
        </div>
      </div>

      {/* Comparison Grid: DFA vs Regex Verification */}
      {activeEntityData && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          {/* DFA Evaluation Box */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-800 flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-orange-600" /> DFA State-Machine Result
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                activeEntityData.dfa.accepted ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
              }`}>
                {activeEntityData.dfa.accepted ? 'ACCEPTED' : 'REJECTED'}
              </span>
            </div>
            <div className="font-mono text-slate-600 text-[11px]">
              Final State: <strong className="text-slate-900">{activeEntityData.dfa.final_state}</strong>
            </div>
            <div className="font-mono text-slate-500 text-[11px] flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>DFA Duration: <strong className="text-slate-800">{activeEntityData.dfa.execution_time_ns} ns</strong></span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed pt-1">
              {activeEntityData.dfa.reason}
            </p>
          </div>

          {/* Regex Evaluation Box */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-800 flex items-center gap-1.5">
                <Code2 className="w-4 h-4 text-blue-600" /> Regex Matcher Result
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                activeEntityData.regex.matched ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
              }`}>
                {activeEntityData.regex.matched ? 'MATCHED' : 'FAILED'}
              </span>
            </div>
            <div className="font-mono text-slate-600 text-[11px] truncate">
              Pattern: <strong className="text-slate-800 font-mono text-[10px]">{activeEntityData.regex.pattern}</strong>
            </div>
            <div className="font-mono text-slate-500 text-[11px] flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>Regex Duration: <strong className="text-slate-800">{activeEntityData.regex.execution_time_ns} ns</strong></span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed pt-1">
              {activeEntityData.regex.reason}
            </p>
          </div>
        </div>
      )}

      {/* Formal Agreement Banner */}
      {activeEntityData && (
        <div className={`p-3 rounded-lg border flex items-center justify-between text-xs font-semibold ${
          activeEntityData.agreement 
            ? 'bg-emerald-50 text-emerald-800 border-emerald-200' 
            : 'bg-rose-50 text-rose-800 border-rose-200'
        }`}>
          <div className="flex items-center gap-2">
            {activeEntityData.agreement ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <XCircle className="w-4 h-4 text-rose-600" />}
            <span>Formal Language Equivalence Assertion: {activeEntityData.agreement ? 'L(DFA) = L(Regex) — 100% Agreement' : 'CRITICAL Conflict: DFA and Regex Disagree!'}</span>
          </div>
          <span className="font-mono text-[11px] font-bold">
            Audit ID: {activeEntityData.is_valid ? 'STATUS_VALID' : 'STATUS_REJECT'}
          </span>
        </div>
      )}
    </div>
  );
}

