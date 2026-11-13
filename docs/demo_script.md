# IRIS — Hackathon Live Demonstration Script

Follow this step-by-step walkthrough during the hackathon jury evaluation to demonstrate the synergy of **Automata Theory (TOC)**, **Computer Networks (CN)**, and **Full-Stack Engineering**.

---

## Pre-Demo Quick Reset (10 Seconds)
1. Open the web interface at `http://localhost:5173`.
2. Look at the top bar and click the orange **"Reset Demo State"** button (or call `POST /api/demo/reset`).
3. Notice the toast: *"Demo state restored with 6 live incident scenarios"*.
4. All KPI cards, priority queues, and charts immediately populate with real database records.

---

## Scenario 1: Theory of Computation (TOC) Formal Verification
**Objective**: Prove character-by-character DFA execution and formal equivalence with Regex.

1. Navigate to **"Report Submission"** in the sidebar.
2. Toggle the **"Interactive DFA Stepper & Tape Visualizer"** switch.
3. In the Invigilator ID field, type `INVCSE0001`:
   - Watch the tape head advance character-by-character across states:
     $q_0 \xrightarrow{\text{I}} q_1 \xrightarrow{\text{N}} q_2 \xrightarrow{\text{V}} q_3 \xrightarrow{\text{C}} q_{C} \xrightarrow{\text{S}} q_{CS} \xrightarrow{\text{E}} q_{dept} \dots \xrightarrow{1} q_{d4}$ (Accepting).
   - Point out the nanosecond benchmark clock comparing DFA ($\approx 25\,\mu\text{s}$) vs Regex ($\approx 18\,\mu\text{s}$).
4. Now delete the last digit so it is `INVCSE000`:
   - Observe immediate rejection: DFA trapped in state $q_{d3}$ (Requires exactly 4 digits).
5. Now enter an invalid department code like `INVXYZ9999`:
   - Observe DFA transition directly into Dead State $q_{dead}$.

---

## Scenario 2: Computer Networks (CN) Longest Prefix Matching (LPM)
**Objective**: Prove Layer-3 IP subnet calculations and overlapping route selection.

1. Navigate to **"Network Management"** in the sidebar.
2. Under **LPM Forwarding Engine Simulator**, select the pre-filled IP `192.168.10.134` (Lab 3 Terminal) and click **"Run LPM Route Lookup"**.
3. Point out the candidate trace:
   - Candidate 1: `192.168.10.0/24` (Dept Subnet, Prefix 24)
   - Candidate 2: `192.168.10.128/25` (Specialized Lab, Prefix 25)
   - Candidate 3: `0.0.0.0/0` (Default Backbone, Prefix 0)
4. Show that the router **selected Candidate 2** because $25 > 24$ (Longest Prefix Match). Interface `eth0.100`, Next-Hop `192.168.10.254`.
5. Enter `192.168.10.45` (Hall 401 Terminal):
   - Notice that this IP is $< 128$, so it does NOT match `/25`. The router cleanly falls back to `/24` via interface `eth0`.
6. Test the **Subnet Geometry Calculator**: enter `192.168.20.0/24` to compute usable hosts ($254$), network/broadcast addresses, and inverted wildcard mask (`0.0.0.255`).

---

## Scenario 3: Intelligent Dispatch, Backup Escalation & Priority Queue
**Objective**: Demonstrate capacity saturation, deterministic priority queueing, and auto-dequeueing.

1. Navigate to **"Handler Management"**.
2. Point out the handlers' live workload capacity bars:
   - Primary handlers for Chief Superintendent are at capacity ($2/2$).
3. Navigate to **"Report Submission"**:
   - Submit an **Emergency Medical Incident** (`IR03`, Hall-204, `192.168.20.12`).
   - Notice the status: **ASSIGNED** or **ESCALATED** depending on backup capacity.
4. Now submit another incident when all handlers for that authority are full:
   - Watch the report automatically enter status **QUEUED**.
5. Return to **"Handler Management"**:
   - Show the waiting report at the top of the **Deterministic Priority Queue** table.
   - Point out the ordering: `CRITICAL` incidents jump ahead of `MEDIUM` and `LOW` incidents.
6. Now click **"Resolve"** on an active report in **"User Dashboard"** (or increase handler capacity in Handler Management):
   - **Watch the system automatically dequeue the highest-priority waiting report** and assign it to the newly freed handler in real time!

---

## Scenario 4: Full-Stack Auditability, CSV Export & RBAC
**Objective**: Show institutional grade integrity and data portability.

1. Click **"Export CSV"** in the top bar:
   - Downloads `iris_exam_reports_export.csv` containing all 16 standardized audit columns.
2. In the top bar, click the user badge to open the **Role Switcher**:
   - Switch between **Admin**, **Invigilator**, and **Handler** to demonstrate RBAC authorization.
3. Navigate to **"Routing Rules"**:
   - Click **"Edit Rule"** on `IR02` to update the escalation authority.
   - Show the **Audit History** table below, proving every policy change is permanently logged with timestamp and author.

