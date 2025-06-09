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

    print(f"event['body']: {event.get('body')}")

    # Parse the request body
    try:
        print(event)
        body = json.loads(event["body"])
        if "tags" in body:
            tag_conditions = body["tags"]
        else:
            tag_conditions = body
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
        print(f"[DEBUG] tags: {tags}")
        logger.debug(f"Checking item: {item['file_id']} with tags: {tags}")

        match = True
        for tag, min_count in tag_conditions.items():
            # If the tag is not present in the item's tags, or the value is insufficient, mark as no match
            if tag not in tags:
                match = False
                break
            try:
                # Handle Decimal or DynamoDB number types
                tag_value = tags[tag]
                if isinstance(tag_value, dict) and "N" in tag_value:
                    tag_value = int(tag_value["N"])
                else:
                    tag_value = int(tag_value)
                if tag_value < min_count:
                    match = False
                    break
            except Exception as e:
                logger.warning(f"Tag value error for {tag}: {tags.get(tag)} - {e}")
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
