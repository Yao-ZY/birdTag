# Base image provided by AWS for Python 3.12 Lambda functions
FROM public.ecr.aws/lambda/python:3.12

# Install OpenCV-related system dependencies for image processing
RUN dnf install -y \
        mesa-libGL \
        mesa-libGLU \
        glib2 \
    && dnf clean all

# Copy dependency list into the container workspace
COPY requirements.txt /var/task/

# Install all required Python packages listed in requirements.txt
RUN pip install --no-cache-dir -r /var/task/requirements.txt

# Copy the YOLO model file into the working directory
COPY model.pt /var/task/

# Copy the main Lambda function script into the container
COPY birds_detection.py /var/task/

# Define the Lambda function entry point
CMD ["birds_detection.handler"]