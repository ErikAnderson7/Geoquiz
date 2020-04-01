#!/bin/sh

echo "Starting Server for Multiplayer"

# This gunicorn command allows for it to work with websockets. 
# The gunicorn command I was using previously (basically the one from the normal backend) did not work with websockets. 
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 multiplayer:app