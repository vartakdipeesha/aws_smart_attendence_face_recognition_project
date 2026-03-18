# get_active_session.py
import json
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
sessions_table = dynamodb.Table('Sessions')
students_table = dynamodb.Table('students')
faculty_table = dynamodb.Table('Faculty')

def now_utc():
    return datetime.now(timezone.utc)

def iso_to_dt(iso_str):
    return datetime.fromisoformat(iso_str)

def lambda_handler(event, context):
    try:
        params = event.get('queryStringParameters', {}) or {}
        sap_id = params.get('sapId')

        if not sap_id:
            return response(400, {"message": "Missing sapId"})

        # 1) Get student to determine class/division
        student_resp = students_table.get_item(Key={"SAP_ID": sap_id})
        student = student_resp.get("Item")
        if not student:
            return response(404, {"message": f"Student {sap_id} not found"})

        student_class = student.get("class_id") or student.get("division") or student.get("class") or "N/A"

        # 2) Scan sessions table (small table in demo — scanning is OK)
        sessions_resp = sessions_table.scan()
        sessions = sessions_resp.get("Items", [])
        now = now_utc()

        # 3) Find best session for student's class:
        # Prefer ACTIVE (now between start and end), else nearest STARTING (start_time > now)
        active_session = None
        starting_candidate = None
        starting_delta_seconds = None

        for s in sessions:
            if s.get("class_id") != student_class:
                continue
            try:
                start_dt = iso_to_dt(s["start_time"])
                end_dt = iso_to_dt(s["end_time"])
            except Exception:
                continue

            # If session already active
            if start_dt <= now <= end_dt:
                s["status"] = "ACTIVE"
                active_session = s
                break

            # If session is in the future and within a reasonable window, track closest one
            if start_dt > now:
                delta = (start_dt - now).total_seconds()
                # track nearest future session (choose the smallest delta)
                if starting_candidate is None or delta < starting_delta_seconds:
                    starting_candidate = s
                    starting_delta_seconds = delta

        # If no ACTIVE, and the nearest STARTING is within e.g. 30 minutes, return as STARTING
        if not active_session and starting_candidate:
            # mark STARTING if within 30 minutes
            if starting_delta_seconds <= 1800:  # 30 minutes
                starting_candidate["status"] = "STARTING"
                active_session = starting_candidate

        if not active_session:
            return response(200, {})  # nothing active for this student

        # optional: attach facultyName if not present
        if not active_session.get("facultyName") and active_session.get("faculty_id"):
            f = faculty_table.get_item(Key={"faculty_id": active_session["faculty_id"]}).get("Item", {})
            if f:
                active_session["facultyName"] = f.get("name", active_session.get("faculty_id"))

        # Return only the fields the frontend needs
        result = {
            "session_id": active_session.get("session_id"),
            "class_id": active_session.get("class_id"),
            "facultyName": active_session.get("facultyName", ""),
            "subject": active_session.get("subject", ""),
            "status": active_session.get("status"),
            "start_time": active_session.get("start_time"),
            "end_time": active_session.get("end_time")
        }

        return response(200, result)

    except Exception as e:
        print("Error:", e)
        return response(500, {"message": str(e)})


def response(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }
