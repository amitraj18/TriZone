"""
IP Addressing & Examination Zone Mapping
Computer Networks (CN) Foundation
----------------------------------------
Implements IP address validation, examination zone bindings, and statutory
authority service IP configurations using standard Python ipaddress library.
"""

import ipaddress
from typing import Dict, Any, Optional

# Configurable Examination Zone to Subnet bindings
EXAMINATION_ZONES: Dict[str, Dict[str, Any]] = {
    "HALL-401": {
        "zone_name": "CSE Main Examination Hall 401",
        "department": "CSE",
        "subnet": "192.168.10.0/24"
    },
    "HALL-302": {
        "zone_name": "CSE Upper Floor Hall 302",
        "department": "CSE",
        "subnet": "192.168.10.0/24"
    },
    "LAB-3": {
        "zone_name": "Specialized High-Performance Computing Lab 3",
        "department": "Specialized Lab",
        "subnet": "192.168.10.128/25"  # Overlapping /25 subnet inside 192.168.10.0/24
    },
    "HALL-204": {
        "zone_name": "ECE Examination Hall 204",
        "department": "ECE",
        "subnet": "192.168.20.0/24"
    },
    "HALL-102": {
        "zone_name": "EEE Ground Floor Hall 102",
        "department": "EEE",
        "subnet": "192.168.30.0/24"
    },
    "ADMIN-01": {
        "zone_name": "Examination Control Division",
        "department": "Administration",
        "subnet": "192.168.40.0/24"
    }
}

# Configurable Destination Service IPs for Examination Authorities
AUTHORITY_SERVICE_IPS: Dict[str, str] = {
    "Chief Superintendent": "192.168.40.10",
    "Centre Superintendent": "192.168.40.20",
    "Controller of Examinations": "192.168.40.30",
    "Technical Support Lead": "192.168.40.40",
    "Campus Medical Officer": "192.168.40.50"
}


def parse_ipv4_address(ip_str: str) -> Optional[ipaddress.IPv4Address]:
    """Parses and validates an IPv4 string. Returns None if invalid."""
    if not ip_str or not isinstance(ip_str, str):
        return None
    try:
        addr = ipaddress.ip_address(ip_str.strip())
        if isinstance(addr, ipaddress.IPv4Address):
            return addr
        return None
    except ValueError:
        return None


def parse_ipv4_network(net_str: str) -> Optional[ipaddress.IPv4Network]:
    """Parses and validates an IPv4 network CIDR string."""
    if not net_str or not isinstance(net_str, str):
        return None
    try:
        return ipaddress.ip_network(net_str.strip(), strict=False)
    except ValueError:
        return None


def get_authority_destination_ip(authority_role: str) -> str:
    """Returns the simulated destination IP address for an authority service."""
    return AUTHORITY_SERVICE_IPS.get(authority_role, "192.168.40.10")


def validate_source_ip_for_zone(source_ip_str: str, hall_id: str) -> Dict[str, Any]:
    """
    Validates that the invigilator's terminal source IP belongs to the subnet
    configured for the specified examination hall/zone.
    """
    ip_obj = parse_ipv4_address(source_ip_str)
    if not ip_obj:
        return {
            "is_valid": False,
            "source_ip": source_ip_str,
            "hall_id": hall_id,
            "error": f"Malformed or invalid IPv4 address '{source_ip_str}'."
        }

    zone_info = EXAMINATION_ZONES.get(hall_id.upper().strip()) if hall_id else None

    if not zone_info:
        # Fallback: Check if IP matches any known zone
        matched_zone = None
        for z_id, z_data in EXAMINATION_ZONES.items():
            net = parse_ipv4_network(z_data["subnet"])
            if net and ip_obj in net:
                matched_zone = (z_id, z_data)
                break

        return {
            "is_valid": True,
            "source_ip": str(ip_obj),
            "hall_id": hall_id,
            "zone_name": matched_zone[1]["zone_name"] if matched_zone else "General Campus Terminal",
            "subnet": matched_zone[1]["subnet"] if matched_zone else "Dynamic/DHCP",
            "warning": f"Hall ID '{hall_id}' not in strict registry; permitted via campus gateway."
        }

    expected_net = parse_ipv4_network(zone_info["subnet"])
    is_in_zone = (expected_net is not None) and (ip_obj in expected_net)

    if not is_in_zone:
        return {
            "is_valid": False,
            "source_ip": str(ip_obj),
            "hall_id": hall_id,
            "expected_subnet": zone_info["subnet"],
            "zone_name": zone_info["zone_name"],
            "error": (
                f"Source IP {ip_obj} does not belong to examination zone '{hall_id}' "
                f"assigned subnet {zone_info['subnet']} ({zone_info['zone_name']})."
            )
        }

    return {
        "is_valid": True,
        "source_ip": str(ip_obj),
        "hall_id": hall_id,
        "subnet": zone_info["subnet"],
        "zone_name": zone_info["zone_name"],
        "department": zone_info["department"],
        "message": f"Source IP verified within subnet {zone_info['subnet']}."
    }

