# Use the official AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Add the Python dependencies file to the container's working directory
COPY requirements.txt /var/task/

# Install Python packages listed in requirements.txt without caching
RUN pip install --no-cache-dir -r /var/task/requirements.txt

# Install system-level audio libraries required by soundfile/librosa
RUN yum install -y libsndfile libsndfile-devel && \
    yum clean all

# Copy the BirdNET model and label files to the Lambda working directory
COPY BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite /var/task/
COPY BirdNET_GLOBAL_6K_V2.4_Labels.txt /var/task/

# Transfer the Lambda handler script into the container
COPY birds_audio_detection.py /var/task/

# Define the default Lambda handler entry point
CMD ["birds_audio_detection.handler"]