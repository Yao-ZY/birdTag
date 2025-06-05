import json
import boto3
from decimal import Decimal

# Initialize DynamoDB resource and reference the table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdTagMediaIndex')

# Custom converter to handle Decimal values in DynamoDB (for JSON serialization)
def default_converter(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError(f"Object of type {type(o)} is not JSON serializable")

def lambda_handler(event, context):
    try:
        items = []
        # Initial scan of the table (returns up to 1MB of data)
        response = table.scan()
        items.extend(response.get('Items', []))

        # Continue scanning if more data exists (pagination)
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        # Extract and reformat only the needed fields from each item
        cleaned_items = []
        for item in items:
            cleaned_items.append({
                "file_id": item.get("file_id"),
                "file_type": item.get("file_type"),
                "tags": item.get("tags")
            })

        # Return HTTP 200 with the cleaned data
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps(cleaned_items, default=default_converter)
        }

    except Exception as e:
        # Return HTTP 500 if an error occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
