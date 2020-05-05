#!/bin/sh

echo "Starting Server for Multiplayer"

# Gunicorn configured to work with websockets 
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 multiplayer:app