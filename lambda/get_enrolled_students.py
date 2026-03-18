

# import json
# import boto3
# from boto3.dynamodb.conditions import Attr

# # Initialize DynamoDB resource
# dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
# table = dynamodb.Table('timetable_Div_D')

# def lambda_handler(event, context):
#     try:
#         # Extract query parameters
#         params = event.get('queryStringParameters') or {}
#         class_id = params.get('class_id')
#         subject = params.get('subject')

#         if not class_id or not subject:
#             return {
#                 "statusCode": 400,
#                 "body": json.dumps({"error": "Missing class_id or subject"})
#             }

#         # Match class_id and type (Lecture/Lab)
#         response = table.scan(
#             FilterExpression=Attr("class_id").eq(class_id) & Attr("type").eq(subject)
#         )

#         items = response.get("Items", [])
#         if not items:
#             return {
#                 "statusCode": 404,
#                 "body": json.dumps({"error": f"No enrolled students found for {class_id} - {subject}"})
#             }

#         students = []

#         # Extract each student (handle both DynamoDB string & dict formats)
#         for item in items:
#             for s in item.get("students", []):
#                 if isinstance(s, dict) and "S" in s:
#                     value = s["S"]
#                 else:
#                     value = s  # direct string

#                 parts = value.split("_")
#                 sap_id = parts[0]
#                 name = parts[1] if len(parts) > 1 else "Unknown"

#                 students.append({
#                     "id": sap_id,
#                     "name": name
#                 })

#         # Remove duplicate entries based on SAP ID
#         unique_students = {s["id"]: s for s in students}.values()

#         return {
#             "statusCode": 200,
#             "headers": {
#                 "Access-Control-Allow-Origin": "*",
#                 "Content-Type": "application/json"
#             },
#             "body": json.dumps(list(unique_students))
#         }

#     except Exception as e:
#         print("Error:", str(e))
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"error": str(e)})
#         }










import json
import boto3
from boto3.dynamodb.conditions import Attr

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table("timetable_Div_D")

def lambda_handler(event, context):
    try:
        # Handle CORS preflight (OPTIONS)
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps({"message": "CORS preflight success"})
            }

        # Extract query parameters
        params = event.get("queryStringParameters") or {}
        class_id = (params.get("class_id") or "").strip()
        subject = (params.get("subject") or "").strip()

        if not class_id or not subject:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps({"error": "Missing class_id or subject"})
            }

        print(f"Received params: class_id={class_id}, subject={subject}")

        # Scan DynamoDB for all matching items (all timetable entries)
        response = table.scan(
            FilterExpression=Attr("class_id").eq(class_id) & Attr("subject").eq(subject)
        )
        items = response.get("Items", [])
        print(f"Total timetable items found: {len(items)}")

        student_set = set()

        # Merge students from all matched items
        for item in items:
            students_data = item.get("students", [])
            if isinstance(students_data, dict) and "L" in students_data:
                students_list = [x["S"] for x in students_data["L"] if "S" in x]
            else:
                students_list = [
                    s["S"] if isinstance(s, dict) and "S" in s else str(s)
                    for s in students_data
                ]

            for entry in students_list:
                entry = entry.strip()
                if "_" in entry:
                    student_set.add(entry)

        print(f"Unique students found: {len(student_set)}")

        # Convert "70322000106_Saanvi" → {"sap_id": "70322000106", "name": "Saanvi"}
        students = []
        for entry in sorted(student_set):
            sid, name = entry.split("_", 1)
            students.append({
                "sap_id": sid.strip(),
                "name": name.strip()
            })

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"students": students})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": str(e)})
        }
