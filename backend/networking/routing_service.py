"""
Routing Service Orchestrator
Computer Networks (CN) Foundation
---------------------------------
Orchestrates examination terminal source IP verification, authority service
destination resolution, and Longest Prefix Match (LPM) packet routing.
"""

from typing import Dict, Any, Optional
from networking.ip_addressing import (
    validate_source_ip_for_zone, 
    get_authority_destination_ip, 
    EXAMINATION_ZONES
)
from networking.network_routing import lookup_route
from networking.subnet_calculator import SubnetCalculator

def process_network_packet_routing(
    source_ip: str,
    hall_id: str,
    target_authority: str,
    custom_routes: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Simulates end-to-end network packet traversal:
    1. Validates invigilator source IP against physical examination hall zone.
    2. Resolves destination IP for target examination authority service.
    3. Performs deterministic Longest Prefix Matching (LPM) on routing table.
    4. Returns complete Layer-3 routing audit record.
    """
    # Step 1: Validate source IP against examination zone
    source_check = validate_source_ip_for_zone(source_ip, hall_id)
    if not source_check["is_valid"]:
        return {
            "success": False,
            "stage": "SOURCE_IP_VALIDATION",
            "source_verification": source_check,
            "error": source_check.get("error", "Source IP verification failed.")
        }

    # Step 2: Resolve destination IP for designated authority
    destination_ip = get_authority_destination_ip(target_authority)

    # Step 3: Run Longest Prefix Matching routing table lookup
    lpm_result = lookup_route(destination_ip, custom_routes)
    if not lpm_result.get("reachable", False):
        return {
            "success": False,
            "stage": "FORWARDING_LOOKUP",
            "source_verification": source_check,
            "destination_ip": destination_ip,
            "target_authority": target_authority,
            "routing_lookup": lpm_result,
            "error": lpm_result.get("error", f"Network unreachable: No route to authority service at {destination_ip}.")
        }

    return {
        "success": True,
        "source_ip": source_ip,
        "hall_id": hall_id,
        "source_zone": source_check.get("zone_name"),
        "source_subnet": source_check.get("subnet"),
        "destination_ip": destination_ip,
        "target_authority": target_authority,
        "routing_decision": {
            "matched_network": lpm_result["matched_route"]["destination_network"],
            "subnet_mask": lpm_result["matched_route"]["subnet_mask"],
            "prefix_length": lpm_result["prefix_length"],
            "next_hop": lpm_result["next_hop"],
            "interface": lpm_result["interface"],
            "metric": lpm_result["metric"],
            "department": lpm_result["department"],
            "is_default_fallback": lpm_result["is_default_fallback"],
            "candidates_evaluated": lpm_result["candidates_evaluated"],
            "explanation": lpm_result["explanation"]
        }
    }

