import React, { useState } from 'react';
import { 
  Network, 
  Server, 
  ArrowRight, 
  ShieldCheck, 
  Terminal, 
  Radio, 
  CheckCircle2, 
  AlertTriangle, 
  Cpu, 
  Calculator,
  Compass
} from 'lucide-react';
import { lookupNetworkRoute, calculateSubnet } from '../api/client';
import NetworkTopology from '../components/NetworkTopology';

export default function NetworkDashboard({ networkRoutes }) {
  const routes = networkRoutes && networkRoutes.length > 0 ? networkRoutes : [];
  
  // LPM Simulator State
  const [testIp, setTestIp] = useState('192.168.10.134');
  const [isSearching, setIsSearching] = useState(false);
  const [lpmResult, setLpmResult] = useState(null);
  const [lpmError, setLpmError] = useState(null);

  // Subnet Calculator State
  const [calcCidr, setCalcCidr] = useState('192.168.10.128/25');
  const [calcResult, setCalcResult] = useState(null);
  const [calcError, setCalcError] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const testAddresses = [
    { label: 'Lab-3 (/25 Overlap Test)', ip: '192.168.10.134', desc: 'Selects /25 over /24' },
    { label: 'CSE Hall (/24 Test)', ip: '192.168.10.45', desc: 'Matches CSE 192.168.10.0/24' },
    { label: 'ECE Hall (/24 Test)', ip: '192.168.20.15', desc: 'Matches ECE 192.168.20.0/24' },
    { label: 'Authority Service (Admin)', ip: '192.168.40.10', desc: 'Matches Admin 192.168.40.0/24' },
    { label: 'External (Default Route)', ip: '10.50.2.1', desc: 'Fallbacks to 0.0.0.0/0' },
  ];

  const sampleSubnets = [
    '192.168.10.128/25',
    '192.168.10.0/24',
    '192.168.20.0/24',
    '192.168.40.0/24',
    '10.0.0.0/8',
    '172.16.0.0/16'
  ];

  const handleSimulate = async (ipToTest) => {
    const ip = ipToTest || testIp;
    setIsSearching(true);
    setLpmError(null);
    setLpmResult(null);

    try {
      const res = await lookupNetworkRoute(ip);
      setLpmResult(res);
    } catch (err) {
      console.error(err);
      setLpmError(err.error || 'Failed to perform LPM routing lookup.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleCalculateSubnet = async (cidrToTest) => {
    const cidr = cidrToTest || calcCidr;
    setIsCalculating(true);
    setCalcError(null);
    setCalcResult(null);

    try {
      const res = await calculateSubnet(cidr);
      setCalcResult(res);
    } catch (err) {
      console.error(err);
      setCalcError(err.error || 'Failed to calculate subnet parameters.');
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Simulation Banner - Explicitly Labeled */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-xl p-5 shadow-xs flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-lg bg-orange-500/20 text-orange-400 border border-orange-500/30">
            <Radio className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-tight">Computer Networks (CN) Subnet Routing & LPM Engine</h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-orange-500/30 text-orange-300 border border-orange-400/30 font-semibold">
                Live ipaddress Engine
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Layer-3 software packet forwarding simulation. Demonstrates Longest Prefix Matching (LPM) where overlapping subnets (such as Specialized Lab /25 inside CSE /24) are evaluated with strict longest-prefix precedence and metric tie-breaking.
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Network Topology Diagram */}
      <NetworkTopology currentLookupResult={lpmResult} />

      {/* Subnet Cluster Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { dept: 'Computer Science (CSE)', cidr: '192.168.10.0/24', iface: 'eth0', gw: '192.168.10.1', metric: '10' },
          { dept: 'Specialized Lab (Overlap)', cidr: '192.168.10.128/25', iface: 'eth0.100', gw: '192.168.10.254', metric: '05' },
          { dept: 'Electronics (ECE)', cidr: '192.168.20.0/24', iface: 'eth1', gw: '192.168.20.1', metric: '10' },
          { dept: 'Administration Service', cidr: '192.168.40.0/24', iface: 'vlan40', gw: '192.168.40.1', metric: '05' },
        ].map((sub, idx) => (
          <div key={idx} className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900">{sub.dept}</span>
              <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-orange-50 text-orange-700 border border-orange-200">
                {sub.iface}
              </span>
            </div>
            <div className="text-sm font-mono font-bold text-slate-800">{sub.cidr}</div>
            <div className="text-[11px] text-slate-500 flex items-center justify-between pt-1 border-t border-slate-100">
              <span>Next-Hop: <span className="font-mono font-medium text-slate-700">{sub.gw}</span></span>
              <span>Metric: <span className="font-mono">{sub.metric}</span></span>
            </div>
          </div>
        ))}
      </div>

      {/* Longest Prefix Match Simulator Console */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-orange-600" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">Longest-Prefix Match (LPM) Forwarding Simulator</h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400">RFC 1812 Compliant</span>
        </div>

        {/* Quick IP Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Test IPs:</span>
          {testAddresses.map((t, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setTestIp(t.ip);
                handleSimulate(t.ip);
              }}
              className="text-xs font-mono px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-md hover:bg-slate-100 text-slate-800 shadow-2xs transition-colors"
            >
              {t.ip} ({t.label})
            </button>
          ))}
        </div>

        <form onSubmit={(e) => { e.preventDefault(); handleSimulate(); }} className="flex flex-col sm:flex-row items-center gap-3">
          <div className="flex-1 w-full">
            <input
              type="text"
              value={testIp}
              onChange={(e) => setTestIp(e.target.value)}
              placeholder="e.g. 192.168.10.134, 192.168.40.10, 10.0.0.1"
              className="w-full text-xs font-mono px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-900"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching}
            className="w-full sm:w-auto px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors flex items-center justify-center gap-1.5 disabled:opacity-50"
          >
            <span>{isSearching ? 'Computing LPM...' : 'Execute Routing Lookup'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Error message */}
        {lpmError && (
          <div className="p-3 bg-rose-50 rounded-lg border border-rose-200 text-xs text-rose-800 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{lpmError}</span>
          </div>
        )}

        {/* Live LPM Result */}
        {lpmResult && (
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span className="font-bold text-slate-900 text-xs">
                  Routing Decision for Destination: <span className="font-mono text-orange-600">{lpmResult.destination_ip}</span>
                </span>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                lpmResult.is_default_fallback ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
              }`}>
                {lpmResult.is_default_fallback ? 'Default Route Fallback' : `Matched /${lpmResult.prefix_length}`}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Matched Subnet</div>
                <div className="font-mono font-bold text-slate-900">{lpmResult.matched_route.destination_network}</div>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Next-Hop Gateway</div>
                <div className="font-mono font-bold text-slate-900">{lpmResult.next_hop}</div>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Outgoing Interface</div>
                <div className="font-mono font-bold text-slate-900">{lpmResult.interface}</div>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Route Metric / Cost</div>
                <div className="font-mono font-bold text-slate-900">{lpmResult.metric}</div>
              </div>
            </div>

            {/* Candidate Routes Evaluated */}
            {lpmResult.candidates_evaluated && lpmResult.candidates_evaluated.length > 0 && (
              <div className="space-y-1.5 pt-1">
                <div className="text-[11px] font-bold text-slate-600">Candidate Routes Evaluated by LPM:</div>
                <div className="overflow-x-auto bg-white rounded border border-slate-200 text-[11px] font-mono">
                  <table className="w-full text-left">
                    <thead className="bg-slate-50 text-slate-500 border-b border-slate-200">
                      <tr>
                        <th className="py-1 px-3">Preference</th>
                        <th className="py-1 px-3">Subnet</th>
                        <th className="py-1 px-3">Prefix</th>
                        <th className="py-1 px-3">Metric</th>
                        <th className="py-1 px-3">Next Hop</th>
                        <th className="py-1 px-3">Interface</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {lpmResult.candidates_evaluated.map((c, i) => (
                        <tr key={i} className={c.selected ? 'bg-orange-50/70 font-bold text-orange-900' : 'text-slate-600'}>
                          <td className="py-1.5 px-3">
                            {c.selected ? <span className="text-orange-600">&bull; Selected (LPM)</span> : `#${c.rank}`}
                          </td>
                          <td className="py-1.5 px-3">{c.network}</td>
                          <td className="py-1.5 px-3">/{c.prefix_length}</td>
                          <td className="py-1.5 px-3">{c.metric}</td>
                          <td className="py-1.5 px-3">{c.next_hop}</td>
                          <td className="py-1.5 px-3">{c.interface}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Interactive Subnet Calculator Tool */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calculator className="w-4 h-4 text-orange-600" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Interactive CIDR Subnet Calculator (Python ipaddress)
            </h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400">Classless Inter-Domain Routing</span>
        </div>

        {/* Quick CIDR Chips */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Quick CIDRs:</span>
          {sampleSubnets.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => {
                setCalcCidr(s);
                handleCalculateSubnet(s);
              }}
              className="text-xs font-mono px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-md hover:bg-slate-100 text-slate-800 shadow-2xs transition-colors"
            >
              {s}
            </button>
          ))}
        </div>

        <form onSubmit={(e) => { e.preventDefault(); handleCalculateSubnet(); }} className="flex flex-col sm:flex-row items-center gap-3">
          <div className="flex-1 w-full">
            <input
              type="text"
              value={calcCidr}
              onChange={(e) => setCalcCidr(e.target.value)}
              placeholder="e.g. 192.168.10.128/25"
              className="w-full text-xs font-mono px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-900"
            />
          </div>
          <button
            type="submit"
            disabled={isCalculating}
            className="w-full sm:w-auto px-5 py-2.5 bg-orange-600 hover:bg-orange-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors flex items-center justify-center gap-1.5 disabled:opacity-50"
          >
            <span>{isCalculating ? 'Calculating...' : 'Compute Subnet Parameters'}</span>
            <Calculator className="w-3.5 h-3.5" />
          </button>
        </form>

        {calcError && (
          <div className="p-3 bg-rose-50 rounded-lg border border-rose-200 text-xs text-rose-800 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{calcError}</span>
          </div>
        )}

        {calcResult && (
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <span className="font-bold text-slate-900 text-xs font-mono">
                Subnet Parameters for: <span className="text-orange-600">{calcResult.cidr}</span>
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-100 text-blue-800">
                /{calcResult.prefix_length} Netmask
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Network Address</div>
                <div className="font-mono font-bold text-slate-900">{calcResult.network_address}</div>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Broadcast Address</div>
                <div className="font-mono font-bold text-slate-900">{calcResult.broadcast_address}</div>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Subnet Netmask</div>
                <div className="font-mono font-bold text-slate-900">{calcResult.netmask}</div>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Wildcard Mask</div>
                <div className="font-mono font-bold text-slate-900">{calcResult.wildcard_mask}</div>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Total Addresses</div>
                <div className="font-mono font-bold text-slate-900">{calcResult.total_addresses}</div>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Usable Hosts</div>
                <div className="font-mono font-bold text-emerald-700">{calcResult.usable_hosts}</div>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200 sm:col-span-2">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Usable Host Range</div>
                <div className="font-mono font-bold text-slate-900">
                  {calcResult.first_usable_host} &ndash; {calcResult.last_usable_host}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Actual Routing Table from SQLite */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Simulated Routing Information Base (SQLite network_routes)</h3>
            <p className="text-xs text-slate-400">Ordered by prefix_length DESC, metric ASC</p>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {routes.length} Active Route(s)
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
              <tr>
                <th className="py-2.5 px-4">Network Scope</th>
                <th className="py-2.5 px-4">Destination Network</th>
                <th className="py-2.5 px-4">Subnet Mask</th>
                <th className="py-2.5 px-4">Prefix</th>
                <th className="py-2.5 px-4">Next-Hop Gateway</th>
                <th className="py-2.5 px-4">Outgoing Interface</th>
                <th className="py-2.5 px-4">Metric</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {routes.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3 px-4 font-bold text-slate-800">{r.department}</td>
                  <td className="py-3 px-4 font-mono font-semibold text-orange-700">{r.destination_network}</td>
                  <td className="py-3 px-4 font-mono text-slate-600">{r.subnet_mask}</td>
                  <td className="py-3 px-4 font-mono font-bold text-slate-900">/{r.prefix_length}</td>
                  <td className="py-3 px-4 font-mono text-slate-700">{r.next_hop}</td>
                  <td className="py-3 px-4 font-mono">
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 font-semibold">
                      {r.interface}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-500">{r.metric}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
