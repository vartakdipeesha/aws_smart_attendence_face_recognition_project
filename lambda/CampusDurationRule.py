import boto3
from datetime import datetime

# DynamoDB connections
dynamodb = boto3.resource('dynamodb')
daily_present_table = dynamodb.Table('DailyPresent')
attendance_table = dynamodb.Table('AttendanceLogs')

# Demo thresholds
MIN_DURATION_MINUTES = 4
MIN_SNAPSHOTS = 2

def fetch_snapshots(sap_id, date_today):
    """
    Fetch all snapshots for a student on a specific date.
    Partition key = SAP_ID
    Sort key = Date (or SAP_IDClass)
    """
    response = daily_present_table.query(
        KeyConditionExpression="SAP_ID = :sap AND begins_with(#d, :dt)",
        ExpressionAttributeNames={
            "#d": "Date"  # Date is reserved keyword
        },
        ExpressionAttributeValues={
            ":sap": sap_id,
            ":dt": date_today
        }
    )
    return response.get('Items', [])

def group_by_class(snapshots):
    class_snapshots = {}
    for snap in snapshots:
        class_id = snap['Class_ID']
        class_snapshots.setdefault(class_id, []).append(snap['Timestamp'])
    return class_snapshots

def evaluate_attendance(class_snapshots, sap_id, date_today):
    for class_id, times in class_snapshots.items():
        times_sorted = sorted([datetime.fromisoformat(t) for t in times])
        duration = (times_sorted[-1] - times_sorted[0]).total_seconds() / 60
        snapshot_count = len(times_sorted)
        present = duration >= MIN_DURATION_MINUTES and snapshot_count >= MIN_SNAPSHOTS

        attendance_table.put_item(
            Item={
                'Date': date_today,
                'SAP_IDClass': f"{sap_id}#{class_id}",
                'Present': present,
                'SnapshotCount': snapshot_count,
                'Duration': duration
            }
        )

def lambda_handler(event, context):
    sap_id = event['SAP_ID']
    date_today = event['date']  # 'YYYY-MM-DD'

    snapshots = fetch_snapshots(sap_id, date_today)
    class_snapshots = group_by_class(snapshots)
    evaluate_attendance(class_snapshots, sap_id, date_today)

    return {"status": "success"}
