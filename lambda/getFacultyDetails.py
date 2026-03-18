import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Faculty')  # ✅ Replace with your actual Faculty table name

def lambda_handler(event, context):
    try:
        # ✅ Extract query params properly
        params = event.get("queryStringParameters") or {}
        faculty_id = params.get("faculty_id")

        if not faculty_id:
            return response(400, {"error": "Missing faculty_id"})

        # ✅ Fetch faculty record from DynamoDB
        result = table.get_item(Key={"faculty_id": faculty_id})

        if "Item" not in result:
            return response(404, {"error": f"Faculty ID {faculty_id} not found"})

        item = result["Item"]

        # ✅ Return the relevant faculty details
        return response(200, {
            "faculty_id": item.get("faculty_id"),
            "name": item.get("name"),
            "class_id": item.get("class_id"),
            "subject": item.get("subject")
        })

    except Exception as e:
        # ✅ Handle unexpected errors
        return response(500, {"error": str(e)})


def response(status, body):
    """Helper function for API Gateway–friendly responses"""
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization"
        },
        "body": json.dumps(body)
    }
