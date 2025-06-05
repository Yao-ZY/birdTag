
import logging
import os
import json
import base64
from collections import Counter
from datetime import datetime

from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set up writable cache for BirdNET
os.environ["NUMBA_CACHE_DIR"] = "/tmp/numba_cache"
os.makedirs("/tmp/numba_cache", exist_ok=True)

# Supported audio extensions
AUDIO_EXTENSIONS = [".wav", ".mp3", ".ogg", ".flac"]

# BirdNET model paths
MODEL_PATH = "./BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite"
LABEL_PATH = "./BirdNET_GLOBAL_6K_V2.4_Labels.txt"

# BirdNET prediction function
def audio_prediction(audio_path, min_conf=0.5):
    try:
        analyzer = Analyzer(classifier_model_path=MODEL_PATH,
                            classifier_labels_path=LABEL_PATH)
        recording = Recording(analyzer, audio_path, min_conf=min_conf)
        recording.analyze()

        return [det["common_name"] for det in recording.detections]
    except Exception as e:
        logger.error(f"Audio prediction failed: {e}")
        return []

# Lambda handler
def handler(event, context):
    logger.info("Received event")

    try:
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)

        file_base64 = body.get("file_bytes")
        file_type = body.get("file_type")  # e.g. ".wav"

        if not file_base64 or not file_type:
            return {"statusCode": 400, "body": "Missing file_bytes or file_type"}

        if file_type.lower() not in AUDIO_EXTENSIONS:
            return {"statusCode": 400, "body": f"Unsupported audio type: {file_type}"}

        # Decode and save audio file to /tmp
        file_bytes = base64.b64decode(file_base64)
        file_name = datetime.now().strftime("%Y%m%d_%H%M%S") + file_type
        local_path = f"/tmp/{file_name}"

        with open(local_path, "wb") as f:
            f.write(file_bytes)

        logger.info(f"Saved temporary audio file: {local_path}")

        # Predict tags
        tags = audio_prediction(local_path)
        tag_summary = dict(Counter(tags))

        logger.info(f"Audio tag summary: {tag_summary}")

        return {
            "statusCode": 200,
            "body": json.dumps(tag_summary)
        }

    except Exception as e:
        logger.error(f"Error in handler: {e}", exc_info=True)
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
