"""
Flask Application Factory & REST API Controllers
Exam Hall Irregularity Reporter (IRIS)
------------------------------------------------
Integrates:
1. TOC Validation: Character-by-character DFA + Regex equivalence assertion.
2. CN Routing: Examination zone source verification + Destination LPM routing.
3. Dispatch Engine: Deterministic authority allocation, capacity management, priority queue.
4. RBAC Authentication, CSV Export, In-App Notifications & Demo Reset.
"""

import os
import uuid
from flask import Flask, jsonify, request, Response, g
from flask_cors import CORS
from config import Config, DATABASE_PATH
from database.connection import get_db_connection, db_session
from database.seed_data import init_db
from database.demo_seeder import reset_demonstration_database
from database.models import (
    InvigilatorModel,
    CategoryModel,
    RoutingRuleModel,
    HandlerModel,
    NetworkRouteModel,
    ReportModel
)
from validation.validation_service import (
    validate_invigilator_id,
    validate_irregularity_code,
    validate_report_identifiers
)
from networking.ip_addressing import (
    validate_source_ip_for_zone,
    get_authority_destination_ip,
    EXAMINATION_ZONES
)
from networking.network_routing import lookup_route, load_active_routes
from networking.routing_service import process_network_packet_routing
from networking.subnet_calculator import SubnetCalculator
from dispatch.dispatch_engine import DispatchEngine
from dispatch.handler_manager import HandlerManager
from dispatch.queue_manager import QueueManager
from dispatch.priority_manager import PriorityManager
from auth.auth_service import (
    authenticate_user,
    get_current_user_from_request,
    require_auth
)
from notifications.notification_service import NotificationService
from export.csv_exporter import export_reports_to_csv

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Auto-initialize database if not present
    if not os.path.exists(app.config["DATABASE"]):
        init_db(db_path=app.config["DATABASE"], force=False)

    # -------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health_check():
        db_status = "unreachable"
        try:
            with get_db_connection() as conn:
                conn.execute("SELECT 1")
                db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

        return jsonify({
            "status": "healthy",
            "service": "Exam Hall Irregularity Reporter API",
            "version": "2.5.0",
            "phase": "Master Complete",
            "database": db_status
        }), 200

    # -------------------------------------------------------------
    # Authentication & User Profile Endpoints
    # -------------------------------------------------------------
    @app.route("/api/auth/login", methods=["POST"])
    def login_endpoint():
        payload = request.get_json() or {}
        username = payload.get("username", "")
        password = payload.get("password", "")

        user = authenticate_user(username, password)
        if not user:
            return jsonify({
                "success": False,
                "error": "Invalid username or password. Please check your credentials."
            }), 401

        # Emit login notification
        NotificationService.create_notification(
            title="User Signed In",
            message=f"{user['name']} signed in with role {user['role']}.",
            n_type="INFO",
            target_role="ADMIN"
        )

        return jsonify({
            "success": True,
            "data": user
        }), 200

    @app.route("/api/auth/me", methods=["GET"])
    def current_user_endpoint():
        auth_header = request.headers.get("Authorization", "")
        if auth_header:
            if not auth_header.startswith("Bearer "):
                return jsonify({"success": False, "error": "Invalid auth header."}), 401
            user = get_current_user_from_request()
            if not user:
                return jsonify({"success": False, "error": "Invalid or expired token."}), 401
            return jsonify({"success": True, "data": user}), 200

        # Fallback mock for open hackathon inspection when unauthenticated
        return jsonify({
            "success": True,
            "data": {
                "id": 1,
                "username": "admin",
                "role": "ADMIN",
                "name": "Dr. Barbara Liskov (Admin)",
                "department": "Examination Cell"
            }
        }), 200

    @app.route("/api/auth/logout", methods=["POST"])
    def logout_endpoint():
        return jsonify({"success": True, "message": "Logged out successfully."}), 200

    # -------------------------------------------------------------
    # In-App Notifications Endpoints
    # -------------------------------------------------------------
    @app.route("/api/notifications", methods=["GET"])
    def get_notifications_endpoint():
        role = request.args.get("role", "ALL")
        limit = request.args.get("limit", default=30, type=int)
        notifications = NotificationService.get_notifications(target_role=role, limit=limit)
        unread_count = sum(1 for n in notifications if not n["is_read"])
        return jsonify({
            "success": True,
            "count": len(notifications),
            "unread_count": unread_count,
            "data": notifications
        }), 200

    @app.route("/api/notifications/<int:notification_id>/read", methods=["PUT", "PATCH"])
    def mark_notification_read_endpoint(notification_id):
        updated = NotificationService.mark_as_read(notification_id)
        return jsonify({"success": updated, "data": {"id": notification_id, "is_read": 1}}), 200

    @app.route("/api/notifications/read-all", methods=["PUT", "POST"])
    @app.route("/api/notifications/mark-all-read", methods=["PUT", "POST"])
    def mark_all_notifications_read_endpoint():
        role = request.args.get("role", "ALL")
        count = NotificationService.mark_all_as_read(role)
        return jsonify({"success": True, "marked_count": count}), 200

    # -------------------------------------------------------------
    # CSV Data Export
    # -------------------------------------------------------------
    @app.route("/api/reports/export/csv", methods=["GET"])
    def export_reports_csv_endpoint():
        csv_data = export_reports_to_csv()
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=iris_exam_reports_export.csv"}
        )

    # -------------------------------------------------------------
    # Hackathon Demo Data Reset
    # -------------------------------------------------------------
    @app.route("/api/demo/reset", methods=["POST"])
    def reset_demo_endpoint():
        res = reset_demonstration_database()
        return jsonify(res), 200

    # -------------------------------------------------------------
    # TOC Validation Endpoints
    # -------------------------------------------------------------
    @app.route("/api/reports/validate", methods=["POST"])
    def validate_identifiers_endpoint():
        data = request.get_json() or {}
        inv_id = data.get("invigilator_id", "")
        irr_code = data.get("irregularity_code", "")

        val_result = validate_report_identifiers(inv_id, irr_code)
        status_code = 200 if val_result["is_valid"] else 400
        return jsonify({
            "success": val_result["is_valid"],
            "data": val_result
        }), status_code

    # -------------------------------------------------------------
    # Report Submission & Processing Pipeline (19-Step Complete Flow)
    # -------------------------------------------------------------
    @app.route("/api/reports", methods=["POST"])
    def submit_report():
        payload = request.get_json() or {}
        
        invigilator_id = payload.get("invigilator_id", "").strip()
        irregularity_code = payload.get("irregularity_code", "").strip()
        hall_id = payload.get("hall_id", "").strip()
        student_roll = payload.get("student_roll", "").strip() or None
        description = payload.get("description", "").strip()
        severity = payload.get("severity", "MEDIUM").strip().upper()
        source_ip = payload.get("source_ip", "").strip()
        is_emergency = bool(payload.get("is_emergency", False)) or (severity == "CRITICAL")
        override_reason = payload.get("override_reason")

        # Step 1: Validate required fields
        if not invigilator_id or not irregularity_code or not hall_id or not description or not source_ip:
            return jsonify({
                "success": False,
                "error": "Missing required fields: invigilator_id, irregularity_code, hall_id, description, and source_ip are mandatory."
            }), 400

        # Step 2-4: Run TOC DFA + Regex validation
        val_result = validate_report_identifiers(invigilator_id, irregularity_code)
        if not val_result["is_valid"]:
            return jsonify({
                "success": False,
                "stage": "TOC_VALIDATION",
                "status": "REJECTED",
                "errors": val_result["errors"],
                "validation_breakdown": val_result
            }), 400

        # Step 5: Check authority routing rule from SQLite
        with db_session() as conn:
            cur_rule = conn.execute("""
                SELECT rr.irregularity_code, rr.target_authority, rr.escalation_authority, 
                       rr.priority, c.name as category_name
                FROM routing_rules rr
                JOIN categories c ON rr.irregularity_code = c.code
                WHERE rr.irregularity_code = ? AND rr.is_active = 1
            """, (irregularity_code,))
            rule = cur_rule.fetchone()

        if not rule:
            return jsonify({
                "success": False,
                "stage": "EXAMINATION_ROUTING",
                "error": f"No active authority routing rule found for code '{irregularity_code}'."
            }), 400

        target_authority = rule["target_authority"]

        # Step 6: Validate Source IP against Examination Zone and Run LPM on Destination IP
        net_result = process_network_packet_routing(
            source_ip=source_ip,
            hall_id=hall_id,
            target_authority=target_authority
        )
        if not net_result["success"]:
            return jsonify({
                "success": False,
                "stage": net_result.get("stage", "NETWORK_ROUTING"),
                "status": "REJECTED",
                "error": net_result.get("error", "Network packet routing rejected."),
                "network_details": net_result
            }), 400

        # Step 7: Create report record in SQLite (status 'VALIDATED')
        rep_uid = f"REP-{uuid.uuid4().hex[:8].upper()}"
        with db_session() as conn:
            cur = conn.execute("""
                INSERT INTO reports (report_uid, invigilator_id, irregularity_code, hall_id, student_roll, description, severity, target_authority, status, source_ip)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'VALIDATED', ?)
            """, (rep_uid, invigilator_id, irregularity_code, hall_id, student_roll, description, severity, target_authority, source_ip))
            report_id = cur.lastrowid

            conn.execute("""
                INSERT INTO status_history (report_id, old_status, new_status, updated_by, comment)
                VALUES (?, 'SUBMITTED', 'VALIDATED', 'SYSTEM_GATEWAY', 'TOC and CN parameters formally validated.')
            """, (report_id,))

        # Step 8: Execute Dispatch Engine (Handler assignment or priority queueing)
        dispatch_result = DispatchEngine.dispatch_report(
            report_id=report_id,
            irregularity_code=irregularity_code,
            is_emergency=is_emergency,
            override_reason=override_reason
        )

        # Trigger in-app notification
        notif_type = "CRITICAL" if is_emergency else "INFO"
        if dispatch_result["dispatch_status"] == "ASSIGNED":
            handler_name = dispatch_result["assigned_handler"]["name"]
            NotificationService.create_notification(
                title=f"Incident {rep_uid} Dispatched",
                message=f"Category {rule['category_name']} ({irregularity_code}) assigned to {handler_name} ({target_authority}).",
                n_type=notif_type,
                target_role="HANDLER",
                report_id=report_id
            )
        elif dispatch_result["dispatch_status"] == "QUEUED":
            NotificationService.create_notification(
                title=f"Incident {rep_uid} Enqueued",
                message=f"All handlers for {target_authority} at capacity. Incident placed in priority queue.",
                n_type="WARNING",
                target_role="ADMIN",
                report_id=report_id
            )

        return jsonify({
            "success": True,
            "report_id": report_id,
            "report_uid": rep_uid,
            "invigilator_id": invigilator_id,
            "irregularity_code": irregularity_code,
            "category": rule["category_name"],
            "target_authority": target_authority,
            "hall_id": hall_id,
            "source_ip": source_ip,
            "status": dispatch_result["dispatch_status"],
            "priority": dispatch_result["priority"],
            "assigned_handler": dispatch_result["assigned_handler"],
            "network_routing": net_result["routing_decision"],
            "validation_audit": val_result,
            "message": dispatch_result["reason"]
        }), 201

    # -------------------------------------------------------------
    # Report Retrieval & Status Update Endpoints
    # -------------------------------------------------------------
    @app.route("/api/reports", methods=["GET"])
    def get_reports():
        limit = request.args.get("limit", default=100, type=int)
        status_filter = request.args.get("status")
        category_filter = request.args.get("category")
        search_query = request.args.get("search", "").strip()

        with db_session() as conn:
            query = """
                SELECT r.*, c.name as category_name, i.name as invigilator_name, i.department as invigilator_dept,
                       a.assigned_role, a.assignment_type, h.name as handler_name, h.handler_uid
                FROM reports r
                LEFT JOIN categories c ON r.irregularity_code = c.code
                LEFT JOIN invigilators i ON r.invigilator_id = i.invigilator_id
                LEFT JOIN assignments a ON r.id = a.report_id AND a.status = 'ASSIGNED'
                LEFT JOIN handlers h ON a.handler_id = h.id
                WHERE 1=1
            """
            params = []
            if status_filter:
                query += " AND r.status = ?"
                params.append(status_filter.upper())
            if category_filter:
                query += " AND r.irregularity_code = ?"
                params.append(category_filter.upper())
            if search_query:
                query += " AND (r.report_uid LIKE ? OR r.invigilator_id LIKE ? OR r.hall_id LIKE ? OR r.student_roll LIKE ? OR r.description LIKE ?)"
                like_term = f"%{search_query}%"
                params.extend([like_term, like_term, like_term, like_term, like_term])

            query += " ORDER BY r.created_at DESC LIMIT ?"
            params.append(limit)

            cur = conn.execute(query, tuple(params))
            reports = [dict(r) for r in cur.fetchall()]

        return jsonify({
            "success": True,
            "count": len(reports),
            "data": reports
        }), 200

    @app.route("/api/reports/<int:report_id>", methods=["GET"])
    def get_report_details(report_id):
        with db_session() as conn:
            cur = conn.execute("""
                SELECT r.*, c.name as category_name, i.name as invigilator_name, i.department as invigilator_dept
                FROM reports r
                LEFT JOIN categories c ON r.irregularity_code = c.code
                LEFT JOIN invigilators i ON r.invigilator_id = i.invigilator_id
                WHERE r.id = ?
            """, (report_id,))
            rep = cur.fetchone()
            if not rep:
                return jsonify({"success": False, "error": f"Report ID {report_id} not found."}), 404

            report_dict = dict(rep)

            cur_val = conn.execute("SELECT * FROM validation_logs WHERE report_id = ? ORDER BY validated_at ASC", (report_id,))
            report_dict["validation_logs"] = [dict(r) for r in cur_val.fetchall()]

            cur_assign = conn.execute("""
                SELECT a.*, h.name as handler_name, h.handler_uid, h.role, h.contact
                FROM assignments a
                JOIN handlers h ON a.handler_id = h.id
                WHERE a.report_id = ?
                ORDER BY a.assigned_at DESC
            """, (report_id,))
            report_dict["assignments"] = [dict(r) for r in cur_assign.fetchall()]

            cur_hist = conn.execute("SELECT * FROM status_history WHERE report_id = ? ORDER BY timestamp ASC", (report_id,))
            report_dict["status_history"] = [dict(r) for r in cur_hist.fetchall()]

            cur_disp = conn.execute("""
                SELECT dl.*, h.name as handler_name FROM dispatch_logs dl
                LEFT JOIN handlers h ON dl.handler_id = h.id
                WHERE dl.report_id = ?
                ORDER BY dl.timestamp ASC
            """, (report_id,))
            report_dict["dispatch_logs"] = [dict(r) for r in cur_disp.fetchall()]

        return jsonify({"success": True, "data": report_dict}), 200

    @app.route("/api/reports/<int:report_id>/history", methods=["GET"])
    def get_report_history(report_id):
        with db_session() as conn:
            cur = conn.execute("SELECT * FROM status_history WHERE report_id = ? ORDER BY timestamp ASC", (report_id,))
            rows = [dict(r) for r in cur.fetchall()]
        return jsonify({"success": True, "count": len(rows), "data": rows}), 200

    @app.route("/api/reports/<int:report_id>/status", methods=["PUT"])
    def update_report_status_endpoint(report_id):
        payload = request.get_json() or {}
        new_status = payload.get("status")
        updated_by = payload.get("updated_by", "EXAMINATION_CELL")
        comment = payload.get("comment", "")

        if not new_status:
            return jsonify({"success": False, "error": "Field 'status' is required."}), 400

        try:
            res = DispatchEngine.update_report_status(report_id, new_status, updated_by, comment)
            
            # Emit notification if incident resolved
            if new_status.upper() == "RESOLVED":
                NotificationService.create_notification(
                    title="Incident Resolved",
                    message=f"Report ID {report_id} has been marked RESOLVED. Handler capacity released.",
                    n_type="SUCCESS",
                    target_role="ALL",
                    report_id=report_id
                )

            return jsonify({"success": True, "data": res}), 200
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route("/api/reports/<int:report_id>/assign", methods=["POST"])
    def manual_assign_report(report_id):
        payload = request.get_json() or {}
        handler_id = payload.get("handler_id")
        notes = payload.get("notes", "Manual supervisor assignment.")

        if not handler_id:
            return jsonify({"success": False, "error": "Field 'handler_id' is required."}), 400

        with db_session() as conn:
            h = conn.execute("SELECT id, name, role, capacity, current_load, is_available FROM handlers WHERE id = ?", (handler_id,)).fetchone()
            if not h:
                return jsonify({"success": False, "error": "Handler not found."}), 404
            if not h["is_available"]:
                return jsonify({"success": False, "error": "Selected handler is marked offline."}), 400
            if h["current_load"] >= h["capacity"]:
                return jsonify({"success": False, "error": f"Handler {h['name']} is at maximum capacity ({h['capacity']})."}), 400

            conn.execute("UPDATE handlers SET current_load = current_load + 1 WHERE id = ?", (handler_id,))
            conn.execute("UPDATE reports SET status = 'ASSIGNED', target_authority = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (h["role"], report_id))
            conn.execute("""
                INSERT INTO assignments (report_id, handler_id, assigned_role, assignment_type, status, notes)
                VALUES (?, ?, ?, 'PRIMARY', 'ASSIGNED', ?)
            """, (report_id, handler_id, h["role"], notes))
            conn.execute("""
                INSERT INTO status_history (report_id, old_status, new_status, updated_by, comment)
                VALUES (?, 'QUEUED', 'ASSIGNED', 'SUPERVISOR', ?)
            """, (report_id, f"Manually assigned to {h['name']} ({h['role']})."))

        return jsonify({"success": True, "message": f"Report successfully assigned to {h['name']}."}), 200

    # -------------------------------------------------------------
    # Computer Networks Routing & Subnet Calculation Endpoints
    # -------------------------------------------------------------
    @app.route("/api/network-routes", methods=["GET"])
    def get_network_routes():
        routes = NetworkRouteModel.get_all()
        return jsonify({"success": True, "count": len(routes), "data": routes}), 200

    @app.route("/api/network-routes/lookup", methods=["POST"])
    def network_route_lookup():
        payload = request.get_json() or {}
        destination_ip = payload.get("destination_ip")
        if not destination_ip:
            return jsonify({"success": False, "error": "Field 'destination_ip' is required."}), 400

        result = lookup_route(destination_ip)
        status_code = 200 if result.get("reachable", False) else 404
        return jsonify(result), status_code

    @app.route("/api/network-routes/calculate-subnet", methods=["POST"])
    def calculate_subnet_endpoint():
        payload = request.get_json() or {}
        cidr = payload.get("cidr")
        if not cidr:
            return jsonify({"success": False, "error": "Field 'cidr' is required."}), 400

        res = SubnetCalculator.calculate(cidr)
        status_code = 200 if res.get("success", False) else 400
        return jsonify(res), status_code

    # -------------------------------------------------------------
    # Handler Management Endpoints
    # -------------------------------------------------------------
    @app.route("/api/handlers", methods=["GET"])
    def get_handlers():
        handlers = HandlerManager.get_all_handlers()
        return jsonify({"success": True, "count": len(handlers), "data": handlers}), 200

    @app.route("/api/handlers/<int:handler_id>/availability", methods=["PUT"])
    def update_handler_availability(handler_id):
        payload = request.get_json() or {}
        if "is_available" not in payload:
            return jsonify({"success": False, "error": "Field 'is_available' (boolean) is required."}), 400

        is_avail = bool(payload["is_available"])
        updated = HandlerManager.set_availability(handler_id, is_avail)
        if not updated:
            return jsonify({"success": False, "error": f"Handler {handler_id} not found."}), 404

        dequeued = None
        if is_avail:
            with db_session() as conn:
                h = conn.execute("SELECT role FROM handlers WHERE id = ?", (handler_id,)).fetchone()
                if h:
                    dequeued = QueueManager.process_queue_for_authority(h["role"], conn)

        return jsonify({
            "success": True,
            "handler_id": handler_id,
            "is_available": is_avail,
            "dequeued_incident": dequeued,
            "message": f"Handler availability set to {'Available' if is_avail else 'Offline'}."
        }), 200

    @app.route("/api/handlers/<int:handler_id>/capacity", methods=["PUT"])
    def update_handler_capacity(handler_id):
        payload = request.get_json() or {}
        new_cap = payload.get("capacity")
        if new_cap is None:
            return jsonify({"success": False, "error": "Field 'capacity' (int) is required."}), 400

        try:
            new_cap_int = int(new_cap)
            updated = HandlerManager.update_capacity(handler_id, new_cap_int)
            if not updated:
                return jsonify({"success": False, "error": f"Handler {handler_id} not found."}), 404

            dequeued = None
            with db_session() as conn:
                h = conn.execute("SELECT role FROM handlers WHERE id = ?", (handler_id,)).fetchone()
                if h:
                    dequeued = QueueManager.process_queue_for_authority(h["role"], conn)

            return jsonify({
                "success": True,
                "handler_id": handler_id,
                "capacity": new_cap_int,
                "dequeued_incident": dequeued,
                "message": f"Handler capacity updated to {new_cap_int}."
            }), 200
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400

    # -------------------------------------------------------------
    # Dispatch Queue & Log Endpoints
    # -------------------------------------------------------------
    @app.route("/api/dispatch/queue", methods=["GET"])
    def get_dispatch_queue():
        queue_items = QueueManager.get_queued_reports()
        return jsonify({"success": True, "count": len(queue_items), "data": queue_items}), 200

    @app.route("/api/dispatch/logs", methods=["GET"])
    def get_dispatch_logs():
        limit = request.args.get("limit", default=50, type=int)
        with db_session() as conn:
            cur = conn.execute("""
                SELECT dl.*, r.report_uid, r.irregularity_code, h.name as handler_name, h.role as handler_role
                FROM dispatch_logs dl
                LEFT JOIN reports r ON dl.report_id = r.id
                LEFT JOIN handlers h ON dl.handler_id = h.id
                ORDER BY dl.timestamp DESC
                LIMIT ?
            """, (limit,))
            logs = [dict(r) for r in cur.fetchall()]

        return jsonify({"success": True, "count": len(logs), "data": logs}), 200

    # -------------------------------------------------------------
    # Categories & Routing Rules Management (with Admin Modification Audit)
    # -------------------------------------------------------------
    @app.route("/api/categories", methods=["GET"])
    def get_categories():
        categories = CategoryModel.get_all()
        return jsonify({"success": True, "data": categories}), 200

    @app.route("/api/routing-rules", methods=["GET"])
    def get_routing_rules():
        rules = RoutingRuleModel.get_all()
        return jsonify({"success": True, "data": rules}), 200

    @app.route("/api/routing-rules/<int:rule_id>", methods=["PUT"])
    def update_routing_rule_endpoint(rule_id):
        payload = request.get_json() or {}
        new_target = payload.get("target_authority")
        new_priority = payload.get("priority")
        new_escalation = payload.get("escalation_authority")
        reason = payload.get("reason", "Administrative policy adjustment.")
        modified_by = payload.get("modified_by", "ADMINISTRATOR")

        with db_session() as conn:
            cur = conn.execute("SELECT * FROM routing_rules WHERE id = ?", (rule_id,))
            rule = cur.fetchone()
            if not rule:
                return jsonify({"success": False, "error": f"Rule {rule_id} not found."}), 404

            # Record audit history
            conn.execute("""
                INSERT INTO routing_rule_history 
                (rule_id, irregularity_code, old_target_authority, new_target_authority, old_priority, new_priority, modified_by, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule_id, 
                rule["irregularity_code"], 
                rule["target_authority"], 
                new_target or rule["target_authority"],
                rule["priority"],
                new_priority or rule["priority"],
                modified_by,
                reason
            ))

            # Update rule
            conn.execute("""
                UPDATE routing_rules 
                SET target_authority = COALESCE(?, target_authority),
                    priority = COALESCE(?, priority),
                    escalation_authority = COALESCE(?, escalation_authority)
                WHERE id = ?
            """, (new_target, new_priority, new_escalation, rule_id))

        return jsonify({
            "success": True,
            "message": f"Routing rule {rule['irregularity_code']} updated successfully."
        }), 200

    @app.route("/api/routing-rules/history", methods=["GET"])
    def get_routing_rule_history():
        with db_session() as conn:
            cur = conn.execute("SELECT * FROM routing_rule_history ORDER BY timestamp DESC LIMIT 50")
            history = [dict(r) for r in cur.fetchall()]
        return jsonify({"success": True, "data": history}), 200

    @app.route("/api/invigilators", methods=["GET"])
    def get_invigilators():
        invigilators = InvigilatorModel.get_all()
        return jsonify({"success": True, "data": invigilators}), 200

    # -------------------------------------------------------------
    # High-Level KPI Stats
    # -------------------------------------------------------------
    @app.route("/api/stats", methods=["GET"])
    def get_stats():
        stats = ReportModel.get_stats()
        with db_session() as conn:
            queued_count = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'QUEUED'").fetchone()[0]
            escalated_count = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'ESCALATED'").fetchone()[0]
            in_prog_count = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'IN_PROGRESS'").fetchone()[0]
            stats["queued_incidents"] = queued_count
            stats["escalated_incidents"] = escalated_count
            stats["in_progress_incidents"] = in_prog_count
        return jsonify({"success": True, "data": stats}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
