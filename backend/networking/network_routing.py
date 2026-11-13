"""
Network Routing Table & Longest Prefix Matching (LPM) Engine
Computer Networks (CN) Foundation
------------------------------------------------------------
Implements Layer-3 forwarding simulation using Longest Prefix Matching (LPM)
with lowest-metric tie-breaking, default-route fallback, and candidate path tracing.
"""

import ipaddress
from typing import Dict, Any, List, Optional
from database.connection import db_session

class RouteEntry:
    def __init__(
        self,
        id: int,
        department: str,
        destination_network: str,
        subnet_mask: str,
        prefix_length: int,
        next_hop: str,
        interface: str,
        metric: int,
        route_type: str = "STATIC",
        is_active: bool = True
    ):
        self.id = id
        self.department = department
        self.destination_network = destination_network
        self.subnet_mask = subnet_mask
        self.prefix_length = prefix_length
        self.next_hop = next_hop
        self.interface = interface
        self.metric = metric
        self.route_type = route_type
        self.is_active = is_active
        self.network_obj = ipaddress.ip_network(destination_network, strict=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "department": self.department,
            "destination_network": self.destination_network,
            "subnet_mask": self.subnet_mask,
            "prefix_length": self.prefix_length,
            "next_hop": self.next_hop,
            "interface": self.interface,
            "metric": self.metric,
            "route_type": self.route_type,
            "is_active": self.is_active
        }


def load_active_routes(custom_routes: Optional[List[Dict[str, Any]]] = None) -> List[RouteEntry]:
    """Loads active routing table entries from SQLite network_routes or custom input."""
    routes: List[RouteEntry] = []
    
    if custom_routes is not None:
        raw_list = custom_routes
    else:
        try:
            with db_session() as conn:
                cur = conn.execute("""
                    SELECT id, department, destination_network, subnet_mask, prefix_length, 
                           next_hop, interface, metric, is_active
                    FROM network_routes
                    WHERE is_active = 1
                """)
                raw_list = [dict(row) for row in cur.fetchall()]
        except Exception:
            raw_list = []

    for r in raw_list:
        try:
            entry = RouteEntry(
                id=r.get("id", 0),
                department=r.get("department", "General"),
                destination_network=r["destination_network"],
                subnet_mask=r.get("subnet_mask", "255.255.255.0"),
                prefix_length=int(r.get("prefix_length", 24)),
                next_hop=r["next_hop"],
                interface=r["interface"],
                metric=int(r.get("metric", 10)),
                route_type=r.get("route_type", "STATIC"),
                is_active=bool(r.get("is_active", 1))
            )
            routes.append(entry)
        except Exception:
            continue

    return routes


def lookup_route(
    destination_ip_str: str, 
    custom_routes: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Executes Longest Prefix Matching (LPM) algorithm for a destination IPv4.
    
    Algorithm:
    1. Parse and validate destination IP.
    2. Enumerate all active routing table entries.
    3. Filter all routes whose destination_network encompasses destination_ip.
    4. Primary sort key: prefix_length DESC (Longest Prefix Match).
    5. Tie-breaker sort key: metric ASC (Lowest Administrative Distance / Cost).
    6. Return most specific route, next-hop IP, outgoing interface, and full candidate list.
    7. If only 0.0.0.0/0 matches, flag default_fallback.
    8. If no routes match, return reachable=False.
    """
    if not destination_ip_str or not isinstance(destination_ip_str, str):
        return {
            "success": False,
            "destination_ip": destination_ip_str,
            "reachable": False,
            "error": "Destination IP string is required."
        }

    try:
        dest_ip = ipaddress.ip_address(destination_ip_str.strip())
        if not isinstance(dest_ip, ipaddress.IPv4Address):
            return {
                "success": False,
                "destination_ip": destination_ip_str,
                "reachable": False,
                "error": "Only IPv4 destination addresses are supported."
            }
    except ValueError as e:
        return {
            "success": False,
            "destination_ip": destination_ip_str,
            "reachable": False,
            "error": f"Invalid IPv4 address format '{destination_ip_str}': {str(e)}"
        }

    routes = load_active_routes(custom_routes)
    if not routes:
        return {
            "success": False,
            "destination_ip": str(dest_ip),
            "reachable": False,
            "error": "Routing table is empty or inaccessible."
        }

    # Step 2: Find all matching routes
    candidates: List[RouteEntry] = []
    for r in routes:
        if dest_ip in r.network_obj:
            candidates.append(r)

    if not candidates:
        return {
            "success": True,
            "destination_ip": str(dest_ip),
            "reachable": False,
            "matched_route": None,
            "candidates_count": 0,
            "error": f"Network unreachable: No route to host {dest_ip} in routing table."
        }

    # Step 3 & 4: Sort by prefix_length DESC, then metric ASC (tie-breaker)
    candidates.sort(key=lambda r: (-r.prefix_length, r.metric, r.id))

    best_match = candidates[0]
    is_default = (best_match.prefix_length == 0)

    # Candidate evaluation trace for transparency
    candidates_trace = []
    for rank, cand in enumerate(candidates, start=1):
        candidates_trace.append({
            "rank": rank,
            "network": cand.destination_network,
            "prefix_length": cand.prefix_length,
            "metric": cand.metric,
            "next_hop": cand.next_hop,
            "interface": cand.interface,
            "selected": (rank == 1)
        })

    return {
        "success": True,
        "destination_ip": str(dest_ip),
        "reachable": True,
        "is_default_fallback": is_default,
        "matched_route": best_match.to_dict(),
        "next_hop": best_match.next_hop,
        "interface": best_match.interface,
        "metric": best_match.metric,
        "prefix_length": best_match.prefix_length,
        "department": best_match.department,
        "candidates_evaluated": candidates_trace,
        "explanation": (
            f"Forwarding to {dest_ip} via next-hop {best_match.next_hop} on {best_match.interface} "
            f"using Longest Prefix Match /{best_match.prefix_length} (Metric: {best_match.metric})."
        )
    }

