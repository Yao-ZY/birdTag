import json
import boto3
import logging
import os

# Configure logging based on environment variable, default to INFO
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger()
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

def lambda_handler(event, context):
    logger.info("Lambda started")

    # Parse the request body
    try:
        print(event)
        body = json.loads(event["body"])
        tag_conditions = body.get("tags", {})
        logger.info(f"Received tags: {tag_conditions}")
    except Exception as e:
        logger.error(f"Failed to parse request body: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid request format"})
        }

    # Initialize DynamoDB connection and access the BirdTagMediaIndex table
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("BirdTagMediaIndex")

    # Scan the entire table
    all_items = []
    response = table.scan()
    all_items.extend(response.get("Items", []))
    matched_links = []

    # Continue scanning if there are more items (pagination)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        all_items.extend(response.get("Items", []))

    # Evaluate each item against provided tag conditions
    for item in all_items:
        tags = item.get("tags", {})
        logger.debug(f"Checking item: {item['file_id']} with tags: {tags}")

        match = True
        # Check if the item meets all tag conditions
        for tag, min_count in tag_conditions.items():
            if tag not in tags or int(tags[tag]) < min_count:
                match = False
                break
        if match:
            matched_links.append(item["file_id"])  # file_id is an S3 URLL

    logger.info(f"Final response: {matched_links}")

    # Return matched file URLs
    return {
        "statusCode": 200,
        "body": json.dumps({"links": matched_links})
    }
