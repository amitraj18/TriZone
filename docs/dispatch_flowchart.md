# Intelligent Dispatch & Deterministic Priority Queue Flowchart

The IRIS Dispatch Engine guarantees deterministic, non-starving allocation using capacity bounds, workload balancing, and a 4-tier deterministic priority queue.

```mermaid
flowchart TD
    Start(["Dispatch Trigger (New Incident or Dequeue Event)"]) --> QueryRules["Lookup Responsible Authority Role"]
    QueryRules --> CheckPrimary["Query Online Primary Handlers with current_load < capacity"]
    
    CheckPrimary -- Handlers Available --> Balancer["Workload Balancer: Select Handler with min(current_load)"]
    Balancer --> IncrementLoad["Increment Handler current_load by +1"]
    IncrementLoad --> CreateAssign["Insert PRIMARY Assignment (Status: ASSIGNED)"]
    CreateAssign --> LogAudit["Log Dispatch Audit in dispatch_logs"]
    
    CheckPrimary -- All Primaries Full/Offline --> CheckBackupRule{"Escalation Rule Configured?"}
    
    CheckBackupRule -- Yes --> QueryBackup["Query Online Backup Handlers with current_load < capacity"]
    QueryBackup -- Backup Available --> BalancerBackup["Select Backup Handler with min(current_load)"]
    BalancerBackup --> IncBackupLoad["Increment Backup Handler current_load"]
    IncBackupLoad --> CreateEscalation["Insert BACKUP Assignment (Status: ESCALATED)"]
    CreateEscalation --> LogAudit
    
    CheckBackupRule -- No / Backup Full --> Enqueue["Deterministic Priority Queue (Status: QUEUED)"]
    QueryBackup -- All Backups Full/Offline --> Enqueue
    
    Enqueue --> PQueueLogic["PQ Priority Order:<br/>1. CRITICAL (Weight 4)<br/>2. HIGH (Weight 3)<br/>3. MEDIUM (Weight 2)<br/>4. LOW (Weight 1)<br/>Tie-Breaker 1: created_at ASC (FIFO)<br/>Tie-Breaker 2: report id ASC (Deterministic)"]
    
    PQueueLogic --> LogAudit
    LogAudit --> Finish(["Dispatch Step Complete"])

    subgraph DequeueTrigger ["Dynamic Dequeueing Event"]
        Resolution["Report Status Updated to RESOLVED"] --> DecrLoad["Decrement Handler current_load by -1"]
        CapacityUp["Handler Availability set to ONLINE or Capacity Increased"] --> PollPQ["Poll Highest-Priority Waiting Report in Queue"]
        DecrLoad --> PollPQ
        PollPQ -- Incident Waiting --> Balancer
        PollPQ -- Queue Empty --> DoneIdle(["No Pending Queue Work"])
    end
```

