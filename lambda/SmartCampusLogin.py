# import boto3
# import json

# # Initialize DynamoDB
# ddb = boto3.resource('dynamodb', region_name='ap-south-1')
# faculty_table = ddb.Table('Faculty')
# student_table = ddb.Table('students')  # change if needed

# def lambda_handler(event, context):
#     # Parse body safely
#     if 'body' in event and event['body']:
#         try:
#             body = json.loads(event['body'])
#         except Exception:
#             body = {}
#     else:
#         body = event

#     role = body.get('role')
#     password = body.get('password')

#     # CORS + JSON headers
#     headers = {
#         "Access-Control-Allow-Origin": "*",
#         "Access-Control-Allow-Headers": "Content-Type,Authorization",
#         "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
#         "Content-Type": "application/json"
#     }

#     if not role or not password:
#         return {
#             "statusCode": 400,
#             "headers": headers,
#             "body": json.dumps({"error": "Missing role or password"})
#         }

 
#     # FACULTY LOGIN

#     if role == "faculty":
#         faculty_id = body.get('faculty_id')
#         if not faculty_id:
#             return {
#                 "statusCode": 400,
#                 "headers": headers,
#                 "body": json.dumps({"error": "Missing faculty_id"})
#             }

#         try:
#             response = faculty_table.get_item(Key={'faculty_id': faculty_id})
#             item = response.get('Item')

#             if not item or item.get('password') != password:
#                 return {
#                     "statusCode": 401,
#                     "headers": headers,
#                     "body": json.dumps({"error": "Invalid faculty credentials"})
#                 }

#             return {
#                 "statusCode": 200,
#                 "headers": headers,
#                 "body": json.dumps({
#                     "role": "faculty",
#                     "faculty_id": item['faculty_id'],
#                     "name": item.get('name', 'Unknown'),
#                     "class_id": item.get('class_id', ''),
#                     "subject": item.get('subject', ''),
#                     "message": "Faculty login successful"
#                 })
#             }

#         except Exception as e:
#             print("Faculty lookup error:", e)
#             return {
#                 "statusCode": 500,
#                 "headers": headers,
#                 "body": json.dumps({"error": str(e)})
#             }


#     # STUDENT LOGIN
  
#     elif role == "student":
#         sap_id = body.get('SAP_ID')
#         if not sap_id:
#             return {
#                 "statusCode": 400,
#                 "headers": headers,
#                 "body": json.dumps({"error": "Missing SAP_ID"})
#             }

#         try:
#             response = student_table.get_item(Key={'SAP_ID': sap_id})
#             item = response.get('Item')

#             if not item or item.get('password') != password:
#                 return {
#                     "statusCode": 401,
#                     "headers": headers,
#                     "body": json.dumps({"error": "Invalid student credentials"})
#                 }

#             return {
#                 "statusCode": 200,
#                 "headers": headers,
#                 "body": json.dumps({
#                     "role": "student",
#                     "SAP_ID": item['SAP_ID'],
#                     "name": item.get('name', 'Unknown'),
#                     "stream": item.get('stream', ''),
#                     "message": "Student login successful"
#                 })
#             }

#         except Exception as e:
#             print("Student lookup error:", e)
#             return {
#                 "statusCode": 500,
#                 "headers": headers,
#                 "body": json.dumps({"error": str(e)})
#             }

   
#     else:
#         return {
#             "statusCode": 400,
#             "headers": headers,
#             "body": json.dumps({"error": "Invalid role"})
#         }








import json
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
faculty_table = dynamodb.Table('Faculty')
student_table = dynamodb.Table('students')

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Content-Type": "application/json"
    }

    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": json.dumps({"message": "CORS OK"})}

    try:
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)
        elif body is None:
            body = event

        role = (body.get("role") or "").lower()
        password = body.get("password")

        if not role or not password:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"success": False, "message": "Missing role or password"})
            }

        # ---------- Faculty Login ----------
        if role == "faculty":
            faculty_id = body.get("faculty_id")
            if not faculty_id:
                return {
                    "statusCode": 400,
                    "headers": headers,
                    "body": json.dumps({"success": False, "message": "Missing faculty_id"})
                }

            response = faculty_table.get_item(Key={'faculty_id': faculty_id})
            item = response.get("Item")

            if not item or item.get("password") != password:
                return {
                    "statusCode": 401,
                    "headers": headers,
                    "body": json.dumps({"success": False, "message": "Invalid faculty credentials"})
                }

            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "success": True,
                    "role": "faculty",
                    "user": {
                        "faculty_id": item["faculty_id"],
                        "name": item.get("name", "Unknown"),
                        "class_id": item.get("class_id", ""),
                        "subject": item.get("subject", "")
                    },
                    "message": "Faculty login successful"
                })
            }

        # ---------- Student Login ----------
        elif role == "student":
            sap_id = body.get("SAP_ID")
            if not sap_id:
                return {
                    "statusCode": 400,
                    "headers": headers,
                    "body": json.dumps({"success": False, "message": "Missing SAP_ID"})
                }

            response = student_table.get_item(Key={'SAP_ID': sap_id})
            item = response.get("Item")

            if not item or item.get("password") != password:
                return {
                    "statusCode": 401,
                    "headers": headers,
                    "body": json.dumps({"success": False, "message": "Invalid student credentials"})
                }

            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "success": True,
                    "role": "student",
                    "user": {
                        "SAP_ID": item["SAP_ID"],
                        "name": item.get("Name", item.get("name", "Unknown")),
                        "image_key": item.get("ImageKey", ""),
                        "stream": item.get("stream", "")
                    },
                    "message": "Student login successful"
                })
            }

        else:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"success": False, "message": "Invalid role"})
            }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"success": False, "message": f"Server error: {str(e)}"})
        }
