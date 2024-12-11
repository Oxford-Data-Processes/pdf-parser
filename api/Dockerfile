# Start of Selection
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    git \
    poppler-utils

WORKDIR /app

# Copy the entire project
COPY .. /app/

RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# End of Selection
