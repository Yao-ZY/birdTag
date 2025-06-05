import json
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    try:
        thumb_url = unquote_plus(event["queryStringParameters"]["thumb"])
        full_url = thumb_url.replace("Thumbnails/", "Images/")
        return {
            "statusCode": 200,
            "body": json.dumps({"full_url": full_url})
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
