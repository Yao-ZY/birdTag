import json
import boto3
import logging
import os

# Set logging level from environment variable (default to INFO)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger()
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))


def lambda_handler(event, context):
    logger.info("Lambda started")

    # Extract 'species' parameter from query string
    try:
        species = event["queryStringParameters"]["species"].lower()  
        logger.info(f"Searching for species: {species}")
    except Exception as e:
        # Return error if 'species' parameter is missing or invalid
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing or invalid 'species' parameter"})
        }

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("BirdTagMediaIndex")

    # Scan entire table
    all_items = []
    response = table.scan()
    all_items.extend(response.get("Items", []))

    # Handle pagination (continue scanning if there are more items)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        all_items.extend(response.get("Items", []))

    matched = []

    # Filter items based on the presence of the species tag
    for item in all_items:
        tags = item.get("tags", {})
        lower_tags = {k.lower(): v for k, v in tags.items()}
        if species in lower_tags:  # Check if species tag exists
            matched.append(item["file_id"])  # file_id is a URL

    # Return matched URLs
    return {
        "statusCode": 200,
        "body": json.dumps({"links": matched})
    }
