import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from networking.subnet_calculator import SubnetCalculator
from networking.ip_addressing import validate_source_ip_for_zone, parse_ipv4_address, get_authority_destination_ip
from networking.network_routing import lookup_route, RouteEntry
from networking.routing_service import process_network_packet_routing
from database.seed_data import init_db

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    test_db = str(tmp_path / "test_net.db")
    os.environ["DATABASE"] = test_db
    init_db(db_path=test_db, force=True)

class TestSubnetCalculator:
    def test_class_c_subnet(self):
        res = SubnetCalculator.calculate("192.168.10.0/24")
        assert res["success"] is True
        assert res["network_address"] == "192.168.10.0"
        assert res["broadcast_address"] == "192.168.10.255"
        assert res["netmask"] == "255.255.255.0"
        assert res["wildcard_mask"] == "0.0.0.255"
        assert res["usable_hosts"] == 254
        assert res["first_usable_host"] == "192.168.10.1"
        assert res["last_usable_host"] == "192.168.10.254"

    def test_specialized_lab_subnet_overlap(self):
        # Specialized lab /25 is a subset of /24
        overlap = SubnetCalculator.check_subnet_overlap("192.168.10.128/25", "192.168.10.0/24")
        assert overlap["overlaps"] is True
        assert "subnet of" in overlap["relation"]

    def test_invalid_cidr(self):
        res = SubnetCalculator.calculate("999.999.999.999/33")
        assert res["success"] is False


class TestSourceIPValidation:
    def test_valid_cse_terminal_ip(self):
        res = validate_source_ip_for_zone("192.168.10.45", "HALL-401")
        assert res["is_valid"] is True
        assert res["subnet"] == "192.168.10.0/24"

    def test_valid_specialized_lab_terminal_ip(self):
        # 192.168.10.134 is inside 192.168.10.128/25
        res = validate_source_ip_for_zone("192.168.10.134", "LAB-3")
        assert res["is_valid"] is True
        assert res["subnet"] == "192.168.10.128/25"

    def test_source_ip_zone_mismatch(self):
        # 192.168.10.45 is in /24 but NOT inside 192.168.10.128/25
        res = validate_source_ip_for_zone("192.168.10.45", "LAB-3")
        assert res["is_valid"] is False
        assert "does not belong" in res["error"]


class TestLongestPrefixMatching:
    def test_lpm_overlapping_selection(self):
        """
        Critical requirement:
        For address 192.168.10.134, it matches both 192.168.10.0/24 (CSE)
        and 192.168.10.128/25 (Specialized Lab).
        LPM MUST choose /25 because 25 > 24!
        """
        res = lookup_route("192.168.10.134")
        assert res["reachable"] is True
        assert res["prefix_length"] == 25
        assert res["matched_route"]["destination_network"] == "192.168.10.128/25"
        assert res["interface"] == "eth0.100"
        assert res["next_hop"] == "192.168.10.254"

    def test_lpm_non_overlapping_cse(self):
        # 192.168.10.45 is in /24 but outside /25. Must choose /24.
        res = lookup_route("192.168.10.45")
        assert res["reachable"] is True
        assert res["prefix_length"] == 24
        assert res["matched_route"]["destination_network"] == "192.168.10.0/24"
        assert res["interface"] == "eth0"
        assert res["next_hop"] == "192.168.10.1"

    def test_lpm_ece_route(self):
        res = lookup_route("192.168.20.15")
        assert res["reachable"] is True
        assert res["matched_route"]["destination_network"] == "192.168.20.0/24"
        assert res["interface"] == "eth1"

    def test_lpm_admin_route(self):
        res = lookup_route("192.168.40.10")
        assert res["reachable"] is True
        assert res["matched_route"]["destination_network"] == "192.168.40.0/24"
        assert res["interface"] == "vlan40"

    def test_default_route_fallback(self):
        # External or campus backbone address e.g. 10.5.0.1
        res = lookup_route("10.5.0.1")
        assert res["reachable"] is True
        assert res["prefix_length"] == 0
        assert res["matched_route"]["destination_network"] == "0.0.0.0/0"
        assert res["is_default_fallback"] is True

    def test_lowest_metric_tie_breaker(self):
        custom_routes = [
            {
                "id": 1,
                "department": "Route A",
                "destination_network": "172.16.0.0/16",
                "subnet_mask": "255.255.0.0",
                "prefix_length": 16,
                "next_hop": "172.16.0.1",
                "interface": "eth_high_cost",
                "metric": 50,
                "is_active": 1
            },
            {
                "id": 2,
                "department": "Route B",
                "destination_network": "172.16.0.0/16",
                "subnet_mask": "255.255.0.0",
                "prefix_length": 16,
                "next_hop": "172.16.0.254",
                "interface": "eth_low_cost",
                "metric": 10,
                "is_active": 1
            }
        ]
        res = lookup_route("172.16.5.5", custom_routes=custom_routes)
        assert res["reachable"] is True
        assert res["metric"] == 10
        assert res["interface"] == "eth_low_cost"

    def test_unreachable_when_no_default_route(self):
        isolated_routes = [
            {
                "id": 1,
                "department": "Isolated",
                "destination_network": "192.168.1.0/24",
                "subnet_mask": "255.255.255.0",
                "prefix_length": 24,
                "next_hop": "192.168.1.1",
                "interface": "eth0",
                "metric": 10,
                "is_active": 1
            }
        ]
        res = lookup_route("8.8.8.8", custom_routes=isolated_routes)
        assert res["reachable"] is False
        assert "unreachable" in res["error"].lower()

