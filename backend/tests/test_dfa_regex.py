import pytest
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from validation.invigilator_dfa import InvigilatorDFA
from validation.irregularity_dfa import IrregularityDFA
from validation.regex_validator import validate_invigilator_regex, validate_irregularity_regex
from validation.validation_service import validate_report_identifiers, validate_invigilator_id, validate_irregularity_code
from database.seed_data import init_db

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    test_db = str(tmp_path / "test_val.db")
    os.environ["DATABASE"] = test_db
    init_db(db_path=test_db, force=True)

class TestInvigilatorDFA:
    def setup_method(self):
        self.dfa = InvigilatorDFA()

    def test_valid_departments(self):
        valid_ids = [
            "INVCSE0001", "INVCSE9999",
            "INVECE0001", "INVEEE0001",
            "INVCIV0001", "INVME0001", "INVMECH0001"
        ]
        for vid in valid_ids:
            res = self.dfa.validate(vid)
            assert res["is_valid"] is True, f"Failed on valid id: {vid}"
            assert res["accepted"] is True
            assert res["final_state"] == "q_accept"
            assert len(res["trace"]) == len(vid)

    def test_invalid_departments(self):
        invalid_ids = [
            "INVAERO0001", "INVBIO0001", "INVXYZ0001", "INVMATH0001"
        ]
        for iid in invalid_ids:
            res = self.dfa.validate(iid)
            assert res["is_valid"] is False, f"Should reject invalid dept: {iid}"
            assert res["accepted"] is False

    def test_invalid_digits_and_length(self):
        invalid_cases = [
            "INVCSE001",       # 3 digits (too few)
            "INVCSE00001",     # 5 digits (too many)
            "INVCSEABCD",      # non-digits
            "invcse0001",      # lowercase
            "INVCSE000!",      # special character
            "",                # empty
            "   ",             # whitespace
            "INVCSE",          # missing digits entirely
            "0001",            # missing prefix
        ]
        for case in invalid_cases:
            res = self.dfa.validate(case)
            assert res["is_valid"] is False, f"Should reject: {case}"

    def test_character_by_character_trace(self):
        res = self.dfa.validate("INVCSE0001")
        trace = res["trace"]
        assert len(trace) == 10
        # Step 1: I -> q1
        assert trace[0]["char"] == "I" and trace[0]["to_state"] == "q1"
        # Step 2: N -> q2
        assert trace[1]["char"] == "N" and trace[1]["to_state"] == "q2"
        # Step 3: V -> q3
        assert trace[2]["char"] == "V" and trace[2]["to_state"] == "q3"
        # Step 4: C -> q_c
        assert trace[3]["char"] == "C" and trace[3]["to_state"] == "q_c"
        # Final step -> q_accept
        assert trace[-1]["to_state"] == "q_accept"


class TestIrregularityDFA:
    def setup_method(self):
        self.dfa = IrregularityDFA()

    def test_valid_irregularity_codes(self):
        expected = {
            "IR01": "Malpractice",
            "IR02": "Disturbance",
            "IR03": "Medical",
            "IR04": "Technical",
            "IR05": "Missing-Script"
        }
        for code, category in expected.items():
            res = self.dfa.validate(code)
            assert res["is_valid"] is True, f"Failed on valid code {code}"
            assert res["accepted"] is True
            assert res["category"] == category
            assert len(res["trace"]) == 4

    def test_rejected_unsupported_codes(self):
        unsupported = [
            "IR06", "IR99", "IR00", "IR1", "IR001", "ABC01", "ir01", "IR055", ""
        ]
        for code in unsupported:
            res = self.dfa.validate(code)
            assert res["is_valid"] is False, f"Should reject {code}"
            assert res["accepted"] is False


class TestDFARegexEquivalence:
    def test_invigilator_agreement(self):
        test_inputs = [
            "INVCSE0001", "INVECE0001", "INVEEE0001", "INVCIV0001", "INVME0001", "INVMECH0001",
            "INVCSE001", "INVCSE00001", "INVAERO0001", "invcse0001", "ABC1234", "", "INVCSE12#4"
        ]
        for inp in test_inputs:
            service_res = validate_invigilator_id(inp)
            assert service_res["agreement"] is True, f"DFA and Regex disagreed on input '{inp}'"
            assert service_res["engine_error"] is False

    def test_irregularity_agreement(self):
        test_inputs = [
            "IR01", "IR02", "IR03", "IR04", "IR05",
            "IR06", "IR99", "IR1", "IR001", "ABC01", "ir01", ""
        ]
        for inp in test_inputs:
            service_res = validate_irregularity_code(inp)
            assert service_res["agreement"] is True, f"DFA and Regex disagreed on code '{inp}'"
            assert service_res["engine_error"] is False

    def test_nanosecond_timing_measurement(self):
        res = validate_report_identifiers("INVCSE0001", "IR01")
        assert res["is_valid"] is True
        assert res["invigilator"]["dfa"]["execution_time_ns"] > 0
        assert res["invigilator"]["regex"]["execution_time_ns"] > 0
        assert res["irregularity"]["dfa"]["execution_time_ns"] > 0
        assert res["irregularity"]["regex"]["execution_time_ns"] > 0

