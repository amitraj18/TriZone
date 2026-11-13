"""
Subnet Calculator
Computer Networks (CN) Foundation
---------------------------------
Performs deterministic CIDR calculations, host-range evaluations,
and overlapping subnet detection using Python standard ipaddress library.
"""

import ipaddress
from typing import Dict, Any, Optional, Tuple

class SubnetCalculator:
    @staticmethod
    def calculate(cidr_string: str) -> Dict[str, Any]:
        """
        Calculates all Layer-3 subnet parameters for a given CIDR notation.
        """
        try:
            net = ipaddress.ip_network(cidr_string.strip(), strict=False)
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid CIDR notation '{cidr_string}': {str(e)}"
            }

        # Calculate usable host range
        num_addresses = net.num_addresses
        if net.prefixlen >= 31:
            # Point-to-point /31 or single host /32
            usable_hosts = num_addresses
            first_host = str(net.network_address)
            last_host = str(net.broadcast_address)
        else:
            usable_hosts = max(0, num_addresses - 2)
            first_host = str(net.network_address + 1)
            last_host = str(net.broadcast_address - 1)

        # Wildcard mask = inverted netmask
        netmask_int = int(net.netmask)
        wildcard_int = 0xFFFFFFFF ^ netmask_int
        wildcard_mask = str(ipaddress.IPv4Address(wildcard_int))

        return {
            "success": True,
            "cidr": str(net),
            "network_address": str(net.network_address),
            "broadcast_address": str(net.broadcast_address),
            "netmask": str(net.netmask),
            "wildcard_mask": wildcard_mask,
            "prefix_length": net.prefixlen,
            "total_addresses": num_addresses,
            "total_hosts": num_addresses,
            "usable_hosts": usable_hosts,
            "first_usable_host": first_host,
            "last_usable_host": last_host,
            "is_private": net.is_private,
            "is_loopback": net.is_loopback
        }

    @staticmethod
    def is_ip_in_subnet(ip_str: str, subnet_cidr: str) -> bool:
        """Determines if a given IP address falls within a subnet CIDR."""
        try:
            ip_obj = ipaddress.ip_address(ip_str.strip())
            net_obj = ipaddress.ip_network(subnet_cidr.strip(), strict=False)
            return ip_obj in net_obj
        except ValueError:
            return False

    @staticmethod
    def check_subnet_overlap(subnet_a: str, subnet_b: str) -> Dict[str, Any]:
        """
        Detects if subnet_a and subnet_b overlap in IP address space.
        Identifies subset / superset relationships (e.g. /25 inside /24).
        """
        try:
            net_a = ipaddress.ip_network(subnet_a.strip(), strict=False)
            net_b = ipaddress.ip_network(subnet_b.strip(), strict=False)
        except ValueError as e:
            return {"overlaps": False, "error": str(e)}

        overlaps = net_a.overlaps(net_b)
        relation = "DISJOINT"
        if overlaps:
            if net_a == net_b:
                relation = "IDENTICAL"
            elif net_a.subnet_of(net_b):
                relation = f"{net_a} is a subnet of {net_b}"
            elif net_b.subnet_of(net_a):
                relation = f"{net_b} is a subnet of {net_a}"
            else:
                relation = "PARTIAL_OVERLAP"

        return {
            "overlaps": overlaps,
            "relation": relation,
            "net_a": str(net_a),
            "net_b": str(net_b)
        }

