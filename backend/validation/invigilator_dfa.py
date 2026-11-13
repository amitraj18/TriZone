"""
Deterministic Finite Automaton (DFA) for Invigilator ID Validation
Theory of Computation (TOC) Foundation
-------------------------------------------------------------------
Formal 5-Tuple Definition:
M = (Q, Sigma, delta, q0, F)
- Q: Finite set of states:
  {q0, q1, q2, q3,
   q_c, q_cs, q_ci,
   q_e, q_ec, q_ee,
   q_m, q_me, q_mec,
   q_dept,
   q_d1, q_d2, q_d3, q_accept,
   q_trap}
- Sigma: Allowed ASCII alphabet {A-Z, 0-9}
- q0: Initial start state 'q0'
- F: Set of accepting states {q_accept}
- delta: Transition function Q x Sigma -> Q

Language Accepted:
L(M) = { INV . DEPT . d1 d2 d3 d4 | DEPT in {CSE, ECE, EEE, CIV, ME, MECH}, di in [0-9] }
"""

import time
from typing import Dict, Any, List, Tuple

class InvigilatorDFA:
    START_STATE = "q0"
    ACCEPT_STATE = "q_accept"
    TRAP_STATE = "q_trap"

    # Supported academic departments
    SUPPORTED_DEPTS = ["CSE", "ECE", "EEE", "CIV", "ME", "MECH"]

    def __init__(self):
        self._build_transition_table()

    def _build_transition_table(self):
        """Constructs explicit transition table delta: (state, char) -> next_state"""
        self.delta: Dict[Tuple[str, str], str] = {}

        # 1. Prefix 'INV'
        self.delta[("q0", "I")] = "q1"
        self.delta[("q1", "N")] = "q2"
        self.delta[("q2", "V")] = "q3"

        # 2. Department Branches from q3:
        # Branch C: CSE, CIV
        self.delta[("q3", "C")] = "q_c"
        self.delta[("q_c", "S")] = "q_cs"
        self.delta[("q_cs", "E")] = "q_dept"   # 'CSE' complete

        self.delta[("q_c", "I")] = "q_ci"
        self.delta[("q_ci", "V")] = "q_dept"   # 'CIV' complete

        # Branch E: ECE, EEE
        self.delta[("q3", "E")] = "q_e"
        self.delta[("q_e", "C")] = "q_ec"
        self.delta[("q_ec", "E")] = "q_dept"   # 'ECE' complete

        self.delta[("q_e", "E")] = "q_ee"
        self.delta[("q_ee", "E")] = "q_dept"   # 'EEE' complete

        # Branch M: ME, MECH
        self.delta[("q3", "M")] = "q_m"
        self.delta[("q_m", "E")] = "q_me"      # 'ME' complete
        # From q_me, can either go to digits directly (INVME0001) or continue with 'CH' (INVMECH0001)
        self.delta[("q_me", "C")] = "q_mec"
        self.delta[("q_mec", "H")] = "q_dept"  # 'MECH' complete

        digits = [str(d) for d in range(10)]

        # From q_me, if first digit arrives: transitions directly to q_d1 (for 2-letter dept ME)
        for d in digits:
            self.delta[("q_me", d)] = "q_d1"

        # 3. Exactly 4 digits from q_dept
        for d in digits:
            self.delta[("q_dept", d)] = "q_d1"
            self.delta[("q_d1", d)] = "q_d2"
            self.delta[("q_d2", d)] = "q_d3"
            self.delta[("q_d3", d)] = "q_accept"

        # Any character after accept leads to trap state
        # In q_trap, all transitions loop back to q_trap

    def step(self, current_state: str, char: str) -> str:
        """Processes a single input character according to delta transition function."""
        if current_state == self.TRAP_STATE:
            return self.TRAP_STATE
        return self.delta.get((current_state, char), self.TRAP_STATE)

    def validate(self, input_string: str) -> Dict[str, Any]:
        """
        Executes character-by-character DFA simulation.
        Measures exact duration in nanoseconds using time.perf_counter_ns().
        Returns state transition trace and formal decision.
        """
        t0 = time.perf_counter_ns()

        if not isinstance(input_string, str) or len(input_string) == 0:
            duration_ns = time.perf_counter_ns() - t0
            return {
                "input": input_string,
                "is_valid": False,
                "accepted": False,
                "final_state": self.START_STATE,
                "execution_time_ns": duration_ns,
                "trace": [],
                "reason": "Input cannot be empty or non-string."
            }

        current_state = self.START_STATE
        trace: List[Dict[str, Any]] = []

        for idx, char in enumerate(input_string):
            next_state = self.step(current_state, char)
            trace.append({
                "step": idx + 1,
                "char": char,
                "from_state": current_state,
                "to_state": next_state,
                "is_trap": (next_state == self.TRAP_STATE)
            })
            current_state = next_state
            if current_state == self.TRAP_STATE:
                # Add remaining characters to trace as trap if any
                for rem_idx, rem_char in enumerate(input_string[idx + 1:], start=idx + 2):
                    trace.append({
                        "step": rem_idx,
                        "char": rem_char,
                        "from_state": self.TRAP_STATE,
                        "to_state": self.TRAP_STATE,
                        "is_trap": True
                    })
                break

        duration_ns = time.perf_counter_ns() - t0
        is_accepted = (current_state == self.ACCEPT_STATE) and (len(trace) == len(input_string))

        # Determine rejection reason
        reason = ""
        if is_accepted:
            reason = "Accepted: Conforms to INV[DEPT][4-digit] grammar."
        elif current_state == self.TRAP_STATE:
            reason = f"Rejected: Encountered illegal character transition leading to trap state '{self.TRAP_STATE}'."
        else:
            reason = f"Rejected: Input terminated prematurely in non-accepting state '{current_state}'."

        return {
            "input": input_string,
            "is_valid": is_accepted,
            "accepted": is_accepted,
            "final_state": current_state,
            "execution_time_ns": duration_ns,
            "trace": trace,
            "reason": reason
        }

