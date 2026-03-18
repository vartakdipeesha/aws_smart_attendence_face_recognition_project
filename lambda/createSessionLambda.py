# create_session.py
import json
import boto3
import time
import uuid
from datetime import datetime, timedelta, timezone

dynamodb = boto3.resource('dynamodb')
sessions_table = dynamodb.Table('Sessions')
faculty_table = dynamodb.Table('Faculty')

def iso_now_utc():
    return datetime.now(timezone.utc).isoformat()

def parse_iso(dt_str):
    # safe parse for ISO str -> datetime
    return datetime.fromisoformat(dt_str)

def lambda_handler(event, context):
    try:
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body)
        elif body is None:
            body = event

        faculty_id = body.get('faculty_id')
        class_id = body.get('class_id')
        subject = body.get('subject')  # optional; backend will fallback to Faculty table
        countdown_seconds = int(body.get('countdown_seconds', 30))  # default 30s countdown
        duration_minutes = int(body.get('duration_minutes', 10))   # default session duration 10min

        # optional explicit start_time in ISO format (frontend can send start_time instead of countdown)
        start_time_iso = body.get('start_time')

        if not faculty_id or not class_id:
            return response(400, {"message": "Missing faculty_id or class_id"})

        # fetch faculty info (to attach facultyName if available)
        faculty_item = faculty_table.get_item(Key={'faculty_id': faculty_id}).get('Item', {})
        faculty_name = faculty_item.get('name', faculty_id)

        # determine start_time and end_time
        if start_time_iso:
            start_dt = parse_iso(start_time_iso)
        else:
            # schedule start_time = now + countdown_seconds
            start_dt = datetime.now(timezone.utc) + timedelta(seconds=countdown_seconds)

        end_dt = start_dt + timedelta(minutes=duration_minutes)

        session_id = f"SESSION_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        session_item = {
            "session_id": session_id,
            "faculty_id": faculty_id,
            "facultyName": faculty_name,
            "class_id": class_id,
            "subject": subject or faculty_item.get('subject', 'N/A'),
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "status": "STARTING",   # initial
            "created_at": iso_now_utc()
        }

        sessions_table.put_item(Item=session_item)

        return response(200, {
            "message": "Session created",
            "session": session_item
        })

    except Exception as e:
        print("Error:", str(e))
        return response(500, {"message": str(e)})


def response(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }
