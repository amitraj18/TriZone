"""
Priority Manager
Incident Priority Determination & Emergency Override Engine
------------------------------------------------------------
Implements default category priorities, emergency critical escalation,
and numerical weights for deterministic queue ordering.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Default priority matrix per standard examination protocol
DEFAULT_PRIORITIES = {
    "IR01": "HIGH",       # Malpractice
    "IR02": "MEDIUM",     # Disturbance
    "IR03": "CRITICAL",   # Medical Emergency
    "IR04": "MEDIUM",     # Technical Glitch
    "IR05": "HIGH"        # Missing-Script
}

# Numerical weights for deterministic priority queue ordering
PRIORITY_WEIGHTS = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}

class PriorityManager:
    @staticmethod
    def get_priority_weight(priority: str) -> int:
        """Returns integer weight for queue sorting (CRITICAL=4, HIGH=3, MEDIUM=2, LOW=1)."""
        return PRIORITY_WEIGHTS.get((priority or "").upper().strip(), 1)

    @staticmethod
    def determine_priority(
        irregularity_code: str, 
        is_emergency: bool = False,
        override_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines the effective incident priority:
        1. Reads default priority for irregularity code.
        2. Applies Critical override if emergency flag is present.
        3. Preserves original category, priority, override reason, and timestamp.
        """
        code = (irregularity_code or "").upper().strip()
        default_prio = DEFAULT_PRIORITIES.get(code, "MEDIUM")

        if is_emergency and default_prio != "CRITICAL":
            now_iso = datetime.now(timezone.utc).isoformat()
            effective_prio = "CRITICAL"
            reason = override_reason or "Emergency flag active: elevated to CRITICAL priority override."
            is_overridden = True
        else:
            now_iso = None
            effective_prio = default_prio
            reason = None
            is_overridden = False

        return {
            "irregularity_code": code,
            "default_priority": default_prio,
            "effective_priority": effective_prio,
            "is_overridden": is_overridden,
            "override_reason": reason,
            "override_timestamp": now_iso,
            "priority_weight": PriorityManager.get_priority_weight(effective_prio)
        }

