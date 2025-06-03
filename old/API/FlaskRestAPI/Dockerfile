# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Expose the port your app runs on (adjust if needed)
EXPOSE 8088

# Command to run the application (adjust if your app entry point differs)
CMD ["python", "run.py"]