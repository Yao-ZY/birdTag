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


# Function: Generate a thumbnail from an image
def create_thumbnail(image_path, size=(150, 150)):
    """
    Create a thumbnail image from the original image.

    Args:
        image_path (str): Path to the source image.
        size (tuple): Thumbnail dimensions (width, height).

    Returns:
        bytes: Encoded thumbnail image in bytes, or None if failed.
    """
    try:
        # Get file extension
        ext = os.path.splitext(image_path)[-1]
        # Load image
        image = cv.imread(image_path)
        if image is None:
            logger.warning("Failed to load image for thumbnail.")
            return None

        # Resize image to thumbnail size
        resized = cv.resize(image, size)
        # Encode image as binary
        success, encoded = cv.imencode(ext, resized)

        if not success:
            logger.warning("Image encoding failed.")
            return None

        return encoded.tobytes()

    except Exception as e:
        logger.error(f"Thumbnail creation failed: {e}")
        return None


# Lambda handler function
def handler(event, context):
    """
    Lambda function handler to process uploaded media files (images/videos),
    perform detection, optionally generate thumbnails, and store metadata in DynamoDB.
    """
    # Loop over S3 trigger records
    for record in event.get('Records', []):
        # Extract bucket name
        bucket_name = record['s3']['bucket']['name']
        # Decode key
        object_key = unquote_plus(record['s3']['object']['key'])

        logger.info(f"Processing file from S3: {bucket_name}/{object_key}")
        # Temporary download path
        local_path = f"/tmp/{os.path.basename(object_key)}"

        try:
            # Download file from S3
            s3.download_file(bucket_name, object_key, local_path)
            logger.info(f"Downloaded file to: {local_path}")
        except ClientError as e:
            logger.error(f"Download failed: {e}")
            continue

        # List of detected tags
        tags = []
        # 'image' or 'video'
        file_type = ""

        # Handle image files
        if object_key.startswith("Images/"):
            file_type = "image"
            try:
                # Predict bird species
                tags = image_prediction(local_path)
                # Create thumbnail
                thumbnail_bytes = create_thumbnail(local_path)

                if thumbnail_bytes:
                    # Define thumbnail key
                    thumb_key = object_key.replace("Images/", "Thumbnails/")
                    # Upload thumbnail to S3
                    s3.put_object(Bucket=bucket_name,
                                  Key=thumb_key,
                                  Body=thumbnail_bytes,
                                  ContentType="image/jpeg")
                    logger.info(f"Thumbnail uploaded: {thumb_key}")
            except Exception as e:
                logger.warning(f"Image processing failed: {e}")
                tags = []
        # Handle video files
        elif object_key.startswith("Videos/"):
            file_type = "video"
            try:
                # Predict from video
                tags = video_prediction(local_path)
            except Exception as e:
                logger.warning(f"Video processing failed: {e}")
                tags = []

        # Count each bird species
        tag_summary = dict(Counter(tags))
        # Construct public file URL
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

        # Insert metadata into DynamoDB
        try:
            table.put_item(Item={
                'file_id': file_url,
                'file_type': file_type,
                'tags': tag_summary
            })
            logger.info(f"DynamoDB record inserted for {object_key}")
        except ClientError as e:
            logger.error(f"Failed to write to DynamoDB: {e}")


# Local test block
if __name__ == '__main__':
    print("predicting...")
    # image_prediction("./test_images/crows_1.jpg", result_filename="crows_result1.jpg")
    # image_prediction("./test_images/crows_3.jpg", result_filename='crows_detected_2.jpg')
    # image_prediction("./test_images/kingfisher_2.jpg",result_filename='kingfishers_detected.jpg' )
    # image_prediction("./test_images/myna_1.jpg",result_filename='myna_detected.jpg')
    # image_prediction("./test_images/owl_2.jpg",result_filename='owls_detected.jpg')
    # image_prediction("./test_images/peacocks_3.jpg",result_filename='peacocks_detected_1.jpg')
    # image_prediction('./test_images/sparrow_3.jpg',result_filename='sparrow_detected_1.jpg')
    # image_prediction('./test_images/sparrow_1.jpg',result_filename='sparrow_detected_2.jpg')

    # uncomment to test video prediction
    # video_prediction("./test_videos/crows.mp4")
    # video_prediction("./test_videos/kingfisher.mp4",result_filename='kingfisher_detected.mp4')
