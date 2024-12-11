# Start of Selection
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    git \
    poppler-utils \
    tesseract-ocr \
    python3-pip

WORKDIR /app

# Copy the API code and necessary directories
COPY . /app/api/
COPY ../data /app/data/
COPY ../src /app/src/
COPY ../pdf_parser /app/pdf_parser/

# Install Python dependencies
RUN pip install -r /app/api/requirements.txt

# Create necessary directories
RUN mkdir -p /app/src/outputs /app/src/schema

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# End of Selection
