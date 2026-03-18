import boto3
from datetime import datetime

# Initialize DynamoDB
ddb = boto3.resource('dynamodb')
students_table = ddb.Table('students')
daily_table = ddb.Table('DailyAttendance')  # Merged table

def lambda_handler(event, context):
    sap_id_input = event.get("SAP_ID")
    if not sap_id_input:
        return {"error": "No SAP ID provided"}

    # Fetch student info
    student = students_table.get_item(Key={"SAP_ID": sap_id_input}).get("Item")
    if not student:
        return {"error": "SAP ID not found"}

    # Determine Entry/Exit (Even-Odd logic)
    tap_count = student.get("TapCount", 0) + 1
    action = "Entry" if tap_count % 2 == 1 else "Exit"
    status = "Inside" if action == "Entry" else "Outside"

    # Update students table
    students_table.update_item(
        Key={"SAP_ID": sap_id_input},
        UpdateExpression="SET TapCount=:t, #st=:s",
        ExpressionAttributeNames={"#st": "Status"},
        ExpressionAttributeValues={":t": tap_count, ":s": status}
    )

    timestamp = datetime.utcnow().isoformat()
    today_date = datetime.utcnow().date().isoformat()

    # Update merged DailyAttendance table
    daily_table.update_item(
        Key={"SAP_ID": sap_id_input, "Date": today_date},
        UpdateExpression="SET LastAction=:a, LastTimestamp=:ts ADD ActionHistory :h",
        ExpressionAttributeValues={
            ":a": action,
            ":ts": timestamp,
            ":h": {timestamp: action}  # store historical actions in a map
        },
        ReturnValues="ALL_NEW"
    )

    return {
        "SAP_ID": sap_id_input,
        "Name": student.get("Name", "Unknown"),
        "Action": action,
        "Timestamp": timestamp,
        "Status": status
    }
