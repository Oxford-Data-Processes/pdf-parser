# Start of Selection
FROM python:3.11-slim

COPY requirements_package.txt .

RUN pip install -r requirements_package.txt



