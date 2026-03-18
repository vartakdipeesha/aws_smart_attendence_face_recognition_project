import boto3
import json
from decimal import Decimal

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('timetable_Div_D')

# --- Helper to convert Decimal types to float or str ---
def decimal_default(obj):
    if isinstance(obj, Decimal):
        # Convert safely (if integer or decimal)
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        # Default division = D
        division = event.get('division', 'D')

        # Scan all timetable records
        response = table.scan()
        items = response.get('Items', [])

        # Optional: filter by day if passed
        day = event.get('day')
        if day:
            items = [i for i in items if i.get('day') == day]

        # Return JSON response with Decimal-safe serialization
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'division': division,
                'count': len(items),
                'timetable': items
            }, default=decimal_default)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
