# Exam Hall Irregularity Reporter (IRIS)
### Institutional Incident Management, Automata Theory (TOC) & Network Routing (CN) Platform

IRIS (**Irregularity Reporting & Incident System**) is an institutional examination hall administration product designed for universities and testing centers. It integrates theoretical computer science foundations (**Automata Theory & Computability**), systems networking (**Computer Networks & Layer-3 Routing**), and operational full-stack engineering.

---

## 1. System Architecture

```
TriZone/
├── backend/
│   ├── app.py                         # REST controllers & 19-step submission pipeline
│   ├── config.py                      # System configuration & SQLite database path
│   ├── wsgi.py                        # Production WSGI application entry point
│   ├── exam_reporter.db               # Primary SQLite database (13 relational tables)
│   ├── requirements.txt               # Dependencies (Flask, Flask-CORS, Pytest)
│   ├── auth/                          # RBAC Authentication & HMAC token service
│   │   └── auth_service.py
│   ├── notifications/                 # Persistent in-app notification engine
│   │   └── notification_service.py
│   ├── export/                        # RFC 4180 CSV export generator
│   │   └── csv_exporter.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py              # Dynamic connection resolver & transaction context
│   │   ├── schema.sql                 # 13 relational entities, indexes & constraints
│   │   ├── models.py                  # Data Access Objects (DAO)
│   │   ├── seed_data.py               # Seed data bootstrapper
│   │   └── demo_seeder.py             # Hackathon demo state resetter
│   ├── validation/                    # [TOC] Automata Theory & Regular Expressions
│   │   ├── __init__.py
│   │   ├── invigilator_dfa.py         # Character-by-character Invigilator ID DFA
│   │   ├── irregularity_dfa.py        # 6-State authorized code DFA
│   │   ├── regex_validator.py         # Equivalent regex validators & ns timing
│   │   └── validation_service.py      # Equivalence assertor & SQLite audit logger
│   ├── networking/                    # [CN] Computer Networks & Subnet Routing
│   │   ├── __init__.py
│   │   ├── ip_addressing.py           # IPv4 parser & examination zone bindings
│   │   ├── subnet_calculator.py       # Host ranges, wildcard masks & overlap logic
│   │   ├── network_routing.py         # Longest Prefix Matching (LPM) router
│   │   └── routing_service.py         # Source zone verification & destination routing
│   ├── dispatch/                      # [Operations] Statutory Authority Dispatch
│   │   ├── __init__.py
│   │   ├── priority_manager.py        # Default priorities & emergency critical override
│   │   ├── handler_manager.py         # Workload balancer, capacity & backup escalation
│   │   ├── queue_manager.py           # Deterministic priority queue processor
│   │   └── dispatch_engine.py         # Transactional lifecycle coordinator
│   └── tests/
│       ├── test_auth_features.py      # Auth, notifications, CSV, subnet & demo tests (9 tests)
│       ├── test_health.py             # Health & database checks (5 tests)
│       ├── test_dfa_regex.py          # TOC DFA, Regex & agreement tests (9 tests)
│       ├── test_networking.py         # Subnet calculation & LPM tests (13 tests)
│       ├── test_dispatch.py           # Capacity, backup & queue tests (7 tests)
│       └── test_integration.py        # 19-Step end-to-end pipeline tests (8 tests)
├── frontend/
│   ├── index.html                     # Responsive HTML shell
│   ├── vite.config.js                 # Vite bundler & reverse proxy
│   ├── tailwind.config.js             # Institutional orange design tokens
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                    # Root coordinator & active tab router
│       ├── api/client.js              # REST client with full API bindings
│       ├── components/
│       │   ├── Sidebar.jsx            # Fixed left navigation sidebar with live health pulse
│       │   ├── Topbar.jsx             # Top institutional header with notifications & role switcher
│       │   ├── DfaVisualizer.jsx      # Character-by-character interactive DFA tape visualizer
│       │   ├── NetworkTopology.jsx    # Layer-3 academic network topology diagram
│       │   ├── StatCard.jsx           # Compact KPI cards
│       │   └── StatusBadge.jsx        # Status & severity badges
│       └── pages/
│           ├── UserDashboard.jsx      # Live SQLite incidents feed, filter tabs & details dossier
│           ├── ReportSubmission.jsx   # Live report submission, DFA trace & routing receipts
│           ├── HandlerDashboard.jsx   # Real-time workload bars, availability & queue viewer
│           ├── RoutingDashboard.jsx   # Explicit authority lookup matrix & admin edit modal
│           ├── NetworkDashboard.jsx   # Live LPM lookup console & subnet calculator
│           └── AnalyticsDashboard.jsx # Real-time SQLite charts (Recharts)
├── docs/                              # System diagrams, specifications & viva notes
│   ├── architecture.md
│   ├── dfa_state_diagrams.md
│   ├── network_topology.md
│   ├── report_processing_flowchart.md
│   ├── database_er_diagram.md
│   ├── dispatch_flowchart.md
│   ├── api_reference.md
│   ├── demo_script.md
│   └── viva_notes.md
└── README.md
```

---

## 2. Theoretical Foundations & Algorithmic Modules

### Module 1: Theory of Computation (TOC) — Formal DFA & Regex

#### 1. Invigilator ID DFA: `INV[DEPT][4-digit]`
- **Formal 5-Tuple**: $M = (Q, \Sigma, \delta, q_0, F)$
  - $Q = \{q_0, q_1, q_2, q_3, q_c, q_{cs}, q_{ci}, q_e, q_{ec}, q_{ee}, q_m, q_{me}, q_{mec}, q_{dept}, q_{d1}, q_{d2}, q_{d3}, q_{accept}, q_{trap}\}$
  - $\Sigma = \{A-Z, 0-9\}$
  - $q_0 = \text{'q0'}$
  - $F = \{q_{accept}\}$
- **Language**: $L(M) = \{ \text{INV} \cdot \text{DEPT} \cdot d_1 d_2 d_3 d_4 \mid \text{DEPT} \in \{\text{CSE}, \text{ECE}, \text{EEE}, \text{CIV}, \text{ME}, \text{MECH}\}, d_i \in [0-9] \}$
- **Execution**: The DFA processes the string strictly character by character. Any invalid character transitions directly into $q_{trap}$.
- **Equivalent Regex**: `^INV(CSE|ECE|EEE|CIV|ME|MECH)\d{4}$` evaluated with `re.fullmatch()`.

#### 2. Irregularity Code DFA: `IR[2-digit]`
- **Formal 5-Tuple**: $M_2 = (S, \Sigma, \delta_2, s_0, F_2)$
  - $S = \{s_0, s_1, s_2, s_3, s_{ir01}, s_{ir02}, s_{ir03}, s_{ir04}, s_{ir05}, s_{trap}\}$
  - $F_2 = \{s_{ir01}, s_{ir02}, s_{ir03}, s_{ir04}, s_{ir05}\}$
- **Language**: Only accepts the 5 authorized institutional codes:
  - `IR01` &mdash; Malpractice
  - `IR02` &mdash; Disturbance
  - `IR03` &mdash; Medical Emergency
  - `IR04` &mdash; Technical Interruption
  - `IR05` &mdash; Missing-Script Audit
- **Strict Rejection**: Rejecting codes outside this set (`IR06`, `IR99`, `IR1`, `ABC01`, lowercase, etc.).
- **Equivalent Regex**: `^IR0[1-5]$` evaluated with `re.fullmatch()`.

#### 3. Formal Equivalence & Timing Assertion
Every input passes through both the DFA and the Regex validator:
- Execution time measured in nanoseconds using `time.perf_counter_ns()`.
- Agreement condition verified: `dfa_result == regex_result`.
- If DFA and Regex disagree, an engine conflict error is raised, preventing further processing.
- All decisions, nanosecond measurements, and agreement states are logged into `validation_logs` in SQLite.

---

### Module 2: Computer Networks (CN) — IP Subnetting & Longest Prefix Matching (LPM)

#### 1. Examination Zone Source Verification
Every physical examination room has a designated Layer-3 subnet:
- `HALL-401` / `HALL-302` (CSE Main): `192.168.10.0/24`
- `LAB-3` (Specialized Lab): `192.168.10.128/25`
- `HALL-204` (ECE): `192.168.20.0/24`
- `HALL-102` (EEE): `192.168.30.0/24`
- `ADMIN-01` (Control Wing): `192.168.40.0/24`

The invigilator terminal's `source_ip` is verified against the hall's assigned subnet using Python's `ipaddress` library before transmission.

#### 2. Longest Prefix Matching (LPM) Forwarding Algorithm
Authority services are bound to simulated service destination IPs:
- Chief Superintendent: `192.168.40.10`
- Centre Superintendent: `192.168.40.20`
- Controller of Examinations: `192.168.40.30`

When forwarding a packet to destination IP:
1. Enumerate all active routing entries in `network_routes`.
2. Filter candidate routes where $\text{destination\_ip} \in \text{route.network}$.
3. Sort candidate routes by `prefix_length` DESC (Longest Prefix Match).
4. **Tie-Breaker**: If two routes have identical prefix lengths, select the route with the lowest `metric` (cost).
5. **Overlapping Subnet Proof**: Address `192.168.10.134` falls inside both `192.168.10.0/24` and `192.168.10.128/25`. The algorithm selects `/25` because $25 > 24$.
6. **Default Route**: External or unmatched addresses fall back to `0.0.0.0/0`.
7. **Unreachable**: If no route matches and no default route is configured, the destination is marked unreachable.

---

### Module 3: Dispatch Engine — Workload Balancing, Escalation & Priority Queue

#### 1. Authority Jurisdiction Matrix (Explicit O(1) Lookup)
Read dynamically from SQLite `routing_rules`:
- `IR01` (Malpractice) $\to$ **Chief Superintendent** (Escalation: Controller of Examinations)
- `IR02` (Disturbance) $\to$ **Centre Superintendent** (Escalation: Chief Superintendent)
- `IR03` (Medical) $\to$ **Chief Superintendent** (Escalation: Campus Medical Officer)
- `IR04` (Technical) $\to$ **Centre Superintendent** (Escalation: Technical Support Lead)
- `IR05` (Missing-Script) $\to$ **Controller of Examinations** (Escalation: Chief Superintendent)

#### 2. Emergency Priority Override
Default priorities: IR01 (High), IR02 (Medium), IR03 (Critical), IR04 (Medium), IR05 (High).
- When flagged as an emergency, priority is elevated to `CRITICAL`.
- Preserves original category, logs override reason, and records ISO timestamp.

#### 3. Deterministic Handler Selection & Capacity
- Criteria: `role == target_authority`, `is_available == 1`, and `current_load < capacity`.
- Sorted by:
  1. Primary eligible handler.
  2. Lowest current workload (`current_load ASC`).
  3. Stable tie-breaker (`handler_uid ASC`).
- Backup Escalation: If primary handlers are full, assigns eligible handler from `escalation_authority` marked as `BACKUP`.

#### 4. Deterministic Priority Queue
If all primary and backup handlers are at full capacity:
- Report enters `QUEUED` status in SQLite.
- Sorted deterministically:
  1. Priority tier: `CRITICAL` (4) > `HIGH` (3) > `MEDIUM` (2) > `LOW` (1)
  2. Submission timestamp (`created_at ASC`)
  3. Report ID (`id ASC`)
- Automatic Dequeueing: When any handler resolves an incident, becomes available, or increases capacity, the queue processor instantly assigns the next waiting report.

---

## 3. REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health-check endpoint verifying Flask & SQLite connection |
| `POST` | `/api/reports/validate` | Validates Invigilator ID & IR code via DFA + Regex |
| `POST` | `/api/reports` | Complete 19-step submission, routing & dispatch pipeline |
| `GET` | `/api/reports` | List reports with optional `status` or `category` filters |
| `GET` | `/api/reports/<id>` | Full incident dossier (validation logs, history, assignments) |
| `GET` | `/api/reports/<id>/history`| Status transition audit history |
| `PUT` | `/api/reports/<id>/status` | Update incident status (`IN_PROGRESS`, `RESOLVED`, etc.) |
| `POST` | `/api/reports/<id>/assign` | Manually assign or reassign handler |
| `GET` | `/api/network-routes` | List all active Layer-3 network routes |
| `POST` | `/api/network-routes/lookup` | Execute Longest Prefix Match (LPM) on destination IP |
| `GET` | `/api/handlers` | List handlers with capacity, current load & availability |
| `PUT` | `/api/handlers/<id>/availability` | Toggle handler availability (triggers queue processing) |
| `PUT` | `/api/handlers/<id>/capacity` | Update handler max capacity (triggers queue processing) |
| `GET` | `/api/dispatch/queue` | List waiting reports ordered by priority queue rank |
| `GET` | `/api/dispatch/logs` | Audit trail of dispatch decisions |
| `GET` | `/api/routing-rules` | Query explicit authority routing table |
| `GET` | `/api/categories` | Query standard irregularity categories |
| `GET` | `/api/stats` | High-level KPI metrics for dashboards |

---

## 4. Test Suite & Verification Results

Pytest automated test suite: **51 / 51 passed (100%)**

```powershell
backend> python -m pytest tests/
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\amitr\OneDrive\Desktop\TriZone\backend
collected 51 items

tests\test_auth_features.py .........                                    [ 17%]
tests\test_dfa_regex.py .........                                        [ 35%]
tests\test_dispatch.py .......                                           [ 49%]
tests\test_health.py .....                                               [ 58%]
tests\test_integration.py ........                                       [ 74%]
tests\test_networking.py .............                                   [100%]

============================= 51 passed in 40.38s =============================
```

- `test_auth_features.py` (9 tests): Validates HMAC-SHA256 tokens, RBAC roles, persistent in-app notifications, RFC 4180 CSV export generation, CIDR subnet calculator, admin routing rule audit trails, and demo resetter.
- `test_dfa_regex.py` (9 tests): Validates invigilator DFA, irregularity DFA, regex matching, character traces, rejected codes, and nanosecond timing comparison.
- `test_networking.py` (13 tests): Validates subnet math, CIDR ranges, source IP zone matching, /25 vs /24 overlapping LPM, metric tie-breakers, and default route fallback.
- `test_dispatch.py` (7 tests): Validates authority routing from SQLite, workload balancing, backup escalation, capacity overflow queueing, and priority order.
- `test_integration.py` (8 tests): Validates end-to-end report intake, rejection of malformed IDs, source IP subnet violations, handler resolution cycles, and automatic queue dequeueing.
- `test_health.py` (5 tests): Verifies health check endpoints and SQLite database connectivity.

---

## 5. Running the Application Locally

### Step 1: Start Backend (Flask)
```powershell
cd c:\Users\amitr\OneDrive\Desktop\TriZone\backend
python -m pytest tests/
python app.py
```
*API live at `http://127.0.0.1:5000`*

### Step 2: Start Frontend (React + Vite)
```powershell
cd c:\Users\amitr\OneDrive\Desktop\TriZone\frontend
npm run dev
```
*Frontend live at `http://localhost:3000`*
