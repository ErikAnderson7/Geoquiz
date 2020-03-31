#!/bin/sh

echo "Starting Server for Multiplayer"

gunicorn -b 0.0.0.0:5002 multiplayer:app