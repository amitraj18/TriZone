"""
CSV Data Exporter
-----------------
Exports comprehensive incident records and audit details to standard CSV.
"""

import io
import csv
from typing import Dict, Any, List
from database.connection import db_session

def export_reports_to_csv() -> str:
    """Generates RFC 4180 compliant CSV string from SQLite reports repository."""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header Row
    headers = [
        "Report UID",
        "Invigilator ID",
        "Invigilator Name",
        "Department",
        "Category Code",
        "Category Name",
        "Hall/Zone",
        "Student Roll No",
        "Severity",
        "Target Authority",
        "Assigned Handler",
        "Handler Role",
        "Status",
        "Source IP",
        "Submission Timestamp",
        "Factual Description"
    ]
    writer.writerow(headers)

    with db_session() as conn:
        cur = conn.execute("""
            SELECT r.report_uid, r.invigilator_id, i.name as invigilator_name, i.department as invigilator_dept,
                   r.irregularity_code, c.name as category_name, r.hall_id, r.student_roll,
                   r.severity, r.target_authority, h.name as handler_name, h.role as handler_role,
                   r.status, r.source_ip, r.created_at, r.description
            FROM reports r
            LEFT JOIN invigilators i ON r.invigilator_id = i.invigilator_id
            LEFT JOIN categories c ON r.irregularity_code = c.code
            LEFT JOIN assignments a ON r.id = a.report_id AND a.status = 'ASSIGNED'
            LEFT JOIN handlers h ON a.handler_id = h.id
            ORDER BY r.created_at DESC
        """)
        rows = cur.fetchall()
        for r in rows:
            writer.writerow([
                r["report_uid"],
                r["invigilator_id"],
                r["invigilator_name"] or "",
                r["invigilator_dept"] or "",
                r["irregularity_code"],
                r["category_name"] or "",
                r["hall_id"],
                r["student_roll"] or "N/A",
                r["severity"],
                r["target_authority"] or "",
                r["handler_name"] or "None / Queued",
                r["handler_role"] or "",
                r["status"],
                r["source_ip"],
                r["created_at"],
                r["description"]
            ])

    return output.getvalue()

