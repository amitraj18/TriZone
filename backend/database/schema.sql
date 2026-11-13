-- Exam Hall Irregularity Reporter Relational SQLite Schema
PRAGMA foreign_keys = ON;

-- 1. Invigilators Table
CREATE TABLE IF NOT EXISTS invigilators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invigilator_id TEXT UNIQUE NOT NULL,      -- Format: INV[DEPT][4-digit], e.g., INVCSE0001
    name TEXT NOT NULL,
    department TEXT NOT NULL,                -- CSE, ECE, EEE, etc.
    email TEXT,
    phone TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    code TEXT PRIMARY KEY,                   -- IR01, IR02, IR03, IR04, IR05
    name TEXT NOT NULL,                      -- Malpractice, Disturbance, Medical, Technical, Missing-Script
    description TEXT,
    default_priority TEXT NOT NULL,          -- CRITICAL, HIGH, MEDIUM, LOW
    authority_role TEXT NOT NULL             -- Chief Superintendent, Centre Superintendent, Controller of Examinations
);

-- 3. Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_uid TEXT UNIQUE NOT NULL,         -- UUID or timestamp-based human-readable identifier
    invigilator_id TEXT NOT NULL,            -- e.g. INVCSE0001
    irregularity_code TEXT NOT NULL,         -- e.g. IR01
    hall_id TEXT NOT NULL,                   -- e.g. HALL-302, LAB-1
    student_roll TEXT,                       -- Optional/associated student roll number
    description TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, CRITICAL
    target_authority TEXT,                   -- Assigned examination authority
    status TEXT NOT NULL DEFAULT 'SUBMITTED',-- SUBMITTED, VALIDATED, ROUTED, ASSIGNED, IN_PROGRESS, RESOLVED, REJECTED
    source_ip TEXT,                          -- Network simulation IP address
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invigilator_id) REFERENCES invigilators (invigilator_id),
    FOREIGN KEY (irregularity_code) REFERENCES categories (code)
);

-- 4. Validation Logs Table (Automata & Regex validation audit trail)
CREATE TABLE IF NOT EXISTS validation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER,
    entity_type TEXT NOT NULL,               -- INVIGILATOR_ID, IRREGULARITY_CODE
    input_value TEXT NOT NULL,
    dfa_result INTEGER NOT NULL,             -- 1 = accepted, 0 = rejected
    regex_result INTEGER NOT NULL,           -- 1 = matched, 0 = failed
    is_valid INTEGER NOT NULL,               -- 1 = valid, 0 = invalid
    failure_reason TEXT,
    dfa_time_ns INTEGER,                     -- Execution duration in nanoseconds
    regex_time_ns INTEGER,                   -- Execution duration in nanoseconds
    agreement INTEGER DEFAULT 1,             -- 1 = DFA and Regex agree, 0 = conflict
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
);

-- 5. Routing Rules Table (Explicit Lookup Table for Examination Authority)
CREATE TABLE IF NOT EXISTS routing_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    irregularity_code TEXT UNIQUE NOT NULL,
    target_authority TEXT NOT NULL,          -- Chief Superintendent, Centre Superintendent, Controller of Examinations
    escalation_authority TEXT,
    priority TEXT NOT NULL DEFAULT 'HIGH',
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (irregularity_code) REFERENCES categories (code)
);

-- 6. Handlers Table (Staff/Authorities available for incident assignment)
CREATE TABLE IF NOT EXISTS handlers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    handler_uid TEXT UNIQUE NOT NULL,        -- HND-001, HND-002, etc.
    name TEXT NOT NULL,
    role TEXT NOT NULL,                      -- Chief Superintendent, Centre Superintendent, Controller of Examinations, Technical Lead, Medical Officer
    department TEXT NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 5,     -- Max concurrent incidents
    current_load INTEGER NOT NULL DEFAULT 0,
    is_available INTEGER NOT NULL DEFAULT 1,
    contact TEXT
);

-- 7. Assignments Table
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    handler_id INTEGER NOT NULL,
    assigned_role TEXT NOT NULL,
    assignment_type TEXT NOT NULL DEFAULT 'PRIMARY', -- PRIMARY, BACKUP, ESCALATED
    status TEXT NOT NULL DEFAULT 'ASSIGNED',         -- ASSIGNED, ACKNOWLEDGED, RESOLVED, REASSIGNED
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE,
    FOREIGN KEY (handler_id) REFERENCES handlers (id)
);

-- 8. Status History Table (Audit Trail)
CREATE TABLE IF NOT EXISTS status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    comment TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
);

-- 9. Network Routes Table (Simulated IP routing table with longest-prefix matching)
CREATE TABLE IF NOT EXISTS network_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department TEXT NOT NULL,                -- CSE, ECE, EEE, Administration
    destination_network TEXT NOT NULL,       -- e.g., 192.168.10.0/24
    subnet_mask TEXT NOT NULL,               -- 255.255.255.0
    prefix_length INTEGER NOT NULL,          -- 24
    next_hop TEXT NOT NULL,                  -- Gateway IP, e.g. 192.168.10.1
    interface TEXT NOT NULL,                 -- eth0, vlan10, wlan-exam1
    metric INTEGER NOT NULL DEFAULT 10,
    is_active INTEGER NOT NULL DEFAULT 1
);

-- 10. Dispatch Logs Table
CREATE TABLE IF NOT EXISTS dispatch_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER,
    handler_id INTEGER,
    action TEXT NOT NULL,                    -- QUEUED, ASSIGNED, ESCALATED, CAPACITY_OVERFLOW, RESOLVED
    reason TEXT,
    success INTEGER NOT NULL DEFAULT 1,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE SET NULL,
    FOREIGN KEY (handler_id) REFERENCES handlers (id) ON DELETE SET NULL
);

-- 11. Users & Authentication Table (Role-Based Access Control)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,                      -- ADMIN, INVIGILATOR, HANDLER
    name TEXT NOT NULL,
    email TEXT,
    department TEXT,
    reference_id TEXT,                       -- Link to invigilator_id or handler_uid
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. In-App Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    target_role TEXT NOT NULL DEFAULT 'ALL', -- ALL, ADMIN, INVIGILATOR, HANDLER
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'INFO',       -- INFO, WARNING, CRITICAL, SUCCESS
    report_id INTEGER,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
);

-- 13. Routing Rule Modification Audit Table
CREATE TABLE IF NOT EXISTS routing_rule_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    irregularity_code TEXT NOT NULL,
    old_target_authority TEXT,
    new_target_authority TEXT,
    old_priority TEXT,
    new_priority TEXT,
    modified_by TEXT NOT NULL,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for optimal lookup performance
CREATE INDEX IF NOT EXISTS idx_reports_uid ON reports (report_uid);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports (status);
CREATE INDEX IF NOT EXISTS idx_reports_invigilator ON reports (invigilator_id);
CREATE INDEX IF NOT EXISTS idx_network_prefix ON network_routes (prefix_length DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_role ON notifications (target_role, is_read);

