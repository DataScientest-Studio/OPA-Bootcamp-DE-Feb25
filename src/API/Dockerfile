# Use an official Python image as the base
FROM python:3.9-slim

ENV PYTHONPATH=/app

# install curl for testing purposes
RUN apt-get update && apt-get install -y curl

RUN mkdir -p /app/FlaskRestAPI
RUN mkdir -p /app/tests
RUN mkdir -p /app/logs
# Set environment variables to avoid Python buffering and enable unbuffered output
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
# Set the working directory in the container
WORKDIR /app

COPY FlaskRestAPI FlaskRestAPI
COPY tests tests
COPY config.py .
COPY ope_db.db .

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Expose the port where FastAPI will run
EXPOSE 8088

# Run the API with Uvicorn
CMD ["gunicorn", "FlaskRestAPI.run:app", "--bind", "0.0.0.0:8088", "--workers", "2"]
