#!/bin/bash

# Install necessary packages
sudo apt-get update && sudo apt-get install -y xvfb x11vnc

# Start Xvfb virtual display server
Xvfb :99 -screen 0 1024x768x16 &

# Start x11vnc to share the display
x11vnc -display :99 -forever -nopw &

# Set DISPLAY environment variable
export DISPLAY=:99

# Start the WhatsApp bot
python3 whatsapp_bot.py