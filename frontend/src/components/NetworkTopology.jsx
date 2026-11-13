import React, { useState } from 'react';
import { Network, Server, ArrowRight, ShieldCheck, Terminal, Radio, CheckCircle2, Cpu, Globe, Laptop, HardDrive } from 'lucide-react';

export default function NetworkTopology({ currentLookupResult }) {
  const [selectedNode, setSelectedNode] = useState(null);

  const zones = [
    { id: 'cse', name: 'CSE Department Hall', subnet: '192.168.10.0/24', iface: 'eth0', gw: '192.168.10.1', color: 'border-orange-200 bg-orange-50/50' },
    { id: 'lab', name: 'Specialized Lab (/25 Overlap)', subnet: '192.168.10.128/25', iface: 'eth0.100', gw: '192.168.10.254', color: 'border-amber-200 bg-amber-50/50' },
    { id: 'ece', name: 'ECE Department Hall', subnet: '192.168.20.0/24', iface: 'eth1', gw: '192.168.20.1', color: 'border-blue-200 bg-blue-50/50' },
    { id: 'eee', name: 'EEE Department Hall', subnet: '192.168.30.0/24', iface: 'eth2', gw: '192.168.30.1', color: 'border-purple-200 bg-purple-50/50' },
  ];

  const authorities = [
    { id: 'cs', role: 'Chief Superintendent', ip: '192.168.40.10', iface: 'vlan40', color: 'bg-orange-50 text-orange-800' },
    { id: 'centre', role: 'Centre Superintendent', ip: '192.168.40.20', iface: 'vlan40', color: 'bg-blue-50 text-blue-800' },
    { id: 'coe', role: 'Controller of Examinations', ip: '192.168.40.30', iface: 'vlan40', color: 'bg-purple-50 text-purple-800' },
  ];

  const matchedIface = currentLookupResult?.interface;
  const matchedNextHop = currentLookupResult?.next_hop;

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-orange-100 text-orange-700">
            <Network className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Interactive Layer-3 Academic Network Topology (CN Simulation)
            </h3>
            <p className="text-[11px] text-slate-500">
              Visualizes ingress examination zone subnets, simulated core distribution router, and authority endpoints
            </p>
          </div>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold">
          Layer-3 Forwarding
        </span>
      </div>

      {/* Topology Diagram Container */}
      <div className="bg-slate-900 rounded-xl p-6 text-white overflow-x-auto relative">
        <div className="min-w-[700px] flex items-center justify-between gap-6">
          
          {/* Left Column: Examination Zones */}
          <div className="space-y-3 flex-1">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <Laptop className="w-3.5 h-3.5 text-orange-400" />
              <span>Examination Zones (Source Ingress)</span>
            </div>

            {zones.map((z) => {
              const isMatched = matchedIface === z.iface;
              return (
                <div
                  key={z.id}
                  onClick={() => setSelectedNode(z)}
                  className={`p-3 rounded-lg border transition-all cursor-pointer ${
                    isMatched
                      ? 'bg-orange-500/20 border-orange-400 ring-2 ring-orange-400/40 text-orange-200 scale-102'
                      : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span>{z.name}</span>
                    <span className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-slate-900/60 text-slate-300">
                      {z.iface}
                    </span>
                  </div>
                  <div className="text-[11px] font-mono text-slate-400 mt-1 flex items-center justify-between">
                    <span>Subnet: {z.subnet}</span>
                    <span className="text-[10px]">GW: {z.gw}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Middle: Core Simulated Distribution Router */}
          <div className="flex flex-col items-center justify-center px-4">
            <div className="w-28 h-28 rounded-2xl bg-gradient-to-tr from-slate-800 to-slate-700 border-2 border-orange-500/60 shadow-lg shadow-orange-500/10 flex flex-col items-center justify-center p-2 text-center space-y-1">
              <Radio className="w-6 h-6 text-orange-400 animate-pulse" />
              <div className="text-[11px] font-bold font-mono text-white tracking-tight">IRIS-CORE-R1</div>
              <div className="text-[9px] text-slate-400 font-mono">LPM Router</div>
              <div className="text-[9px] px-1.5 py-0.2 rounded bg-orange-500/30 text-orange-300 font-mono font-bold">
                RIB: 6 Routes
              </div>
            </div>

            {/* Ingress / Egress indicator */}
            {matchedIface && (
              <div className="mt-2 text-[10px] font-mono font-semibold text-emerald-400 text-center animate-bounce">
                &larr; {matchedIface} | Forwarding &rarr;
              </div>
            )}
          </div>

          {/* Right Column: Administration Network & Authority Endpoints */}
          <div className="space-y-3 flex-1">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <HardDrive className="w-3.5 h-3.5 text-blue-400" />
              <span>Admin Subnet: 192.168.40.0/24 (Egress)</span>
            </div>

            {authorities.map((a) => {
              const isDest = currentLookupResult?.destination_ip === a.ip;
              return (
                <div
                  key={a.id}
                  onClick={() => setSelectedNode(a)}
                  className={`p-3 rounded-lg border transition-all cursor-pointer ${
                    isDest
                      ? 'bg-emerald-500/20 border-emerald-400 ring-2 ring-emerald-400/40 text-emerald-200 scale-102'
                      : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span>{a.role}</span>
                    <span className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-slate-900/60 text-slate-300">
                      {a.iface}
                    </span>
                  </div>
                  <div className="text-[11px] font-mono text-slate-400 mt-1 flex items-center justify-between">
                    <span>IP: {a.ip}</span>
                    {isDest && (
                      <span className="text-[10px] font-bold text-emerald-400 flex items-center gap-0.5">
                        &bull; Target Host
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Selected Node Details or Dynamic Lookup Banner */}
      {currentLookupResult && currentLookupResult.reachable && (
        <div className="p-3 rounded-lg bg-orange-50 border border-orange-200 text-xs text-orange-950 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-orange-600 shrink-0" />
            <span>
              Active Forwarding Path to <strong className="font-mono">{currentLookupResult.destination_ip}</strong>: 
              Outgoing Interface <strong className="font-mono">{currentLookupResult.interface}</strong> via Gateway <strong className="font-mono">{currentLookupResult.next_hop}</strong>
            </span>
          </div>
          <span className="font-mono font-bold text-[11px] bg-orange-200/70 px-2 py-0.5 rounded text-orange-900">
            Metric: {currentLookupResult.metric}
          </span>
        </div>
      )}
    </div>
  );
}

