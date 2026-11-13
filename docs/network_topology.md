# Computer Networks (CN) — Academic Layer-3 Topology & Routing

IRIS simulates an enterprise academic Layer-3 routed network environment.

```mermaid
flowchart TD
    subgraph CoreBackbone ["Campus Core Layer-3 Switch / Router (192.168.1.1)"]
        CORE_RTR["Core Gateway<br/>wan0: Default 0.0.0.0/0 (Metric 100)"]
    end

    subgraph DeptSubnets ["Academic Department Subnets (/24)"]
        CSE_SUB["CSE Department<br/>192.168.10.0/24<br/>Next-Hop: 192.168.10.1 (eth0, Metric 10)"]
        ECE_SUB["ECE Department<br/>192.168.20.0/24<br/>Next-Hop: 192.168.20.1 (eth1, Metric 10)"]
        EEE_SUB["EEE Department<br/>192.168.30.0/24<br/>Next-Hop: 192.168.30.1 (eth2, Metric 10)"]
        ADM_SUB["Administration & Exam Cell<br/>192.168.40.0/24<br/>Next-Hop: 192.168.40.1 (vlan40, Metric 5)"]
    end

    subgraph SpecialSubnet ["Overlapping High-Security Subnet (/25)"]
        CSE_LAB["CSE Advanced Research Lab<br/>192.168.10.128/25<br/>Next-Hop: 192.168.10.254 (eth0.100, Metric 5)"]
    end

    subgraph Endpoints ["Simulated Examination Terminal Endpoints"]
        H401["Hall 401 Terminal<br/>192.168.10.45"]
        L3["Lab 3 Terminal<br/>192.168.10.134"]
        H204["Hall 204 Terminal<br/>192.168.20.12"]
        H102["Hall 102 Terminal<br/>192.168.30.8"]
        EXAM_SRV["Chief Supt Server<br/>192.168.40.10"]
    end

    CORE_RTR --- CSE_SUB
    CORE_RTR --- ECE_SUB
    CORE_RTR --- EEE_SUB
    CORE_RTR --- ADM_SUB
    CSE_SUB -.->|"Longest Prefix Match (/25 over /24)"| CSE_LAB

    H401 --> CSE_SUB
    L3 --> CSE_LAB
    H204 --> ECE_SUB
    H102 --> EEE_SUB
    EXAM_SRV --> ADM_SUB
```

---

## Longest Prefix Matching (LPM) Example
When terminal `192.168.10.134` sends an incident packet:
1. `192.168.10.134` matches `192.168.10.0/24` (Prefix length 24).
2. `192.168.10.134` also matches `192.168.10.128/25` (Prefix length 25).
3. **LPM Rule**: Prefix length $25 > 24$.
4. **Resolution**: Packet is routed via interface `eth0.100` to Next-Hop `192.168.10.254` (Metric 5).

