"""
Deterministic Finite Automaton (DFA) for Irregularity ID Validation
Theory of Computation (TOC) Foundation
-------------------------------------------------------------------
Formal 5-Tuple Definition:
M = (S, Sigma, delta, s0, F)
- S: Finite set of states:
  {s0, s1, s2, s3,
   s_ir01, s_ir02, s_ir03, s_ir04, s_ir05,
   s_trap}
- Sigma: Allowed ASCII alphabet {A-Z, 0-9}
- s0: Initial start state 's0'
- F: Set of accepting states {s_ir01, s_ir02, s_ir03, s_ir04, s_ir05}
- delta: Transition function S x Sigma -> S

Language Accepted:
L(M) = { "IR01", "IR02", "IR03", "IR04", "IR05" }
Strictly rejects unsupported codes such as IR06, IR99, IR1, IR001, ABC01.
"""

import time
from typing import Dict, Any, List, Tuple

class IrregularityDFA:
    START_STATE = "s0"
    TRAP_STATE = "s_trap"
    ACCEPT_STATES = {"s_ir01", "s_ir02", "s_ir03", "s_ir04", "s_ir05"}

    CODE_CATEGORY_MAP = {
        "s_ir01": ("IR01", "Malpractice"),
        "s_ir02": ("IR02", "Disturbance"),
        "s_ir03": ("IR03", "Medical"),
        "s_ir04": ("IR04", "Technical"),
        "s_ir05": ("IR05", "Missing-Script"),
    }

    def __init__(self):
        self._build_transition_table()

    def _build_transition_table(self):
        """Constructs explicit transition table delta: (state, char) -> next_state"""
        self.delta: Dict[Tuple[str, str], str] = {}

        # 1. Prefix 'IR0'
        self.delta[("s0", "I")] = "s1"
        self.delta[("s1", "R")] = "s2"
        self.delta[("s2", "0")] = "s3"

        # 2. Fifth character: exactly '1' through '5'
        self.delta[("s3", "1")] = "s_ir01"
        self.delta[("s3", "2")] = "s_ir02"
        self.delta[("s3", "3")] = "s_ir03"
        self.delta[("s3", "4")] = "s_ir04"
        self.delta[("s3", "5")] = "s_ir05"

        # Any character after accept leads to trap state
        # In s_trap, all transitions loop back to s_trap

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
                "category": None,
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
        is_accepted = (current_state in self.ACCEPT_STATES) and (len(trace) == len(input_string))

        cat_info = self.CODE_CATEGORY_MAP.get(current_state)
        category_name = cat_info[1] if cat_info else None

        reason = ""
        if is_accepted:
            reason = f"Accepted: Valid irregularity code {cat_info[0]} ({category_name})."
        elif current_state == self.TRAP_STATE:
            reason = f"Rejected: Illegal character or unsupported code '{input_string}'. Allowed: IR01-IR05."
        else:
            reason = f"Rejected: Incomplete code sequence ending in non-accepting state '{current_state}'."

        return {
            "input": input_string,
            "is_valid": is_accepted,
            "accepted": is_accepted,
            "final_state": current_state,
            "category": category_name,
            "execution_time_ns": duration_ns,
            "trace": trace,
            "reason": reason
        }

