import json
import boto3
import urllib.parse
import logging  

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Connect to DynamoDB table named "BirdTagMediaIndex"
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdTagMediaIndex')

# Helper function to extract file_id from URL (currently just returns URL directly)
def extract_file_id(url):
    return url

def lambda_handler(event, context):
    try:
        # Log the incoming event for debugging
        logger.info(f"Received event: {event}")

        # Parse JSON body from API Gateway
        body = json.loads(event.get('body', '{}'))
        logger.info(f"Parsed body: {body}")

        urls = body.get('url', [])                      # List of file_ids to update
        operation = int(body.get('operation', 1))       # Operation: 1 = add/update, 0 = remove
        tag_pairs = body.get('tags', [])                # e.g., ["Crow,5", "Pigeon,2"]
        logger.info(f"URLs: {urls}, operation: {operation}, tag_pairs: {tag_pairs}")
        
        # Convert tag strings into tuples e.g., ["Crow,5"] -> [("Crow", "5")]
        tags_to_update = [tuple(t.split(",", 1)) for t in tag_pairs]
        logger.info(f"tags_to_update: {tags_to_update}")

        # Update DynamoDB entries per URL
        for url in urls:
            file_id = extract_file_id(url)
            logger.info(f"Processing file_id: {file_id}")

            if operation == 1:
               # Prepare partial update for adding/updating tags
                update_expr_parts = []
                expr_names = {"#tags": "tags"}      
                expr_vals = {}

                for idx, (tag, val_str) in enumerate(tags_to_update):
                    placeholder_name = f"#tg{idx}"   # e.g. "#tg0"
                    placeholder_val  = f":v{idx}"    # e.g. ":v0"

                    update_expr_parts.append(f"#tags.{placeholder_name} = {placeholder_val}")
                    expr_names[placeholder_name] = tag   # "#tg0" -> "Crow"
                    expr_vals[placeholder_val] = int(val_str)  # ":v0" -> 5

                update_expression = "SET " + ", ".join(update_expr_parts)
                logger.info(f"UpdateExpression (ADD/UPDATE): {update_expression}")
                logger.info(f"ExpressionAttributeNames: {expr_names}")
                logger.info(f"ExpressionAttributeValues: {expr_vals}")

                # Perform the update
                table.update_item(
                    Key={'file_id': file_id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expr_names,
                    ExpressionAttributeValues=expr_vals
                )
                logger.info(f"Added/Updated tags for {file_id}")

            # operation == 0, remove specified tags from map
            else:  
                remove_expr_parts = []
                expr_names = {"#tags": "tags"}

                for idx, (tag, _) in enumerate(tags_to_update):
                    placeholder_name = f"#tg{idx}"    # e.g. "#tg0"
                    remove_expr_parts.append(f"#tags.{placeholder_name}")
                    expr_names[placeholder_name] = tag  # "#tg0" -> "Crow"

                update_expression = "REMOVE " + ", ".join(remove_expr_parts)
                logger.info(f"UpdateExpression (REMOVE): {update_expression}")
                logger.info(f"ExpressionAttributeNames: {expr_names}")

                # Perform the removal
                table.update_item(
                    Key={'file_id': file_id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expr_names
                )
                logger.info(f"Removed tags from {file_id}")

        # Successful response
        logger.info("Done updating tags.")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Tags updated successfully'})
        }

    except Exception as e:
        # Log error with stack trace and return 500
        logger.error("Error during tag update", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
