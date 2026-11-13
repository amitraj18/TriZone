import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  Bell, 
  Search, 
  ShieldCheck, 
  Download, 
  CheckCheck, 
  X, 
  User, 
  LogOut, 
  Sparkles,
  RotateCcw
} from 'lucide-react';
import { 
  fetchNotifications, 
  markNotificationRead, 
  markAllNotificationsRead, 
  getExportCsvUrl, 
  login, 
  logout,
  resetDemoDatabase 
} from '../api/client';

export default function Topbar({ 
  title, 
  subtitle, 
  onRefresh, 
  isRefreshing, 
  backendHealth,
  currentUser,
  onUserChanged 
}) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [demoResetting, setDemoResetting] = useState(false);
  const [loginForm, setLoginForm] = useState({ username: 'admin', password: 'admin123' });
  const [loginError, setLoginError] = useState(null);

  const loadNotifs = async () => {
    try {
      const res = await fetchNotifications(currentUser?.role || 'ALL');
      setNotifications(res.data || []);
      setUnreadCount(res.unread_count || 0);
    } catch (e) {}
  };

  useEffect(() => {
    loadNotifs();
    const interval = setInterval(loadNotifs, 10000);
    return () => clearInterval(interval);
  }, [currentUser]);

  const handleMarkRead = async (id) => {
    await markNotificationRead(id);
    loadNotifs();
  };

  const handleMarkAllRead = async () => {
    await markAllNotificationsRead(currentUser?.role || 'ALL');
    loadNotifs();
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoginError(null);
    try {
      const u = await login(loginForm.username, loginForm.password);
      setShowLoginModal(false);
      if (onUserChanged) onUserChanged(u);
      if (onRefresh) onRefresh();
    } catch (err) {
      setLoginError(err.error || 'Authentication failed.');
    }
  };

  const handleQuickSwitchUser = async (u, p) => {
    try {
      const user = await login(u, p);
      if (onUserChanged) onUserChanged(user);
      if (onRefresh) onRefresh();
      setShowLoginModal(false);
    } catch (e) {}
  };

  const handleResetDemo = async () => {
    if (!window.confirm("Reset database to clean hackathon demo state? This will repopulate standard demonstration records.")) return;
    setDemoResetting(true);
    try {
      await resetDemoDatabase();
      alert("Demonstration database reset successfully!");
      if (onRefresh) onRefresh();
      loadNotifs();
    } catch (e) {
      alert("Failed to reset demo database: " + e.message);
    } finally {
      setDemoResetting(false);
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-base font-bold text-slate-900 tracking-tight">{title}</h1>
        <p className="text-xs text-slate-500">{subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Demo Reset Shortcut */}
        <button
          onClick={handleResetDemo}
          disabled={demoResetting}
          className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-semibold text-orange-700 bg-orange-50 border border-orange-200 hover:bg-orange-100 rounded-lg transition-colors"
          title="Reset database to clean Hackathon Demo state"
        >
          <RotateCcw className={`w-3.5 h-3.5 ${demoResetting ? 'animate-spin' : ''}`} />
          <span>Demo Reset</span>
        </button>

        {/* CSV Export Button */}
        <a
          href={getExportCsvUrl()}
          download="iris_exam_reports_export.csv"
          className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg shadow-2xs transition-colors"
          title="Export Reports to CSV"
        >
          <Download className="w-3.5 h-3.5 text-slate-500" />
          <span className="hidden sm:inline">Export CSV</span>
        </a>

        {/* Sync API Button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg shadow-2xs transition-colors disabled:opacity-50"
          title="Refresh Data from Backend"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-orange-600' : 'text-slate-500'}`} />
          <span className="hidden sm:inline">Sync API</span>
        </button>

        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 relative transition-colors"
            title="In-App Notifications"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-white text-[9px] font-bold flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 p-3 space-y-2 z-50 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <span className="font-bold text-slate-900">Notifications ({unreadCount} unread)</span>
                {unreadCount > 0 && (
                  <button
                    onClick={handleMarkAllRead}
                    className="text-[10px] text-orange-600 hover:text-orange-700 font-semibold"
                  >
                    Mark all read
                  </button>
                )}
              </div>

              <div className="max-h-64 overflow-y-auto space-y-1.5">
                {notifications.length === 0 ? (
                  <div className="py-4 text-center text-slate-400 text-xs">No notifications yet.</div>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      onClick={() => handleMarkRead(n.id)}
                      className={`p-2 rounded-lg border transition-colors cursor-pointer ${
                        n.is_read ? 'bg-white border-slate-100 text-slate-600' : 'bg-orange-50/60 border-orange-200 text-slate-900 font-medium'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[11px]">{n.title}</span>
                        <span className="text-[9px] text-slate-400 font-mono">{n.created_at?.slice(11, 16)}</span>
                      </div>
                      <p className="text-[11px] text-slate-600 mt-0.5 leading-snug">{n.message}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Account / Role Switcher */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <button
            onClick={() => setShowLoginModal(true)}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            title="Switch User / Account"
          >
            <div className="w-8 h-8 rounded-full bg-orange-100 border border-orange-200 flex items-center justify-center text-xs font-bold text-orange-800">
              {currentUser?.role ? currentUser.role[0] : 'A'}
            </div>
            <div className="hidden lg:block text-left">
              <div className="text-xs font-semibold text-slate-800 leading-tight">
                {currentUser?.name || 'Administrator'}
              </div>
              <div className="text-[10px] text-orange-700 font-bold font-mono">
                {currentUser?.role || 'ADMIN'}
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Login / Role Switcher Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl shadow-xl border border-slate-200 max-w-sm w-full p-6 space-y-4 text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Switch Demo Account</h3>
                <p className="text-slate-500 text-[11px]">Role-Based Access Control (RBAC)</p>
              </div>
              <button onClick={() => setShowLoginModal(false)} className="p-1 text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Quick Demo Switcher Buttons */}
            <div className="space-y-1.5">
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Quick Switch Roles:</span>
              <div className="grid grid-cols-1 gap-1.5">
                <button
                  type="button"
                  onClick={() => handleQuickSwitchUser('admin', 'admin123')}
                  className="p-2 text-left rounded-lg border border-slate-200 hover:bg-orange-50 hover:border-orange-200 flex items-center justify-between"
                >
                  <div>
                    <div className="font-bold text-slate-800">Dr. Barbara Liskov</div>
                    <div className="text-[10px] text-slate-500">Administrator (All Access)</div>
                  </div>
                  <span className="px-1.5 py-0.5 rounded bg-orange-100 text-orange-800 font-mono text-[9px] font-bold">ADMIN</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleQuickSwitchUser('inv_cse', 'exam123')}
                  className="p-2 text-left rounded-lg border border-slate-200 hover:bg-orange-50 hover:border-orange-200 flex items-center justify-between"
                >
                  <div>
                    <div className="font-bold text-slate-800">Dr. Alan Turing</div>
                    <div className="text-[10px] text-slate-500">Invigilator (CSE Dept &bull; INVCSE0001)</div>
                  </div>
                  <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 font-mono text-[9px] font-bold">INVIGILATOR</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleQuickSwitchUser('handler_cs', 'exam123')}
                  className="p-2 text-left rounded-lg border border-slate-200 hover:bg-orange-50 hover:border-orange-200 flex items-center justify-between"
                >
                  <div>
                    <div className="font-bold text-slate-800">Dr. Robert Davis</div>
                    <div className="text-[10px] text-slate-500">Chief Superintendent Handler</div>
                  </div>
                  <span className="px-1.5 py-0.5 rounded bg-purple-100 text-purple-800 font-mono text-[9px] font-bold">HANDLER</span>
                </button>
              </div>
            </div>

            {/* Custom Login Form */}
            <form onSubmit={handleLoginSubmit} className="pt-2 border-t border-slate-100 space-y-3">
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Manual Credentials:</span>
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">Username:</label>
                <input
                  type="text"
                  required
                  value={loginForm.username}
                  onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">Password:</label>
                <input
                  type="password"
                  required
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-900"
                />
              </div>

              {loginError && (
                <div className="p-2 bg-rose-50 text-rose-800 border border-rose-200 rounded text-[11px]">
                  {loginError}
                </div>
              )}

              <button
                type="submit"
                className="w-full py-2 bg-orange-600 hover:bg-orange-700 text-white font-bold rounded-lg shadow-sm"
              >
                Sign In
              </button>
            </form>
          </div>
        </div>
      )}
    </header>
  );
}
