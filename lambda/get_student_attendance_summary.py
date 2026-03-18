import json
import boto3
from collections import defaultdict
from datetime import datetime

# DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
attendance_table = dynamodb.Table("AttendanceRecords")

def normalize_date(ts):
    """Convert timestamp (ISO or normal) to YYYY-MM-DD date."""
    try:
        if "T" in ts:
            return ts.split("T")[0]
        elif " " in ts:
            return ts.split(" ")[0]
        return "Unknown"
    except:
        return "Unknown"


def scan_all_items(table):
    """Fetch all DynamoDB records safely (handle pagination)."""
    items = []
    response = table.scan()
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    return items


def lambda_handler(event, context):
    # ✅ CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Content-Type": "application/json",
    }

    # ✅ Preflight CORS
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": json.dumps({"message": "CORS OK"})}

    try:
        # Parse request body
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)
        elif body is None:
            body = event

        sap_id = str(body.get("SAP_ID", "")).strip()
        if not sap_id:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"success": False, "message": "Missing SAP_ID"}),
            }

        # ✅ Get all items
        all_items = scan_all_items(attendance_table)

        # ✅ Filter by StudentID
        student_records = [r for r in all_items if str(r.get("StudentID", "")).strip() == sap_id]

        if not student_records:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"success": True, "attendance": []}),
            }

        summary = defaultdict(
            lambda: {
                "Total_Present": 0,
                "Total_Absent": 0,
                "Daily_Status": {},
                "Detailed_Records": [],
            }
        )

        # ✅ Deduplicate logic
        for r in student_records:
            subj = r.get("Subject", "Unknown")
            status = r.get("Status", "Unknown")
            faculty = r.get("FacultyID", "Unknown")
            ts = r.get("Timestamp", "")
            conf = float(r.get("Confidence", 0))
            date = normalize_date(ts)

            key = (subj, date)

            # Check if record already exists for same subject + date
            existing = next((rec for rec in summary[subj]["Detailed_Records"] if rec["Date"] == date), None)

            if existing:
                existing_ts = existing.get("Timestamp", "")
                # ✅ Keep latest timestamp
                if ts > existing_ts:
                    summary[subj]["Detailed_Records"].remove(existing)
                    summary[subj]["Detailed_Records"].append(
                        {"Timestamp": ts, "Status": status, "FacultyID": faculty, "Confidence": conf, "Date": date}
                    )
                    summary[subj]["Daily_Status"][date] = status
                # ✅ Prefer "Present" over "Absent"
                elif existing["Status"].lower() != "present" and status.lower() == "present":
                    existing["Status"] = "Present"
                    summary[subj]["Daily_Status"][date] = "Present"
                continue

            # Add new entry if not seen before
            summary[subj]["Detailed_Records"].append(
                {"Timestamp": ts, "Status": status, "FacultyID": faculty, "Confidence": conf, "Date": date}
            )
            summary[subj]["Daily_Status"][date] = status

        # ✅ Final summarized result
        final_result = []
        for subj, data in summary.items():
            for date, st in data["Daily_Status"].items():
                if st.lower() == "present":
                    data["Total_Present"] += 1
                elif st.lower() == "absent":
                    data["Total_Absent"] += 1

            total = data["Total_Present"] + data["Total_Absent"]
            percent = round((data["Total_Present"] / total * 100), 2) if total else 0

            final_result.append(
                {
                    "Subject": subj,
                    "Total_Present": data["Total_Present"],
                    "Total_Absent": data["Total_Absent"],
                    "Attendance_Percentage": percent,
                    "Detailed_Records": sorted(data["Detailed_Records"], key=lambda x: x["Timestamp"], reverse=True),
                }
            )

        # Sort alphabetically for consistent display
        final_result = sorted(final_result, key=lambda x: x["Subject"])

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(
                {
                    "success": True,
                    "attendance": final_result,
                    "last_updated": datetime.utcnow().isoformat(),
                }
            ),
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"success": False, "message": str(e)}),
        }
