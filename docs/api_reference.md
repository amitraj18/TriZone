# REST API Reference — IRIS

All endpoints communicate via JSON over HTTP. The backend server listens on port `5000`.

---

## 1. System & Authentication

### `GET /api/health`
Returns health status, active SQLite connectivity, and service version.
```json
{
  "status": "healthy",
  "service": "Exam Hall Irregularity Reporter API",
  "version": "2.5.0",
  "phase": "Master Complete",
  "database": "connected"
}
```

### `POST /api/auth/login`
Authenticates a user via PBKDF2/scrypt hashed password verification. Returns signed HMAC-SHA256 bearer token.
- **Request Body**: `{"username": "admin", "password": "admin123"}`
- **Response**: User profile object and bearer token.

### `GET /api/auth/me`
Inspects current authenticated bearer session.
- **Header**: `Authorization: Bearer <token>`

---

## 2. Theory of Computation (TOC) Validation

### `POST /api/validation/invigilator`
Validates an Invigilator ID through both DFA and Regex with nanosecond timing.
- **Request Body**: `{"invigilator_id": "INVCSE0001"}`
- **Response**: `{"is_valid": true, "dfa": {...}, "regex": {...}, "agreement": true}`

### `POST /api/validation/irregularity`
Validates an Irregularity Code through both DFA and Regex with nanosecond timing.
- **Request Body**: `{"irregularity_code": "IR01"}`
- **Response**: `{"is_valid": true, "dfa": {...}, "regex": {...}, "agreement": true}`

---

## 3. Incident Reports & Submission Pipeline

### `POST /api/reports`
Submits an irregularity report and triggers the full 19-step validation, routing, and dispatch pipeline.
- **Request Body**:
```json
{
  "invigilator_id": "INVCSE0001",
  "irregularity_code": "IR01",
  "hall_id": "HALL-401",
  "student_roll": "21CS042",
  "description": "Smartwatch detected under exam desk",
  "source_ip": "192.168.10.45",
  "is_emergency": false
}
```
- **Response**: Comprehensive 19-step receipt including TOC execution timings, CN routing destination, and dispatch allocation status (`ASSIGNED`, `ESCALATED`, or `QUEUED`).

### `GET /api/reports`
Retrieves list of reports with optional filters (`status`, `severity`, `category`, `limit`).

### `GET /api/reports/<id>`
Retrieves complete incident dossier including audit history, assignments, and validation logs.

### `PUT /api/reports/<id>/status`
Updates status (`IN_PROGRESS`, `RESOLVED`, `REJECTED`). Triggering `RESOLVED` automatically releases handler capacity and dequeues waiting reports.

### `GET /api/reports/export/csv`
Exports all database records as RFC 4180 CSV spreadsheet.

---

## 4. Computer Networks (CN) & Routing

### `GET /api/network-routes`
Lists all active routing table entries.

### `POST /api/network-routes/lookup`
Performs Longest Prefix Matching (LPM) on an arbitrary IPv4 address.
- **Request Body**: `{"destination_ip": "192.168.10.134"}`
- **Response**: Matched route, prefix length, next-hop IP, outgoing interface, metric, and LPM candidate search trace.

### `POST /api/network-routes/calculate-subnet`
Deterministic subnet calculator returning host ranges, wildcard masks, and subnet geometry.
- **Request Body**: `{"cidr": "192.168.10.0/24"}`

---

## 5. Dispatch & Handler Management

### `GET /api/handlers`
Lists all handlers with current active workload and capacity limits.

### `PUT /api/handlers/<id>/availability`
Toggles handler online/offline availability. Turning a handler online automatically dequeues pending incidents.

### `PUT /api/handlers/<id>/capacity`
Adjusts maximum capacity limit. Expanding capacity automatically triggers deterministic dequeueing.

### `GET /api/dispatch/queue`
Retrieves deterministic priority queue ordered by severity weight, submission timestamp, and report ID.

---

## 6. Administration & Demo Control

### `GET /api/routing-rules`
Lists 5-category lookup table rules.

### `PUT /api/routing-rules/<id>`
Admin modification of authority mappings with automatic audit history logging.

### `GET /api/routing-rules/history`
Returns audit log of all routing rule changes.

### `POST /api/demo/reset`
Instantaneously seeds the database with active, queued, and escalated incident scenarios for live hackathon jury demonstrations.

