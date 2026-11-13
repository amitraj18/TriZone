"""
Theory of Computation (TOC) Validation Module
Exports DFA state machines, regular expression engines, and validation service.
"""

from validation.invigilator_dfa import InvigilatorDFA
from validation.irregularity_dfa import IrregularityDFA
from validation.regex_validator import (
    validate_invigilator_regex, 
    validate_irregularity_regex,
    INVIGILATOR_REGEX_PATTERN,
    IRREGULARITY_REGEX_PATTERN
)
from validation.validation_service import (
    validate_invigilator_id,
    validate_irregularity_code,
    validate_report_identifiers
)

__all__ = [
    "InvigilatorDFA",
    "IrregularityDFA",
    "validate_invigilator_regex",
    "validate_irregularity_regex",
    "validate_invigilator_id",
    "validate_irregularity_code",
    "validate_report_identifiers",
    "INVIGILATOR_REGEX_PATTERN",
    "IRREGULARITY_REGEX_PATTERN"
]
