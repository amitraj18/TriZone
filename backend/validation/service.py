"""
Validation Service Orchestrator
Cross-checks DFA & Regex and logs audit trails into SQLite validation_logs
"""

from typing import Dict, Any, Optional
from validation.dfa import InvigilatorDFA, IrregularityDFA
from validation.regex_validator import validate_invigilator_regex, validate_irregularity_regex
from database.connection import db_session

inv_dfa = InvigilatorDFA()
irr_dfa = IrregularityDFA()

def validate_invigilator_id(identifier: str, report_id: Optional[int] = None) -> Dict[str, Any]:
    raw_id = (identifier or "").strip().upper()
    dfa_res = inv_dfa.run(raw_id)
    regex_res = validate_invigilator_regex(raw_id)

    # Formal equivalence assertion
    is_equivalent = (dfa_res.is_valid == regex_res.is_valid)
    is_valid = dfa_res.is_valid and regex_res.is_valid

    failure_reason = "" if is_valid else (dfa_res.reason or "Regex mismatch")

    # Audit log in database if database is available
    try:
        with db_session() as conn:
            conn.execute("""
                INSERT INTO validation_logs 
                (report_id, entity_type, input_value, dfa_result, regex_result, is_valid, failure_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                report_id,
                "INVIGILATOR_ID",
                raw_id,
                1 if dfa_res.is_valid else 0,
                1 if regex_res.is_valid else 0,
                1 if is_valid else 0,
                failure_reason
            ))
    except Exception as e:
        # Non-blocking logging failure
        pass

    return {
        "entity": "INVIGILATOR_ID",
        "input": raw_id,
        "is_valid": is_valid,
        "is_equivalent": is_equivalent,
        "dfa": dfa_res.to_dict(),
        "regex": regex_res.to_dict(),
        "failure_reason": failure_reason
    }


def validate_irregularity_code(code: str, report_id: Optional[int] = None) -> Dict[str, Any]:
    raw_code = (code or "").strip().upper()
    dfa_res = irr_dfa.run(raw_code)
    regex_res = validate_irregularity_regex(raw_code)

    is_equivalent = (dfa_res.is_valid == regex_res.is_valid)
    is_valid = dfa_res.is_valid and regex_res.is_valid

    failure_reason = "" if is_valid else (dfa_res.reason or "Regex mismatch")

    try:
        with db_session() as conn:
            conn.execute("""
                INSERT INTO validation_logs 
                (report_id, entity_type, input_value, dfa_result, regex_result, is_valid, failure_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                report_id,
                "IRREGULARITY_CODE",
                raw_code,
                1 if dfa_res.is_valid else 0,
                1 if regex_res.is_valid else 0,
                1 if is_valid else 0,
                failure_reason
            ))
    except Exception as e:
        pass

    return {
        "entity": "IRREGULARITY_CODE",
        "input": raw_code,
        "is_valid": is_valid,
        "is_equivalent": is_equivalent,
        "dfa": dfa_res.to_dict(),
        "regex": regex_res.to_dict(),
        "failure_reason": failure_reason
    }

