





# import json
# import boto3
# import base64
# import re
# from datetime import datetime
# from boto3.dynamodb.conditions import Attr

# # --- Initialize AWS clients ---
# rekognition = boto3.client("rekognition", region_name="ap-south-1")
# dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")

# # --- Table references ---
# timetable_table = dynamodb.Table("timetable_Div_D")
# attendance_table = dynamodb.Table("AttendanceRecords")

# COLLECTION_ID = "smart-campus-students-collection"


# def lambda_handler(event, context):
#     try:
#         print("Raw event:", event)

#         # --- Handle both API Gateway and direct invocation ---
#         if "body" in event:
#             body = json.loads(event["body"])
#         else:
#             body = event

#         image_data = body.get("image", "")
#         class_id = body.get("class_id", "").strip()
#         subject = body.get("subject", "").strip()
#         faculty_id = body.get("faculty_id", "").strip()

#         # --- Validation ---
#         if not image_data or not class_id or not subject or not faculty_id:
#             return _response(400, {"error": "Missing required fields"})

#         # --- Clean Base64 string ---
#         if image_data.startswith("data:image"):
#             image_data = re.sub("^data:image/[^;]+;base64,", "", image_data)

#         try:
#             image_bytes = base64.b64decode(image_data)
#         except Exception as e:
#             print("Base64 decode failed:", str(e))
#             return _response(400, {"error": "Invalid base64 image"})

#         # --- Step 1: Face Recognition ---
#         rekog_response = rekognition.search_faces_by_image(
#             CollectionId=COLLECTION_ID,
#             Image={"Bytes": image_bytes},
#             MaxFaces=1,
#             FaceMatchThreshold=90
#         )

#         matches = rekog_response.get("FaceMatches", [])
#         if not matches:
#             print("No face match found")
#             return _response(200, {"message": "Recognition failed", "match": False})

#         top_match = matches[0]
#         external_id = top_match["Face"]["ExternalImageId"]
#         confidence = round(top_match["Similarity"], 2)

        
#         if "_" in external_id:
#             student_id, student_name = external_id.split("_", 1)
#         else:
#             student_id, student_name = external_id, "Unknown"

#         print(f"Matched Student: {student_id} ({student_name}) with {confidence}% confidence")

#         # --- Step 2: Check Enrollment ---
#         try:
#             response = timetable_table.scan(
#                 FilterExpression=Attr("class_id").eq(class_id) & Attr("subject").eq(subject)
#             )
#         except Exception as e:
#             print("DynamoDB error:", str(e))
#             return _response(500, {"error": "Database read error"})

#         items = response.get("Items", [])
#         enrolled_ids = []

#         for item in items:
#             for s in item.get("students", []):
#                 if isinstance(s, str):
#                     sid = s.split("_")[0].strip()
#                 elif isinstance(s, dict) and "S" in s:
#                     sid = s["S"].split("_")[0].strip()
#                 else:
#                     continue
#                 enrolled_ids.append(sid)

#         enrolled_ids = list(set(enrolled_ids))
#         print(f"Enrolled IDs for {class_id}-{subject}: {enrolled_ids}")

#         eligible = student_id in enrolled_ids

#         # --- Step 3: Record Attendance if Eligible ---
#         if eligible:
#             timestamp = datetime.now().isoformat()
#             try:
#                 attendance_table.put_item(
#                     Item={
#                         "SAP_ID": student_id,
#                         "StudentName": student_name,
#                         "ClassID": class_id,
#                         "Subject": subject,
#                         "FacultyID": faculty_id,
#                         "Timestamp": timestamp,
#                         "Confidence": confidence,
#                         "Status": "Present"
#                     }
#                 )
#                 print(f"Attendance recorded for {student_id} ({student_name}) at {timestamp}")
#             except Exception as e:
#                 print("Failed to write to AttendanceRecords:", str(e))

#         result = {
#             "StudentID": student_id,
#             "StudentName": student_name,
#             "Confidence": confidence,
#             "Eligible": eligible,
#             "message": "Marked Present" if eligible else "Recognized but not enrolled"
#         }

#         print("Result →", result)
#         return _response(200, result)

#     except Exception as e:
#         print("Unexpected Error:", str(e))
#         return _response(500, {"error": str(e)})


# def _response(status, body_dict):
#     """Reusable HTTP response with CORS headers."""
#     return {
#         "statusCode": status,
#         "headers": {
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Headers": (
#                 "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
#             ),
#             "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
#             "Content-Type": "application/json"
#         },
#         "body": json.dumps(body_dict)
#     }






















import json
import boto3
import base64
import re
import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

# --- AWS clients ---
rekognition = boto3.client("rekognition", region_name="ap-south-1")
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")

# --- DynamoDB Tables ---
timetable_table = dynamodb.Table("timetable_Div_D")
attendance_table = dynamodb.Table("AttendanceRecords")

COLLECTION_ID = "smart-campus-students-collection"


def lambda_handler(event, context):
    try:
        print("Raw event received:", event)

        # --- Support both direct Lambda invoke and API Gateway call ---
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event

        image_data = body.get("image", "")
        class_id = body.get("class_id", "").strip()
        subject = body.get("subject", "").strip()
        faculty_id = body.get("faculty_id", "").strip()

        if not image_data or not class_id or not subject or not faculty_id:
            return _response(400, {"error": "Missing required fields"})

        # --- Clean and decode base64 image ---
        if image_data.startswith("data:image"):
            image_data = re.sub("^data:image/[^;]+;base64,", "", image_data)

        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            print("Base64 decode failed:", str(e))
            return _response(400, {"error": "Invalid base64 image"})

        # --- Face Recognition using Rekognition ---
        try:
            rekog_response = rekognition.search_faces_by_image(
                CollectionId=COLLECTION_ID,
                Image={"Bytes": image_bytes},
                MaxFaces=1,
                FaceMatchThreshold=90
            )
        except Exception as e:
            print("AWS Rekognition error:", str(e))
            return _response(500, {"error": f"Rekognition error: {str(e)}"})

        matches = rekog_response.get("FaceMatches", [])
        if not matches:
            print(" No face match found")
            return _response(200, {"message": "Recognition failed", "match": False})

        top_match = matches[0]
        external_id = top_match["Face"]["ExternalImageId"]
        confidence = round(top_match["Similarity"], 2)

        # --- Extract student details from external ID ---
        if "_" in external_id:
            student_id, student_name = external_id.split("_", 1)
        else:
            student_id, student_name = external_id, "Unknown"

        print(f"Matched Student: {student_id} ({student_name}) with {confidence}% confidence")

        # --- Check if student is enrolled in class & subject ---
        try:
            response = timetable_table.scan(
                FilterExpression=Attr("class_id").eq(class_id) & Attr("subject").eq(subject)
            )
        except Exception as e:
            print("DynamoDB Scan error:", str(e))
            return _response(500, {"error": "Database read error"})

        items = response.get("Items", [])
        enrolled_ids = []

        for item in items:
            for s in item.get("students", []):
                if isinstance(s, str):
                    sid = s.split("_")[0].strip()
                elif isinstance(s, dict) and "S" in s:
                    sid = s["S"].split("_")[0].strip()
                else:
                    continue
                enrolled_ids.append(sid)

        enrolled_ids = list(set(enrolled_ids))
        print(f"Enrolled IDs for {class_id}-{subject}: {enrolled_ids}")

        eligible = student_id in enrolled_ids

        # --- Prepare attendance result ---
        result = {
            "StudentID": student_id,
            "StudentName": student_name,
            "Confidence": confidence,
            "Eligible": eligible,
            "message": "Marked Present" if eligible else "Recognized but not enrolled"
        }

        # --- Log result ---
        print("Result →", result)

        # --- Store attendance record if eligible ---
        if eligible:
            try:
                attendance_item = {
                    "StudentID": str(student_id),
                    "Timestamp": str(datetime.datetime.utcnow()),
                    "StudentName": student_name,
                    "ClassID": class_id,
                    "Subject": subject,
                    "FacultyID": faculty_id,
                    "Confidence": Decimal(str(confidence)),  
                    "Status": "Present"
                }

                print("Writing to AttendanceRecords:", attendance_item)
                attendance_table.put_item(Item=attendance_item)
                print(f"Successfully recorded attendance for {student_id}")

            except Exception as e:
                print(" DynamoDB Write Error:", str(e))

        else:
            print("Not enrolled — record not stored")

        return _response(200, result)

    except Exception as e:
        print("Unexpected Error:", str(e))
        return _response(500, {"error": str(e)})


def _response(status, body_dict):
    """Standard API Gateway JSON response"""
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body_dict)
    }
