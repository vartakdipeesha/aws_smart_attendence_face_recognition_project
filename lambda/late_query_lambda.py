import boto3, json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('StudentQueries')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    item = {
        'SAP_ID': body['sap_id'],
        'Timestamp': body['timestamp'],
        'Name': body['name'],
        'Reason': body['reason'],
        'Status': 'Pending'
    }
    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'success': True, 'message': 'Query stored successfully'})
    }
