import json
import os
import logging
import urllib.parse

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Read from environment variables
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
DYNAMO_TABLE = os.environ.get("DYNAMO_TABLE_NAME")

# Initialize boto3 client/resource
s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMO_TABLE)


def extract_s3_key_from_url(url: str) -> str:
    """
    Extract the key portion from a full S3 URL, for example:
    https://group7-birdtag-media-bucket.s3.us-east-1.amazonaws.com/Images/crows_1.jpg
    → "Images/crows_1.jpg"
    """
    parsed = urllib.parse.urlparse(url)
    # parsed.path = "/Images/crows_1.jpg", strip leading "/"
    key = parsed.path.lstrip("/")
    return key


def get_corresponding_thumbnail_key(key: str) -> str | None:
    """
    If the provided key starts with "Images/", the thumbnail is assumed to live under "Thumbnails/".
    Otherwise (Videos/ or Audios/), return None.
    """
    if key.startswith("Images/"):
        return key.replace("Images/", "Thumbnails/", 1)
    return None


def delete_s3_objects(bucket: str, keys: list[str]):
    """
    Batch-delete S3 objects. 'keys' is a list of object keys like "Images/crows_1.jpg".
    """
    if not keys:
        return

    delete_list = [{"Key": k} for k in keys]
    try:
        resp = s3_client.delete_objects(
            Bucket=bucket,
            Delete={"Objects": delete_list}
        )
        logger.info(f"[S3] delete_objects response: {resp}")
    except ClientError as e:
        logger.error(f"[S3] Failed to delete objects: {e}")
        raise


def delete_dynamo_item(file_url: str):
    """
    Delete the item from DynamoDB whose partition key 'file_id' matches the full URL.
    """
    try:
        table.delete_item(Key={"file_id": file_url})
        logger.info(f"[DynamoDB] Deleted item with file_id = {file_url}")
    except ClientError as e:
        logger.error(f"[DynamoDB] Failed to delete record (file_id={file_url}): {e}")
        raise


def lambda_handler(event, context):
    """
    Entry point for Lambda (using Lambda Proxy Integration in API Gateway).
    Expected request body format:
    {
      "urls": [
        "https://group7-birdtag-media-bucket.s3.us-east-1.amazonaws.com/Images/crows_1.jpg",
        "https://group7-birdtag-media-bucket.s3.us-east-1.amazonaws.com/Audios/city_bird_sound_black_bird_ZU0_YdN.wav",
        "https://group7-birdtag-media-bucket.s3.us-east-1.amazonaws.com/Videos/crows.mp4",
        "https://group7-birdtag-media-bucket.s3.us-east-1.amazonaws.com/Thumbnails/crows_2.jpg"
      ]
    }
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        body_str = event.get("body", "")
        if not body_str:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Request body is empty. Please provide a list of URLs."})
            }

        body = json.loads(body_str)
        urls = body.get("url", [])
        if not isinstance(urls, list) or len(urls) == 0:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Please provide a non-empty list of URLs."})
            }

        result = {"deleted": [], "failed": []}

        for url in urls:
            try:
                # 1) Extract the S3 key
                key = extract_s3_key_from_url(url)
                if not key:
                    raise ValueError(f"Cannot extract key from URL: {url}")

                # 2) If it's an image, attempt to delete its thumbnail as well
                thumb_key = get_corresponding_thumbnail_key(key)

                # 3) Delete the original file and thumbnail (if exists) from S3
                keys_to_delete = [key]
                if thumb_key:
                    keys_to_delete.append(thumb_key)
                delete_s3_objects(S3_BUCKET, keys_to_delete)

                # 4) Delete the record from DynamoDB (partition key is the full URL)
                delete_dynamo_item(url)

                result["deleted"].append(url)

            except Exception as e:
                logger.exception(f"Error during deletion: {url} → {e}")
                result["failed"].append({"url": url, "error": str(e)})

        # If everything succeeded, return 200; otherwise return 207 (Multi-Status)
        status_code = 200 if not result["failed"] else 207
        return {
            "statusCode": status_code,
            "body": json.dumps(result, ensure_ascii=False)
        }

    except Exception as e_all:
        logger.exception("Unhandled exception in lambda_handler")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal error. Deletion failed.",
                "error": str(e_all)
            }, ensure_ascii=False)
        }
