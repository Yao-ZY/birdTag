#!/usr/bin/env python
# coding: utf-8

# requirements
# !pip install ultralytics supervision

from ultralytics import YOLO
import supervision as sv
import cv2 as cv
import boto3
from botocore.exceptions import ClientError
import logging
from urllib.parse import unquote_plus
from collections import Counter
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdTagMediaIndex')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def image_prediction(image_path, confidence=0.5, model="./model.pt"):
    """
    """

    # Load YOLO model
    model = YOLO(model)
    class_dict = model.names

    # Load image from local path
    img = cv.imread(image_path)

    # Check if image was loaded successfully
    if img is None:
        print("Couldn't load the image! Please check the image path.")
        return

    # Run the model on the image
    result = model(img)[0]

    # Convert YOLO result to Detections format
    detections = sv.Detections.from_ultralytics(result)

    # Filter detections based on confidence threshold and check if any exist
    if detections.class_id is not None:
        detections = detections[(detections.confidence > confidence)]

        # Create labels for the detected objects
        labels = [f"{class_dict[cls_id]}" for cls_id in detections.class_id]
        return labels

# ## Video Detection
def video_prediction(video_path, confidence=0.5, model="./model.pt"):
    """
    """
    try:
        # Load video info and extract width, height, and frames per second (fps)
        video_info = sv.VideoInfo.from_video_path(video_path=video_path)
        fps = int(video_info.fps)

        model = YOLO(model)  # Load your custom-trained YOLO model
        tracker = sv.ByteTrack(frame_rate=fps)  # Initialize the tracker with the video's frame rate
        class_dict = model.names  # Get the class labels from the model

        # Capture the video from the given path
        cap = cv.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Error: couldn't open the video!")

        labels = []
        # Process the video frame by frame
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:  # End of the video
                break

            # Make predictions on the current frame using the YOLO model
            result = model(frame)[0]
            detections = sv.Detections.from_ultralytics(result)  # Convert model output to Detections format
            detections = tracker.update_with_detections(detections=detections)  # Track detected objects

            # Filter detections based on confidence
            if detections.tracker_id is not None:
                detections = detections[(detections.confidence > confidence)]  # Keep detections with confidence greater than a threashold
                # labels_1 = [f"{class_dict[cls_id]}" for cls_id in detections.class_id]
                for cls_id in detections.class_id:
                    labels.append(class_dict[cls_id])
        return labels
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Release resources
        cap.release()
        # if result_filename:
        #     out.release()
        print("Video processing complete, Released resources.")

def create_thumbnail(image_path, size=(150, 150)):
    """
    Resize the input image to a thumbnail with specified dimensions.
    
    Args:
        image_path (str): Local path to the image file.
        size (tuple): (width, height) of the thumbnail. Default is (150, 150).
    
    Returns:
        bytes: Encoded thumbnail image in original format, or None if failed.
    """
    try:
        ext = os.path.splitext(image_path)[-1]  
        image = cv.imread(image_path)
        if image is None:
            logger.warning("Unable to load image for thumbnail creation.")
            return None
        resized = cv.resize(image, size)
        success, encoded = cv.imencode(ext, resized)
        if not success:
            logger.warning("Failed to encode thumbnail.")
            return None
        return encoded.tobytes()
    except Exception as e:
        logger.error(f"Thumbnail creation failed: {e}")
        return None
    
def handler(event, context):
    """
    """

    for record in event.get('Records', []):
        bucket_name = record['s3']['bucket']['name']
        object_key = unquote_plus(record['s3']['object']['key'])

        logger.info(f"New object in bucket '{bucket_name}': {object_key}")

        local_path = f"/tmp/{os.path.basename(object_key)}"
        try:
            s3.download_file(bucket_name, object_key, local_path)
            logger.info(f"Downloaded to {local_path}")
        except ClientError as e:
            logger.error(f"Download failed: {e}")
            continue

        tags = []
        file_type = ""
        if object_key.startswith("Images/"):
            file_type = "image"
            try:
                tags = image_prediction(local_path) 
                # create and upload thumbnail
                thumbnail_bytes = create_thumbnail(local_path)
                if thumbnail_bytes:
                    thumb_key = object_key.replace("Images/", "Thumbnails/")
                    s3.put_object(
                        Bucket=bucket_name,
                        Key=thumb_key,
                        Body=thumbnail_bytes,
                        ContentType="image/jpeg"  
                    ) 
            except Exception as e:
                logger.warning(f"Image analysis failed: {e}")
                tags = []
        elif object_key.startswith("Videos/"):
            file_type = "video"
            try:
                tags = video_prediction(local_path)  
            except Exception as e:
                logger.warning(f"video analysis failed: {e}")
                tags = []
        tag_counts = dict(Counter(tags))
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

        try:
            table.put_item(
                Item={
                    'file_id': file_url,                   
                    'file_type': file_type,
                    'tags': tag_counts
                }
            )
            logger.info(f"Inserted to DynamoDB: {object_key}")
        except ClientError as e:
            logger.error(f"Failed to write to DynamoDB: {e}")

if __name__ == '__main__':
    print("predicting...")
    print(image_prediction("./test_images/crows_1.jpg"))
    # image_prediction("./test_images/crows_3.jpg", result_filename='crows_detected_2.jpg')
    # image_prediction("./test_images/kingfisher_2.jpg",result_filename='kingfishers_detected.jpg' )
    # image_prediction("./test_images/myna_1.jpg",result_filename='myna_detected.jpg')
    # image_prediction("./test_images/owl_2.jpg",result_filename='owls_detected.jpg')
    # image_prediction("./test_images/peacocks_3.jpg",result_filename='peacocks_detected_1.jpg')
    # image_prediction('./test_images/sparrow_3.jpg',result_filename='sparrow_detected_1.jpg')
    # image_prediction('./test_images/sparrow_1.jpg',result_filename='sparrow_detected_2.jpg')

    # uncomment to test video prediction
    print(video_prediction("./test_videos/crows.mp4"))
    # video_prediction("./test_videos/kingfisher.mp4",result_filename='kingfisher_detected.mp4')