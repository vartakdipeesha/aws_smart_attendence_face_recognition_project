import boto3
import json

def lambda_handler(event, context):
    ddb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = ddb.Table('students')
    
    try:
        response = table.scan()  # fetch all students
        data = response.get('Items', [])
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': json.dumps(data)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
