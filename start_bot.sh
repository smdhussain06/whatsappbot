#!/bin/bash

# Install necessary packages
sudo apt-get update && sudo apt-get install -y xvfb x11vnc x11-utils

# Start Xvfb virtual display server
Xvfb :99 -screen 0 1024x768x16 -ac &

# Start x11vnc to share the display
x11vnc -display :99 -forever -nopw &

# Set DISPLAY environment variable
export DISPLAY=:99

# Wait for X server to start
sleep 3

# Verify X server is running
echo "Checking if X server is running..."
xdpyinfo >/dev/null 2>&1 || { echo "X server is not running properly"; exit 1; }

# Start the WhatsApp bot
echo "Starting WhatsApp bot..."
python3 whatsapp_bot.py