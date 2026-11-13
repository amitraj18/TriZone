"""
Deterministic Finite Automata (DFA) Validation Engine
Formal Language and Computability (TOC) Foundation
--------------------------------------------------
Implements formal 5-tuple M = (Q, Sigma, delta, q0, F) for:
1. Invigilator ID: INV[DEPT][4-digit]
   - DEPT allowed: CSE, ECE, EEE, MECH, CIVIL, IT, AI, AIDS, etc. (standard: CSE, ECE, EEE, MECH, IT, CIV)
     Formal language: INV(CSE|ECE|EEE|MECH|IT)[0-9]{4}
   - Full state transitions tracked with transition log for visual inspection.
2. Irregularity Code: IR[2-digit]
   - Formal language: IR(01|02|03|04|05)
   - Unsupported codes strictly rejected by trap states.
"""

from typing import Dict, Any, List, Tuple, Optional

class DFAResult:
    def __init__(self, is_valid: bool, current_state: str, accepted: bool, trace: List[Dict[str, str]], reason: str = ""):
        self.is_valid = is_valid
        self.current_state = current_state
        self.accepted = accepted
        self.trace = trace
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "current_state": self.current_state,
            "accepted": self.accepted,
            "trace": self.trace,
            "reason": self.reason
        }


class InvigilatorDFA:
    """
    Formal DFA for Invigilator ID: INV[DEPT][4-digit]
    Standard supported departments: CSE, ECE, EEE, MECH, IT
    Examples: INVCSE0001, INVECE0001, INVEEE0001, INVMECH001, INVIT0001
    
    States:
    - q0: Start
    - q1: Read 'I'
    - q2: Read 'N'
    - q3: Read 'V'
    - q_dept states: Branching by department letters
    - q_d1, q_d2, q_d3, q_d4: Reading the 4 digits
    - q_accept: Accepting state (q_d4 after 4 digits and end of string)
    - q_trap: Dead / error state
    """
    START_STATE = "q0"
    TRAP_STATE = "q_trap"
    ACCEPT_STATE = "q_accept"

    def __init__(self):
        # Recognized departments
        self.departments = ["CSE", "ECE", "EEE", "MECH", "IT"]
        self._build_transitions()

    def _build_transitions(self):
        # Delta: (state, char) -> next_state
        self.delta: Dict[Tuple[str, str], str] = {}

        # Prefix 'INV'
        self.delta[("q0", "I")] = "q1"
        self.delta[("q1", "N")] = "q2"
        self.delta[("q2", "V")] = "q3"

        # From q3, branch into departments
        # 1. CSE: q3 -C-> q_c1 -S-> q_c2 -E-> q_dept_end
        self.delta[("q3", "C")] = "q_c1"
        self.delta[("q_c1", "S")] = "q_c2"
        self.delta[("q_c2", "E")] = "q_digits_start"

        # 2. ECE & EEE: q3 -E-> q_e1
        self.delta[("q3", "E")] = "q_e1"
        self.delta[("q_e1", "C")] = "q_ec1"
        self.delta[("q_ec1", "E")] = "q_digits_start"  # ECE
        self.delta[("q_e1", "E")] = "q_ee1"
        self.delta[("q_ee1", "E")] = "q_digits_start"  # EEE

        # 3. MECH: q3 -M-> q_m1 -E-> q_m2 -C-> q_m3 -H-> q_digits_start
        self.delta[("q3", "M")] = "q_m1"
        self.delta[("q_m1", "E")] = "q_m2"
        self.delta[("q_m2", "C")] = "q_m3"
        self.delta[("q_m3", "H")] = "q_digits_start"

        # 4. IT: q3 -I-> q_it1 -T-> q_digits_start
        # Note: from q3, 'I' begins IT
        self.delta[("q3", "I")] = "q_it1"
        self.delta[("q_it1", "T")] = "q_digits_start"

        # Four digits [0-9] from q_digits_start
        digits = [str(d) for d in range(10)]
        for d in digits:
            self.delta[("q_digits_start", d)] = "q_d1"
            self.delta[("q_d1", d)] = "q_d2"
            self.delta[("q_d2", d)] = "q_d3"
            self.delta[("q_d3", d)] = "q_accept"

        # Any extra characters after accept transition to trap
        for ch in [chr(c) for c in range(32, 127)]:
            self.delta[("q_accept", ch)] = "q_trap"
            self.delta[("q_trap", ch)] = "q_trap"

    def run(self, input_string: str) -> DFAResult:
        if not input_string:
            return DFAResult(
                is_valid=False,
                current_state=self.START_STATE,
                accepted=False,
                trace=[],
                reason="Input string cannot be empty."
            )

        current = self.START_STATE
        trace = []

        for idx, char in enumerate(input_string):
            key = (current, char)
            if key in self.delta:
                next_state = self.delta[key]
            else:
                next_state = self.TRAP_STATE

            trace.append({
                "step": idx + 1,
                "input_char": char,
                "from_state": current,
                "to_state": next_state
            })
            current = next_state

            if current == self.TRAP_STATE:
                break

        # Must be in q_accept state and string must be fully consumed
        is_accepted = (current == self.ACCEPT_STATE) and (len(trace) == len(input_string))

        reason = "Accepted: Conforms to INV[DEPT][4-digit] grammar." if is_accepted else \
                 f"Rejected: Failed at state '{current}' on input '{input_string}'."

        return DFAResult(
            is_valid=is_accepted,
            current_state=current,
            accepted=is_accepted,
            trace=trace,
            reason=reason
        )


class IrregularityDFA:
    """
    Formal DFA for Irregularity ID: IR[2-digit]
    Specifically restricted to authorized institutional codes:
    IR01, IR02, IR03, IR04, IR05
    
    States:
    - s0: Start
    - s1: Read 'I'
    - s2: Read 'R'
    - s3: Read '0'
    - s_ir01: Accept Malpractice
    - s_ir02: Accept Disturbance
    - s_ir03: Accept Medical
    - s_ir04: Accept Technical
    - s_ir05: Accept Missing-Script
    - s_trap: Invalid code trap state
    """
    START_STATE = "s0"
    TRAP_STATE = "s_trap"
    ACCEPTING_STATES = {"s_ir01", "s_ir02", "s_ir03", "s_ir04", "s_ir05"}

    def __init__(self):
        self._build_transitions()

    def _build_transitions(self):
        self.delta: Dict[Tuple[str, str], str] = {}

        self.delta[("s0", "I")] = "s1"
        self.delta[("s1", "R")] = "s2"
        self.delta[("s2", "0")] = "s3"

        # Specific authorized 2nd digits: 1 to 5
        self.delta[("s3", "1")] = "s_ir01"
        self.delta[("s3", "2")] = "s_ir02"
        self.delta[("s3", "3")] = "s_ir03"
        self.delta[("s3", "4")] = "s_ir04"
        self.delta[("s3", "5")] = "s_ir05"

        # Trap on any trailing characters from accept states
        for state in self.ACCEPTING_STATES:
            for ch in [chr(c) for c in range(32, 127)]:
                self.delta[(state, ch)] = "s_trap"

    def run(self, input_string: str) -> DFAResult:
        if not input_string:
            return DFAResult(
                is_valid=False,
                current_state=self.START_STATE,
                accepted=False,
                trace=[],
                reason="Input code cannot be empty."
            )

        current = self.START_STATE
        trace = []

        for idx, char in enumerate(input_string):
            key = (current, char)
            next_state = self.delta.get(key, self.TRAP_STATE)

            trace.append({
                "step": idx + 1,
                "input_char": char,
                "from_state": current,
                "to_state": next_state
            })
            current = next_state

            if current == self.TRAP_STATE:
                break

        is_accepted = (current in self.ACCEPTING_STATES) and (len(trace) == len(input_string))

        category_names = {
            "s_ir01": "IR01 (Malpractice)",
            "s_ir02": "IR02 (Disturbance)",
            "s_ir03": "IR03 (Medical)",
            "s_ir04": "IR04 (Technical)",
            "s_ir05": "IR05 (Missing-Script)"
        }

        if is_accepted:
            reason = f"Accepted: Valid code {category_names.get(current)}."
        else:
            reason = f"Rejected: Code '{input_string}' is not in authorized set {{IR01, IR02, IR03, IR04, IR05}}."

        return DFAResult(
            is_valid=is_accepted,
            current_state=current,
            accepted=is_accepted,
            trace=trace,
            reason=reason
        )

