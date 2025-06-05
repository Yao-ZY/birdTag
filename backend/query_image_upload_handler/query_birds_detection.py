# Import libraries
import logging
import os
from collections import Counter
from urllib.parse import unquote_plus

import boto3
import cv2 as cv
import supervision as sv
from botocore.exceptions import ClientError
from ultralytics import YOLO
import base64
from datetime import datetime

# Initialize S3 and DynamoDB clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdTagMediaIndex')

# Set up the logger to log at the INFO level
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Function: Predict bird species in an image
def image_prediction(image_path, confidence=0.5, model="./model.pt"):
    """
    Run bird detection on an image using a YOLO model.

    Args:
        image_path (str): Path to the image file.
        confidence (float): Minimum confidence threshold for detection.
        model (str): Path to the model file.

    Returns:
        list: List of detected bird class names.
    """
    # Load the YOLO model
    model = YOLO(model)
    # Dictionary of class ID to bird names
    class_dict = model.names
    # Load the image from local path
    img = cv.imread(image_path)

    # If image loading failed
    if img is None:
        print("Failed to load image.")
        return []

    # Run prediction, get first output
    result = model(img)[0]
    # Convert to supervision format
    detections = sv.Detections.from_ultralytics(result)

    # If any detections exist
    if detections.class_id is not None:
        # Filter by confidence
        detections = detections[(detections.confidence > confidence)]
        # Map IDs to names
        labels = [f"{class_dict[cls_id]}" for cls_id in detections.class_id]
        # Return list of bird names
        return labels
    # Return empty if no detections
    return []


# Function: Predict bird species in a video
def video_prediction(video_path, confidence=0.5, model="./model.pt"):
    """
    Run bird detection on a video using YOLO and ByteTrack.

    Args:
        video_path (str): Path to the video file.
        confidence (float): Confidence threshold for predictions.
        model (str): Path to the YOLO model.

    Returns:
        list: List of bird species detected across video frames.
    """
    try:
        # Extract video info
        video_info = sv.VideoInfo.from_video_path(video_path=video_path)
        # Extract frames per second
        fps = int(video_info.fps)
        # Load YOLO model
        model = YOLO(model)
        # Initialize tracker for object tracking
        tracker = sv.ByteTrack(frame_rate=fps)
        # Get bird name dictionary
        class_dict = model.names

        # Open video file
        cap = cv.VideoCapture(video_path)
        # Check if opened successfully
        if not cap.isOpened():
            raise Exception("Failed to open video.")

        # List to collect detected labels
        labels = []
        # Process the video frame by frame
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: 
                break

            # Run YOLO on current frame
            result = model(frame)[0]
            # Parse results
            detections = sv.Detections.from_ultralytics(result)
            # Apply tracking
            detections = tracker.update_with_detections(detections)

            # Filter detections based on confidence
            if detections.tracker_id is not None:
                detections = detections[detections.confidence > confidence]
                labels += [
                    class_dict[cls_id] for cls_id in detections.class_id
                ]

        # Return all detected bird names
        return labels

    except Exception as e:
        print(f"Video prediction failed: {e}")  # Log failure
        return []

    finally:
        cap.release()
        print("Released video resources.")


# Lambda handler function
def handler(event, context):
    logger.info(f"Received event: {event}")

    body = event.get("body")
    if isinstance(body, str):
        import json
        body = json.loads(body)
    logger.info(f"Parsed body: {body}")

    file_base64 = body.get("file_bytes")
    file_type = body.get("file_type")

    if not file_base64:
        logger.error("Missing file_bytes")
        return {"statusCode": 400, "body": "Missing file_bytes"}

    try:
        file_bytes = base64.b64decode(file_base64)
        file_name = datetime.now().strftime("%Y%m%d_%H%M%S") + file_type
        local_path = f"/tmp/{file_name}"
        logger.info(f"Saving file to: {local_path}")

        with open(local_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"Saved file: {file_name} ({len(file_bytes)} bytes)")

        tags = []
        file_type = file_type.lower()

        image_exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        video_exts = [".mp4", ".mov", ".avi", ".mkv", ".webm"]

        if file_type in image_exts:
            try:
                logger.info("Processing as image")
                tags = image_prediction(local_path)
                logger.info(f"Image tags: {tags}")
            except Exception as e:
                logger.warning(f"Image processing failed: {e}")
                tags = []
        elif file_type in video_exts:
            try:
                logger.info("Processing as video")
                tags = video_prediction(local_path)
                logger.info(f"Video tags: {tags}")
            except Exception as e:
                logger.warning(f"Video processing failed: {e}")
                tags = []
        else:
            logger.warning(f"Unsupported file_type: {file_type}")
            return {"statusCode": 400, "body": f"Unsupported file type: {file_type}"}

        tag_summary = dict(Counter(tags))
        logger.info(f"Final tag summary: {tag_summary}")

        return {
            "statusCode": 200,
            "body": json.dumps(tag_summary)
        }

    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
