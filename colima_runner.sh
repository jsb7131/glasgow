#!/bin/bash

set -e

MODE=$1
TOKEN="my-token"
PORT=8088
CONTAINER_NAME="docker-run"

function start_colima() {
  echo "Starting Colima with x86_64 architecture..."
  colima start --memory 4 --cpu 4 --arch x86_64
}

function pull_images() {
  echo "Pulling docker-run and glot/python images..."
  docker pull glot/docker-run:latest
  docker pull glot/python:latest
}

function start_runner() {
  echo "Cleaning up old container if it exists..."
  docker rm -f $CONTAINER_NAME 2>/dev/null || true

  echo "Launching docker-run container..."
  docker run -d \
    --restart=always \
    --name $CONTAINER_NAME \
    -p $PORT:8088 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e "API_ACCESS_TOKEN=$TOKEN" \
    glot/docker-run:latest
}

function stop_all() {
  echo "Stopping docker-run container and Colima..."
  docker stop $CONTAINER_NAME 2>/dev/null
  docker rm -f $CONTAINER_NAME 2>/dev/null || true
  colima stop
  echo "Everything stopped."
}

if [[ "$MODE" == "start" ]]; then
  start_colima
  pull_images
  start_runner
elif [[ "$MODE" == "stop" ]]; then
  stop_all
else
  echo "Usage: $0 [start|stop]"
  exit 1
fi
