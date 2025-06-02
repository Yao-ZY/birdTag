# Import libraries
import logging
import os
from collections import Counter
from urllib.parse import unquote_plus

import boto3
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from botocore.exceptions import ClientError

# Set up writable directory for Numba cache
os.environ["NUMBA_CACHE_DIR"] = "/tmp/numba_cache"
os.makedirs("/tmp/numba_cache", exist_ok=True)

# Initialize AWS service clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdTagMediaIndex')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define function to analyze a local audio file and predict bird species
def audio_prediction(audio_path, min_conf=0.5):
    """
    Analyze an audio file using BirdNET to detect bird species.

    Args:
        audio_path (str): Local path to the audio file.
        min_conf (float): Minimum confidence score for prediction.

    Returns:
        list: A list of predicted bird species (common names).
    """
    try:
        # Path to TFLite model
        model_path = "./BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite"
        # Path to label list
        label_path = "./BirdNET_GLOBAL_6K_V2.4_Labels.txt"

        # Initialize BirdNET analyzer
        analyzer = Analyzer(classifier_model_path=model_path,
                            classifier_labels_path=label_path)

        # Create recording object
        recording = Recording(analyzer, audio_path, min_conf=min_conf)
        # Run the model
        recording.analyze()

        # Extract bird names
        labels = [det["common_name"] for det in recording.detections]
        # Return label list
        return labels

    except Exception as e:
        # Log error
        logger.error(f"Audio prediction failed: {e}")
        # Return empty list on failure
        return []


# Define AWS Lambda entry point function
def handler(event, context):
    """
    AWS Lambda handler to process audio files uploaded to S3.
    Downloads the audio, predicts bird species, and logs results in DynamoDB.
    """
    # Loop over S3 records
    for record in event.get("Records", []):
        bucket_name = record['s3']['bucket']['name']
        object_key = unquote_plus(record['s3']['object']['key'])

        # Log received event
        logger.info(f"Received new S3 object: {bucket_name}/{object_key}")

        # Define local file path in /tmp
        local_path = f"/tmp/{os.path.basename(object_key)}"

        try:
            # Download audio file from S3
            s3.download_file(bucket_name, object_key, local_path)
            # Log success
            logger.info(f"Downloaded audio to {local_path}")
        except ClientError as e:
            # Log S3 error
            logger.error(f"Failed to download file: {e}")
            continue

        # Initialize list of predictions
        predictions = []
        # File type
        file_type = ""

        # Check if file is an audio file
        if object_key.startswith("Audios/"):
            # Set file type
            file_type = "audio"
            try:
                # Run BirdNET prediction
                predictions = audio_prediction(local_path)
            except Exception as e:
                # Log error if prediction fails
                logger.warning(f"Audio analysis failed: {e}")
                # Fallback to empty result
                predictions = []

        # Count each species frequency
        tag_summary = dict(Counter(predictions))
        # Build public S3 URL
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

        try:
            # Save result to DynamoDB
            table.put_item(Item={
                'file_id': file_url,
                'file_type': file_type,
                'tags': tag_summary
            })
            # Log success
            logger.info(f"Stored result in DynamoDB for: {object_key}")
        except ClientError as e:
            # Log write failure
            logger.error(f"Failed to write to DynamoDB: {e}")
