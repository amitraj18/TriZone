r"""
Regular Expression Validator
Theory of Computation (TOC) Formal Equivalence Check
-----------------------------------------------------
Implements equivalent regular expression pattern matchers using Python's
re.fullmatch() to cross-verify against DFA state machine decisions.

Patterns:
- Invigilator ID: ^INV(CSE|ECE|EEE|CIV|ME|MECH)\d{4}$
- Irregularity Code: ^IR0[1-5]$
"""

import re
import time
from typing import Dict, Any

INVIGILATOR_REGEX_PATTERN = r"^INV(CSE|ECE|EEE|CIV|ME|MECH)\d{4}$"
IRREGULARITY_REGEX_PATTERN = r"^IR0[1-5]$"

_INV_COMPILED = re.compile(INVIGILATOR_REGEX_PATTERN)
_IRR_COMPILED = re.compile(IRREGULARITY_REGEX_PATTERN)

IRR_NAMES = {
    "IR01": "Malpractice",
    "IR02": "Disturbance",
    "IR03": "Medical",
    "IR04": "Technical",
    "IR05": "Missing-Script"
}

def validate_invigilator_regex(identifier: str) -> Dict[str, Any]:
    """
    Validates Invigilator ID using re.fullmatch().
    Measures duration in nanoseconds using time.perf_counter_ns().
    """
    t0 = time.perf_counter_ns()
    
    if not isinstance(identifier, str) or len(identifier) == 0:
        duration_ns = time.perf_counter_ns() - t0
        return {
            "input": identifier,
            "is_valid": False,
            "matched": False,
            "pattern": INVIGILATOR_REGEX_PATTERN,
            "department": None,
            "execution_time_ns": duration_ns,
            "reason": "Input cannot be empty or non-string."
        }

    match = _INV_COMPILED.fullmatch(identifier)
    duration_ns = time.perf_counter_ns() - t0

    is_valid = match is not None
    department = match.group(1) if match else None

    reason = f"Accepted: Matches pattern {INVIGILATOR_REGEX_PATTERN}." if is_valid else \
             f"Rejected: Input '{identifier}' does not conform to regex pattern."

    return {
        "input": identifier,
        "is_valid": is_valid,
        "matched": is_valid,
        "pattern": INVIGILATOR_REGEX_PATTERN,
        "department": department,
        "execution_time_ns": duration_ns,
        "reason": reason
    }


def validate_irregularity_regex(code: str) -> Dict[str, Any]:
    """
    Validates Irregularity Code using re.fullmatch().
    Measures duration in nanoseconds using time.perf_counter_ns().
    """
    t0 = time.perf_counter_ns()

    if not isinstance(code, str) or len(code) == 0:
        duration_ns = time.perf_counter_ns() - t0
        return {
            "input": code,
            "is_valid": False,
            "matched": False,
            "pattern": IRREGULARITY_REGEX_PATTERN,
            "category": None,
            "execution_time_ns": duration_ns,
            "reason": "Input cannot be empty or non-string."
        }

    match = _IRR_COMPILED.fullmatch(code)
    duration_ns = time.perf_counter_ns() - t0

    is_valid = match is not None
    category = IRR_NAMES.get(code) if is_valid else None

    reason = f"Accepted: Matches pattern {IRREGULARITY_REGEX_PATTERN} ({category})." if is_valid else \
             f"Rejected: Code '{code}' does not match pattern {IRREGULARITY_REGEX_PATTERN}."

    return {
        "input": code,
        "is_valid": is_valid,
        "matched": is_valid,
        "pattern": IRREGULARITY_REGEX_PATTERN,
        "category": category,
        "execution_time_ns": duration_ns,
        "reason": reason
    }
