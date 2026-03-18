import json
import boto3
from boto3.dynamodb.conditions import Attr


dynamodb_res = boto3.resource("dynamodb")

def lambda_handler(event, context):
    try:

        if isinstance(event.get("body"), str):
            event = json.loads(event["body"])

        faculty_id = event.get("faculty_id")
        class_id = event.get("class_id")
        subject = event.get("subject")

        if not (faculty_id and class_id and subject):
            return respond(400, {"success": False, "error": "Missing parameters"})

        print(f"[INFO] Faculty: {faculty_id}, Class: {class_id}, Subject: {subject}")

        # Dynamic table based on class
        timetable_table_name = "timetable_Div_D"

        attendance_table_name = "DailyPresent"

        timetable_table = dynamodb_res.Table(timetable_table_name)

        #Case-insensitive filtering for subject/class keys
        response = timetable_table.scan(
            FilterExpression=(Attr("class_id").eq(class_id) | Attr("Class_ID").eq(class_id)) &
                              (Attr("subject").eq(subject) | Attr("Subject").eq(subject))
        )

        items = response.get("Items", [])
        print(f"[DEBUG] Items found in {timetable_table_name}: {len(items)}")

        if not items:
            return respond(404, {"success": False, "error": f"No timetable entry found for {class_id}-{subject}"})

        # Collect all students from all matched records
        raw_students = []
        for item in items:
            raw_students.extend(item.get("students", []))

        enrolled_students = []
        for entry in raw_students:
            
            if isinstance(entry, dict) and "S" in entry:
                student_str = entry["S"]
            elif isinstance(entry, str):
                student_str = entry
            else:
                continue

            if "_" in student_str:
                sap_id, name = student_str.split("_", 1)
            else:
                sap_id, name = student_str, "Unknown"

            enrolled_students.append({
                "SAP_ID": sap_id.strip(),
                "Name": name.strip(),
                "Status": "Absent",
                "Confidence": "—",
                "Time": "—"
            })

        print(f"[DEBUG] Enrolled students parsed: {len(enrolled_students)}")

        
        attendance_table = dynamodb_res.Table(attendance_table_name)
        present_scan = attendance_table.scan()
        present_records = []

        for rec in present_scan.get("Items", []):
            subj = rec.get("Subject")
            cls = rec.get("Class_ID")
            status = rec.get("Status", "Present")

            if subj == subject and cls == class_id and status == "Present":
                present_records.append({
                    "SAP_ID": rec.get("SAP_ID"),
                    "Name": rec.get("StudentName", "Unknown"),
                    "Status": "Present",
                    "Confidence": rec.get("Confidence", ""),
                    "Time": rec.get("Time", "")
                })

        print(f"[DEBUG] Present records found: {len(present_records)}")

        all_students = []
        for s in enrolled_students:
            sap_id = s["SAP_ID"]
            match = next((p for p in present_records if p["SAP_ID"] == sap_id), None)
            if match:
                s["Status"] = "Present"
                s["Confidence"] = match.get("Confidence", "")
                s["Time"] = match.get("Time", "")
            all_students.append(s)

        for p in present_records:
            if not any(s["SAP_ID"] == p["SAP_ID"] for s in all_students):
                all_students.append(p)

        absent_count = len([s for s in all_students if s["Status"] == "Absent"])
        print(f"[INFO] Session closed — {absent_count} absentees found")

        
        return respond(200, {
            "success": True,
            "message": f"Session closed successfully ({absent_count} absentees)",
            "faculty_id": faculty_id,
            "class_id": class_id,
            "subject": subject,
            "absent_count": absent_count,
            "all_students": all_students
        })

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return respond(500, {"success": False, "error": str(e)})



def respond(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            "Access-Control-Allow-Headers": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }












