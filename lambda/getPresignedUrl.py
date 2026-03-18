import json
import boto3
import os
import time

s3 = boto3.client('s3')
BUCKET_NAME = 'smart-campus-students'

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        file_name = body.get("fileName", f"frame_{int(time.time())}.jpg")
        content_type = body.get("contentType", "image/jpeg")

        # Object key inside S3
        s3_key = f"session-captures/{file_name}"

        # Generate presigned URL valid for 5 minutes
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key, 'ContentType': content_type},
            ExpiresIn=120
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "uploadUrl": presigned_url,
                "s3Key": s3_key
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
