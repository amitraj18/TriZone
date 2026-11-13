const API_BASE = '/api';

export function getAuthToken() {
  return localStorage.getItem('iris_auth_token');
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('iris_auth_token', token);
  } else {
    localStorage.removeItem('iris_auth_token');
  }
}

function getHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await res.json();
  if (!res.ok) throw data;
  if (data.data && data.data.token) {
    setAuthToken(data.data.token);
  }
  return data.data;
}

export async function fetchCurrentUser() {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, { headers: getHeaders() });
    if (!res.ok) return null;
    const body = await res.json();
    return body.data;
  } catch (err) {
    return null;
  }
}

export async function logout() {
  setAuthToken(null);
  try {
    await fetch(`${API_BASE}/auth/logout`, { method: 'POST', headers: getHeaders() });
  } catch (e) {}
}

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      status: 'offline',
      service: 'Exam Hall Irregularity Reporter API',
      database: 'disconnected',
      error: err.message
    };
  }
}

export async function fetchStats() {
  try {
    const res = await fetch(`${API_BASE}/stats`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    console.warn('Failed to fetch backend stats', err);
    return null;
  }
}

export async function fetchReports(params = {}) {
  try {
    const query = new URLSearchParams(params).toString();
    const url = query ? `${API_BASE}/reports?${query}` : `${API_BASE}/reports`;
    const res = await fetch(url, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    console.warn('Failed to fetch backend reports', err);
    return [];
  }
}

export async function fetchReportDetails(reportId) {
  try {
    const res = await fetch(`${API_BASE}/reports/${reportId}`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    console.error('Failed to fetch report details', err);
    throw err;
  }
}

export async function submitReport(payload) {
  const res = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    throw data;
  }
  return data;
}

export async function validateIdentifiers(invigilatorId, irregularityCode) {
  const res = await fetch(`${API_BASE}/reports/validate`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      invigilator_id: invigilatorId,
      irregularity_code: irregularityCode
    })
  });
  return await res.json();
}

export async function fetchCategories() {
  try {
    const res = await fetch(`${API_BASE}/categories`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    console.warn('Failed to fetch categories', err);
    return [];
  }
}

export async function fetchRoutingRules() {
  try {
    const res = await fetch(`${API_BASE}/routing-rules`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    console.warn('Failed to fetch routing rules', err);
    return [];
  }
}

export async function updateRoutingRule(ruleId, updates) {
  const res = await fetch(`${API_BASE}/routing-rules/${ruleId}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(updates)
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export async function fetchRoutingRuleHistory() {
  try {
    const res = await fetch(`${API_BASE}/routing-rules/history`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    return [];
  }
}

export async function fetchHandlers() {
  try {
    const res = await fetch(`${API_BASE}/handlers`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    console.warn('Failed to fetch handlers', err);
    return [];
  }
}

export async function updateHandlerAvailability(handlerId, isAvailable) {
  const res = await fetch(`${API_BASE}/handlers/${handlerId}/availability`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({ is_available: isAvailable })
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export async function updateHandlerCapacity(handlerId, capacity) {
  const res = await fetch(`${API_BASE}/handlers/${handlerId}/capacity`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({ capacity: parseInt(capacity, 10) })
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export async function updateReportStatus(reportId, status, comment = '') {
  const res = await fetch(`${API_BASE}/reports/${reportId}/status`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({ status, comment })
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export async function fetchNetworkRoutes() {
  try {
    const res = await fetch(`${API_BASE}/network-routes`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    console.warn('Failed to fetch network routes', err);
    return [];
  }
}

export async function lookupNetworkRoute(destinationIp) {
  const res = await fetch(`${API_BASE}/network-routes/lookup`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ destination_ip: destinationIp })
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export async function calculateSubnet(cidr) {
  const res = await fetch(`${API_BASE}/network-routes/calculate-subnet`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ cidr })
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export async function fetchDispatchQueue() {
  try {
    const res = await fetch(`${API_BASE}/dispatch/queue`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    console.warn('Failed to fetch dispatch queue', err);
    return [];
  }
}

export async function fetchDispatchLogs() {
  try {
    const res = await fetch(`${API_BASE}/dispatch/logs`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body.data;
  } catch (err) {
    console.warn('Failed to fetch dispatch logs', err);
    return [];
  }
}

export async function fetchNotifications(role = 'ALL') {
  try {
    const res = await fetch(`${API_BASE}/notifications?role=${encodeURIComponent(role)}`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    return body;
  } catch (err) {
    return { count: 0, unread_count: 0, data: [] };
  }
}

export async function markNotificationRead(id) {
  try {
    await fetch(`${API_BASE}/notifications/${id}/read`, { method: 'PUT', headers: getHeaders() });
  } catch (e) {}
}

export async function markAllNotificationsRead(role = 'ALL') {
  try {
    await fetch(`${API_BASE}/notifications/read-all`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ role })
    });
  } catch (e) {}
}

export async function resetDemoDatabase() {
  const res = await fetch(`${API_BASE}/demo/reset`, {
    method: 'POST',
    headers: getHeaders()
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export function getExportCsvUrl() {
  return `${API_BASE}/reports/export/csv`;
}
