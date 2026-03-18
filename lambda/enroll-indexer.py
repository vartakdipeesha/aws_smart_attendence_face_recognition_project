# import os, json, boto3
# rek = boto3.client("rekognition")

# def extract_sap_from_key(key: str) -> str:
#     file = key.split("/")[-1]
#     sap = file.split("_")[0].split(".")[0].strip()
#     if not sap.isdigit():
#         raise ValueError(f"Cannot parse SAP from {key}")
#     return sap

# def lambda_handler(event, _):
#     records = []
#     for r in event.get("Records", []):
#         body = json.loads(r["body"]) if "body" in r else r
#         records.extend(body.get("Records", []))
#     for rec in records:
#         b = rec["s3"]["bucket"]["name"]
#         k = rec["s3"]["object"]["key"]
#         if not k.lower().startswith("enroll/"):
#             continue
#         sap = extract_sap_from_key(k)
#         rek.index_faces(CollectionId=os.getenv("COLLECTION_ID","attendance-prod"),
#                         Image={"S3Object":{"Bucket": b, "Name": k}},
#                         ExternalImageId=sap, DetectionAttributes=[])
#     return {"ok": True}



import boto3

rekognition = boto3.client('rekognition', region_name='ap-south-1')
s3 = boto3.client('s3')

# ---- Configuration ----
BUCKET = 'smart-campus-students'
PREFIX = 'enroll/'
COLLECTION = 'smart-campus-students-collection' 

def lambda_handler(event, context):
    try:
        
        try:
            rekognition.create_collection(CollectionId=COLLECTION)
            print(f"Created collection: {COLLECTION}")
        except rekognition.exceptions.ResourceAlreadyExistsException:
            print(f"Collection already exists: {COLLECTION}")

        # List all images in enroll/ folder
        response = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)

        if 'Contents' not in response:
            print("No student images found in S3.")
            return {
                "statusCode": 404,
                "body": "No student images found."
            }

        indexed = 0
        skipped = 0

        for obj in response['Contents']:
            key = obj['Key']
            if not key.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            external_id = key.split('/')[-1].split('.')[0] 
            print(f"Indexing: {external_id}")

            try:
                rekognition.index_faces(
                    CollectionId=COLLECTION,
                    Image={'S3Object': {'Bucket': BUCKET, 'Name': key}},
                    ExternalImageId=external_id,
                    DetectionAttributes=['DEFAULT']
                )
                indexed += 1
            except Exception as e:
                print(f"Failed to index {key}: {e}")
                skipped += 1

        result = f"Indexed {indexed} faces,  Skipped {skipped}."
        print(result)

        return {
            "statusCode": 200,
            "body": result
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
