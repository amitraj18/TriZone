# Viva Defense Notes & Technical Q&A — IRIS

Use these notes to confidently answer academic jury questions across Automata Theory, Computer Networks, and Full-Stack Engineering.

---

## 1. Theory of Computation (TOC) Questions

### Q1: Why use a formal DFA instead of just a regular expression?
**Answer**:
A regular expression engine in high-level languages uses backtracking or an NFA-to-DFA conversion internally. By explicitly constructing a deterministic finite state machine with transition tables:
1. We achieve strictly linear $O(n)$ time complexity with zero backtracking risks (guaranteed defense against Regular Expression Denial of Service / ReDoS).
2. We can visualize and inspect state transitions character-by-character (e.g. stepping from initial state $q_0$ to $q_{dept}$ to $q_{d4}$).
3. In IRIS, we execute **both** DFA and Regex independently and benchmark nanosecond execution time using `time.perf_counter_ns()`. If they disagree, an engine conflict is raised, ensuring formal mathematical verification.

### Q2: What is the formal 5-tuple of your Invigilator DFA?
**Answer**:
$M_{\text{inv}} = (Q, \Sigma, \delta, q_0, F)$
- $Q$: 19 states ($q_0 \dots q_3$, department branch states $q_C, q_{CS}, q_E, q_{EC}, q_{EE}, q_M, q_{MECH1}, q_{MECH2}$, unified department state $q_{dept}$, digit states $q_{d1}, q_{d2}, q_{d3}, q_{d4}$, and dead state $q_{dead}$).
- $\Sigma$: ASCII characters $[A-Z, 0-9]$.
- $\delta: Q \times \Sigma \to Q$: The deterministic transition function.
- $q_0$: Initial state $q_0$.
- $F$: Singleton set $\{ q_{d4} \}$.

### Q3: Why is the Irregularity ID regular, and how is it bounded?
**Answer**:
The language of irregularity IDs is finite: $L = \{ \text{IR01}, \text{IR02}, \text{IR03}, \text{IR04}, \text{IR05} \}$. Because every finite language is regular (as it can be represented by the union of singleton regular sets), it is strictly recognizable by a finite automaton with no memory (stack) required.

---

## 2. Computer Networks (CN) Questions

### Q1: How does Longest Prefix Matching (LPM) work in IRIS?
**Answer**:
When an irregularity is submitted, IRIS resolves the target authority's destination IP address and queries the Layer-3 routing table. For every active routing entry:
1. The routing network is converted to an `ipaddress.IPv4Network` object.
2. If the destination IP falls within the network, the route is added to candidate matches.
3. The candidates are sorted primarily by **prefix length descending** (longest mask), secondarily by **routing metric ascending** (lowest administrative distance/cost).
4. For example, terminal `192.168.10.134` matches both `192.168.10.0/24` and `192.168.10.128/25`. LPM deterministically selects the `/25` route because $25 > 24$.

### Q2: How does the Subnet Calculator compute the wildcard mask and usable hosts?
**Answer**:
- Usable hosts for prefix $p < 31$ is $2^{(32 - p)} - 2$ (excluding network and broadcast addresses).
- For a /24 subnet, $2^8 - 2 = 254$ usable hosts.
- The wildcard mask is computed via bitwise XOR with the 32-bit broadcast mask:
  $$\text{Wildcard} = \text{0xFFFFFFFF} \oplus \text{Netmask}$$
  For `255.255.255.0` (`0xFFFFFF00`), wildcard is `0.0.0.255`.

### Q3: Why distinguish simulated network routing from actual physical packet transmission?
**Answer**:
In an examination operations center, incidents are submitted over software web forms. Simulating Layer-3 IP routing demonstrates software-defined network (SDN) awareness—validating that the invigilator's physical examination hall matches the assigned departmental IP subnet before routing packet telemetry to the superintendent's network interface.

---

## 3. Full-Stack & Systems Questions

### Q1: How is deterministic queueing implemented without starvation?
**Answer**:
The priority queue is implemented deterministically in SQLite using:
`ORDER BY priority_weight DESC, created_at ASC, id ASC`
- Priority weights: `CRITICAL` (4) > `HIGH` (3) > `MEDIUM` (2) > `LOW` (1).
- Emergency reports jump to `CRITICAL` immediately.
- Between reports of the same priority, `created_at ASC` guarantees First-In-First-Out (FIFO) processing to prevent starvation of older incidents.
- Primary key `id ASC` acts as an absolute tie-breaker.

### Q2: What happens when an incident is resolved?
**Answer**:
When an incident is transitioned to `RESOLVED`:
1. The assigned handler's `current_load` is decremented by 1.
2. The `assignments` and `status_history` tables record resolution audit details.
3. The queue manager is automatically triggered: it queries the top-priority waiting report from the queue matching that authority's jurisdiction and immediately dispatches it to the newly available handler within a single atomic database transaction.

### Q3: How is data consistency protected in SQLite?
**Answer**:
We use Python context managers with `PRAGMA foreign_keys = ON`. Transactions automatically `COMMIT` upon block exit or `ROLLBACK` on exception. Every schema table uses strict relational foreign key constraints and primary keys.

