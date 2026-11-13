"""
Computer Networks (CN) Module
Exports IP addressing, subnet calculation, routing table, and LPM engines.
"""

from networking.ip_addressing import (
    parse_ipv4_address,
    parse_ipv4_network,
    get_authority_destination_ip,
    validate_source_ip_for_zone,
    EXAMINATION_ZONES,
    AUTHORITY_SERVICE_IPS
)
from networking.subnet_calculator import SubnetCalculator
from networking.network_routing import (
    RouteEntry,
    load_active_routes,
    lookup_route
)
from networking.routing_service import process_network_packet_routing

__all__ = [
    "parse_ipv4_address",
    "parse_ipv4_network",
    "get_authority_destination_ip",
    "validate_source_ip_for_zone",
    "EXAMINATION_ZONES",
    "AUTHORITY_SERVICE_IPS",
    "SubnetCalculator",
    "RouteEntry",
    "load_active_routes",
    "lookup_route",
    "process_network_packet_routing"
]
