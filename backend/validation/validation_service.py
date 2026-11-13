"""
Validation Service Orchestrator
Cross-checks DFA and Regex engines, asserts formal language equivalence,
and persists complete verification audit logs into SQLite validation_logs table.
"""

from typing import Dict, Any, Optional
from validation.invigilator_dfa import InvigilatorDFA
from validation.irregularity_dfa import IrregularityDFA
from validation.regex_validator import validate_invigilator_regex, validate_irregularity_regex
from database.connection import db_session

_inv_dfa = InvigilatorDFA()
_irr_dfa = IrregularityDFA()

def _ensure_validation_logs_columns(conn):
    """Safe schema check: adds timing and agreement columns if not present."""
    cur = conn.execute("PRAGMA table_info(validation_logs)")
    columns = [row[1] for row in cur.fetchall()]
    if "dfa_time_ns" not in columns:
        conn.execute("ALTER TABLE validation_logs ADD COLUMN dfa_time_ns INTEGER")
    if "regex_time_ns" not in columns:
        conn.execute("ALTER TABLE validation_logs ADD COLUMN regex_time_ns INTEGER")
    if "agreement" not in columns:
        conn.execute("ALTER TABLE validation_logs ADD COLUMN agreement INTEGER DEFAULT 1")

def validate_invigilator_id(identifier: str, report_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Validates Invigilator ID through both DFA and Regex engines.
    Asserts formal agreement and persists execution metrics in SQLite.
    """
    raw_id = (identifier or "").strip()
    
    # 1. Run DFA
    dfa_res = _inv_dfa.validate(raw_id)
    # 2. Run Regex
    regex_res = validate_invigilator_regex(raw_id)

    # 3. Check agreement
    agreement = (dfa_res["is_valid"] == regex_res["is_valid"])
    engine_error = not agreement

    if engine_error:
        failure_reason = "CRITICAL: Validation engine conflict! DFA and Regex disagree on input acceptance."
        overall_valid = False
    elif not dfa_res["is_valid"]:
        failure_reason = dfa_res["reason"]
        overall_valid = False
    else:
        failure_reason = ""
        overall_valid = True

    # 4. Persist to validation_logs
    try:
        with db_session() as conn:
            _ensure_validation_logs_columns(conn)
            conn.execute("""
                INSERT INTO validation_logs 
                (report_id, entity_type, input_value, dfa_result, regex_result, is_valid, failure_reason, dfa_time_ns, regex_time_ns, agreement)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report_id,
                "INVIGILATOR_ID",
                raw_id,
                1 if dfa_res["is_valid"] else 0,
                1 if regex_res["is_valid"] else 0,
                1 if overall_valid else 0,
                failure_reason,
                dfa_res["execution_time_ns"],
                regex_res["execution_time_ns"],
                1 if agreement else 0
            ))
    except Exception as e:
        # Logging error should not crash validation service
        pass

    return {
        "entity": "INVIGILATOR_ID",
        "input": raw_id,
        "is_valid": overall_valid,
        "agreement": agreement,
        "engine_error": engine_error,
        "failure_reason": failure_reason,
        "dfa": dfa_res,
        "regex": regex_res
    }


def validate_irregularity_code(code: str, report_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Validates Irregularity Code through both DFA and Regex engines.
    Asserts formal agreement and persists execution metrics in SQLite.
    """
    raw_code = (code or "").strip()

    dfa_res = _irr_dfa.validate(raw_code)
    regex_res = validate_irregularity_regex(raw_code)

    agreement = (dfa_res["is_valid"] == regex_res["is_valid"])
    engine_error = not agreement

    if engine_error:
        failure_reason = "CRITICAL: Validation engine conflict! DFA and Regex disagree on code acceptance."
        overall_valid = False
    elif not dfa_res["is_valid"]:
        failure_reason = dfa_res["reason"]
        overall_valid = False
    else:
        failure_reason = ""
        overall_valid = True

    category_name = dfa_res.get("category") or regex_res.get("category")

    try:
        with db_session() as conn:
            _ensure_validation_logs_columns(conn)
            conn.execute("""
                INSERT INTO validation_logs 
                (report_id, entity_type, input_value, dfa_result, regex_result, is_valid, failure_reason, dfa_time_ns, regex_time_ns, agreement)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report_id,
                "IRREGULARITY_CODE",
                raw_code,
                1 if dfa_res["is_valid"] else 0,
                1 if regex_res["is_valid"] else 0,
                1 if overall_valid else 0,
                failure_reason,
                dfa_res["execution_time_ns"],
                regex_res["execution_time_ns"],
                1 if agreement else 0
            ))
    except Exception as e:
        pass

    return {
        "entity": "IRREGULARITY_CODE",
        "input": raw_code,
        "is_valid": overall_valid,
        "category": category_name,
        "agreement": agreement,
        "engine_error": engine_error,
        "failure_reason": failure_reason,
        "dfa": dfa_res,
        "regex": regex_res
    }


def validate_report_identifiers(invigilator_id: str, irregularity_code: str, report_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Validates both Invigilator ID and Irregularity Code.
    Returns composite result with detailed metrics and overall validity.
    """
    inv_result = validate_invigilator_id(invigilator_id, report_id)
    irr_result = validate_irregularity_code(irregularity_code, report_id)

    is_valid = inv_result["is_valid"] and irr_result["is_valid"]
    engine_error = inv_result["engine_error"] or irr_result["engine_error"]

    errors = []
    if not inv_result["is_valid"]:
        errors.append(f"Invigilator ID Error: {inv_result['failure_reason']}")
    if not irr_result["is_valid"]:
        errors.append(f"Irregularity Code Error: {irr_result['failure_reason']}")

    return {
        "is_valid": is_valid,
        "engine_error": engine_error,
        "errors": errors,
        "invigilator": inv_result,
        "irregularity": irr_result
    }

