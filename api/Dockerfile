# Start of Selection
FROM python:3.11-slim

# Install git to enable installation from git repositories
RUN apt-get update && apt-get install -y git

COPY . .

RUN pip install -r requirements.txt
# End of Selection
