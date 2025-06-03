#!/bin/bash

CONTAINER_NAME="opa-flask-api"
IMAGE_NAME="ope-flask-api"
PORT=8088

echo "🛑 Stopping and removing existing container..."
docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

echo "🔁 Rebuilding Docker image..."
docker build -t $IMAGE_NAME .

echo "🚀 Starting new container..."
docker run -d -p $PORT:$PORT --name $CONTAINER_NAME $IMAGE_NAME

echo "✅ Done. Container '$CONTAINER_NAME' is running on port $PORT."