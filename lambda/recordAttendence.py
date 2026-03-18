import json
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
attendance_table = dynamodb.Table("AttendanceRecords")

def lambda_handler(event, context):
    try:
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event

        SAP_ID = body.get("SAP_ID")
        Subject = body.get("Subject")
        Class_ID = body.get("Class_ID")
        Faculty_ID = body.get("Faculty_ID")
        Confidence = body.get("Confidence", 0)
        Time = body.get("Time", datetime.utcnow().isoformat())

        if not all([SAP_ID, Subject, Class_ID, Faculty_ID]):
            return _response(400, {"error": "Missing required fields"})

        
        existing = attendance_table.query(
            KeyConditionExpression=Key("StudentID").eq(str(SAP_ID)),
            FilterExpression=Attr("ClassID").eq(Class_ID) & Attr("Subject").eq(Subject)
        )

        if existing.get("Count", 0) > 0:
            return _response(200, {"message": "Already marked Present"})

        
        attendance_table.put_item(
            Item={
                "StudentID": str(SAP_ID),
                "ClassID": Class_ID,
                "Subject": Subject,
                "FacultyID": Faculty_ID,
                "Timestamp": Time,
                "Status": "Present",
                "Confidence": float(Confidence),
            }
        )

        return _response(200, {"message": "Attendance recorded successfully"})

    except Exception as e:
        print("Error:", str(e))
        return _response(500, {"error": str(e)})


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            "Access-Control-Allow-Headers": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }
