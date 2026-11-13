# Automata Theory (TOC) — Formal DFA State Diagrams

IRIS formally validates all input tokens character-by-character using Deterministic Finite Automata (DFA) defined as 5-tuples:
$$M = (Q, \Sigma, \delta, q_0, F)$$

---

## 1. Invigilator ID DFA ($M_{\text{inv}}$)
**Grammar**: `INV` followed by department code (`CSE`, `ECE`, `EEE`, `CIV`, `ME`, `MECH`), followed by 4 digits $[0-9]^4$.

```mermaid
stateDiagram-v2
    [*] --> q0
    q0 --> q1 : 'I'
    q1 --> q2 : 'N'
    q2 --> q3 : 'V'
    
    %% Department branches
    q3 --> q_C : 'C'
    q3 --> q_E : 'E'
    q3 --> q_M : 'M'

    %% C branch
    q_C --> q_CS : 'S'
    q_C --> q_CI : 'I'
    q_CS --> q_dept : 'E'
    q_CI --> q_dept : 'V'

    %% E branch
    q_E --> q_EC : 'C'
    q_E --> q_EE : 'E'
    q_EC --> q_dept : 'E'
    q_EE --> q_dept : 'E'

    %% M branch
    q_M --> q_dept : 'E'
    q_M --> q_MECH1 : 'E'
    q_MECH1 --> q_MECH2 : 'C'
    q_MECH2 --> q_dept : 'H'

    %% Digit Counter (4 digits)
    q_dept --> q_d1 : [0-9]
    q_d1 --> q_d2 : [0-9]
    q_d2 --> q_d3 : [0-9]
    q_d3 --> q_d4 : [0-9]

    %% Accepting State
    q_d4 --> [*] : Accepting (F)

    %% Dead / Trap State for all invalid transitions
    q0 --> q_dead : [^I]
    q1 --> q_dead : [^N]
    q2 --> q_dead : [^V]
    q_d4 --> q_dead : [Any Character]
    q_dead --> q_dead : [Any Character]
```

---

## 2. Irregularity ID DFA ($M_{\text{irr}}$)
**Language**: Strictly accepts $L = \{ \text{IR01}, \text{IR02}, \text{IR03}, \text{IR04}, \text{IR05} \}$. Rejects IR06-IR99, IR1, IR001, etc.

```mermaid
stateDiagram-v2
    [*] --> s0
    s0 --> s1 : 'I'
    s1 --> s2 : 'R'
    s2 --> s3 : '0'
    s3 --> s_accept : '1', '2', '3', '4', '5'

    s_accept --> [*] : Accepting State

    %% Rejection transitions to dead state
    s0 --> s_dead : [^I]
    s1 --> s_dead : [^R]
    s2 --> s_dead : [^0]
    s3 --> s_dead : [^1-5]
    s_accept --> s_dead : [Any Character]
    s_dead --> s_dead : [Any Character]
```

---

## 3. Formal Equivalence & Benchmark Assertion
Each input token is evaluated through both:
1. $M(w)$: Character-by-character DFA simulator.
2. $R(w)$: Compiled POSIX Regex (`re.fullmatch()`).

Both algorithms record timestamp delta in nanoseconds using Python `time.perf_counter_ns()`:
$$\Delta t = t_{\text{end}} - t_{\text{start}}$$

If $M(w) \neq R(w)$, IRIS aborts ingestion immediately with an `ENGINE_EQUIVALENCE_CONFLICT` failure.

