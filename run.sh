#!/bin/bash

# Create a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Install dependencies using the venv's pip
.venv/bin/pip install Flask requests

# Start the services in the background using the venv's python
.venv/bin/python3 api_gateway/main.py > api_gateway.log 2>&1 &
.venv/bin/python3 content_service/main.py > content_service.log 2>&1 &
.venv/bin/python3 recommendation_service/main.py > recommendation_service.log 2>&1 &
.venv/bin/python3 user_service/main.py > user_service.log 2>&1 &