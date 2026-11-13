import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import UserDashboard from './pages/UserDashboard';
import ReportSubmission from './pages/ReportSubmission';
import HandlerDashboard from './pages/HandlerDashboard';
import RoutingDashboard from './pages/RoutingDashboard';
import NetworkDashboard from './pages/NetworkDashboard';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import { 
  fetchHealth, 
  fetchStats, 
  fetchReports, 
  fetchCategories, 
  fetchRoutingRules, 
  fetchHandlers, 
  fetchNetworkRoutes,
  fetchCurrentUser 
} from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('user_dashboard');
  const [backendHealth, setBackendHealth] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [reports, setReports] = useState([]);
  const [categories, setCategories] = useState([]);
  const [routingRules, setRoutingRules] = useState([]);
  const [handlers, setHandlers] = useState([]);
  const [networkRoutes, setNetworkRoutes] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [health, user] = await Promise.all([
        fetchHealth(),
        fetchCurrentUser()
      ]);
      setBackendHealth(health);
      if (user) setCurrentUser(user);

      const [s, r, c, rr, h, nr] = await Promise.all([
        fetchStats(),
        fetchReports(),
        fetchCategories(),
        fetchRoutingRules(),
        fetchHandlers(),
        fetchNetworkRoutes()
      ]);

      if (s) setStats(s);
      if (r) setReports(r);
      if (c) setCategories(c);
      if (rr) setRoutingRules(rr);
      if (h) setHandlers(h);
      if (nr) setNetworkRoutes(nr);
    } catch (err) {
      console.error('Error synchronizing dashboard data:', err);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const getPageHeader = () => {
    switch (activeTab) {
      case 'user_dashboard':
        return {
          title: 'Institutional Overview & Incident Operations',
          subtitle: 'Live monitor for hall invigilation, integrity violations, and authority routing status'
        };
      case 'report_submission':
        return {
          title: 'Exam Hall Irregularity Intake Terminal',
          subtitle: 'TOC Automata Verification, CN Longest Prefix Match Routing & Dispatch Pipeline'
        };
      case 'handler_dashboard':
        return {
          title: 'Handler Availability & Capacity Management',
          subtitle: 'Authority workload balancing, concurrent incident limits, and priority queue processor'
        };
      case 'routing_management':
        return {
          title: 'Examination Authority Routing Table',
          subtitle: 'Explicit lookup rules mapping irregularity categories to statutory officers'
        };
      case 'network_management':
        return {
          title: 'Computer Networks (CN) Subnet Routing & LPM Engine',
          subtitle: 'Live Layer-3 packet forwarding simulator with longest-prefix matching'
        };
      case 'analytics_dashboard':
        return {
          title: 'Examination Integrity Telemetry & Distribution Analytics',
          subtitle: 'Computed directly from live SQLite database records'
        };
      default:
        return {
          title: 'Examination Administration',
          subtitle: 'System Control Center'
        };
    }
  };

  const header = getPageHeader();

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Fixed Left Navigation Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        backendHealth={backendHealth} 
      />

      {/* Main Content Area (Offset by Sidebar Width 64 = 16rem) */}
      <div className="flex-1 ml-64 flex flex-col min-w-0">
        <Topbar 
          title={header.title} 
          subtitle={header.subtitle} 
          onRefresh={loadData} 
          isRefreshing={isRefreshing}
          backendHealth={backendHealth}
          currentUser={currentUser}
          onUserChanged={(user) => {
            setCurrentUser(user);
            loadData();
          }}
        />

        <main className="p-6 md:p-8 flex-1 overflow-x-hidden">
          {activeTab === 'user_dashboard' && (
            <UserDashboard 
              reports={reports} 
              stats={stats} 
              backendHealth={backendHealth} 
              setActiveTab={setActiveTab}
              onDataChanged={loadData}
            />
          )}

          {activeTab === 'report_submission' && (
            <ReportSubmission 
              categories={categories} 
              onReportSubmitted={loadData}
            />
          )}

          {activeTab === 'handler_dashboard' && (
            <HandlerDashboard 
              handlers={handlers} 
              onDataChanged={loadData}
            />
          )}

          {activeTab === 'routing_management' && (
            <RoutingDashboard 
              routingRules={routingRules} 
              categories={categories}
            />
          )}

          {activeTab === 'network_management' && (
            <NetworkDashboard 
              networkRoutes={networkRoutes} 
            />
          )}

          {activeTab === 'analytics_dashboard' && (
            <AnalyticsDashboard 
              stats={stats} 
              reports={reports} 
            />
          )}
        </main>
      </div>
    </div>
  );
}
