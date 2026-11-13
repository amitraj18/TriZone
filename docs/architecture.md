# System Architecture — IRIS

IRIS (Examination Hall Irregularity Reporting and Intelligent Dispatch System) is architected around a decoupled, three-tier model bridging **Theory of Computation (TOC)**, **Computer Networks (CN)**, and **Full-Stack Systems**.

```mermaid
graph TD
    subgraph ClientTier ["Presentation Layer (React + Tailwind CSS)"]
        UI_SUB["Report Submission Terminal"]
        UI_DFA["Interactive DFA Stepper"]
        UI_DASH["User Incident Dashboard"]
        UI_HND["Handler Workload & Queue"]
        UI_NET["Network LPM Simulator"]
        UI_RTE["Routing Matrix & Audit"]
        UI_ANL["Integrity Analytics (Recharts)"]
    end

    subgraph ApiGateway ["REST API Gateway (Flask Application Factory)"]
        AUTH["Auth & RBAC Service (HMAC-SHA256)"]
        NOTIF["In-App Notification Service"]
        EXPORT["RFC 4180 CSV Exporter"]
        DEMO["Demo State Resetter"]
    end

    subgraph CoreEngines ["Domain Processing Engines"]
        subgraph TOC ["1. Theory of Computation (TOC)"]
            DFA_INV["Invigilator DFA (19-State M_inv)"]
            DFA_IRR["Irregularity DFA (6-State M_irr)"]
            REGEX_INV["Regex Validator (^INV(CSE|ECE...)\d{4}$)"]
            REGEX_IRR["Regex Validator (^IR0[1-5]$)"]
            BENCH["Nanosecond Equivalence Benchmark"]
        end

        subgraph CN ["2. Computer Networks (CN)"]
            ZONE["Zone Binding & Source IP Verification"]
            CIDR["Subnet Calculator (ipaddress)"]
            LPM["Longest Prefix Match (LPM) Router"]
            METRIC["Metric & Subnet Depth Tie-Breaker"]
        end

        subgraph Dispatch ["3. Intelligent Dispatch & Queue"]
            PRIO["Priority Engine (Emergency Overrides)"]
            HND_MGR["Handler Availability & Capacity Balance"]
            ESCAL["Jurisdictional Backup Escalation"]
            PQ["Deterministic Priority Queue (Critical>High>Med>Low)"]
        end
    end

    subgraph DataStore ["Persistence Layer (SQLite Relational Database)"]
        DB_REPORTS[("reports")]
        DB_VAL_LOGS[("validation_logs")]
        DB_ASSIGN[("assignments")]
        DB_QUEUE[("dispatch_logs")]
        DB_ROUTES[("network_routes")]
        DB_RULES[("routing_rules & history")]
        DB_USERS[("users & notifications")]
    end

    ClientTier --> ApiGateway
    ApiGateway --> TOC
    ApiGateway --> CN
    ApiGateway --> Dispatch
    TOC --> DB_VAL_LOGS
    CN --> DB_ROUTES
    Dispatch --> DB_REPORTS
    Dispatch --> DB_ASSIGN
    Dispatch --> DB_QUEUE
    ApiGateway --> DB_USERS
    ApiGateway --> DB_RULES
```

