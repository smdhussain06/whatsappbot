import os
import sys
import time
import logging
from dotenv import load_dotenv

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure DISPLAY environment variable is set for headless environments
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":99"
    logger.info(f"DISPLAY environment variable set to {os.environ['DISPLAY']}")

# Check if X server is available
def check_x_server():
    try:
        import subprocess
        result = subprocess.run(["xdpyinfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            logger.info("X server is available")
            return True
        else:
            logger.error(f"X server check failed: {result.stderr.decode().strip()}")
            return False
    except Exception as e:
        logger.error(f"Error checking X server: {str(e)}")
        return False

# Try to set up X server environment
try:
    logger.info(f"Attempting to connect to X server on display {os.environ['DISPLAY']}")
    
    # Import GUI-dependent libraries
    try:
        from fastapi import FastAPI, HTTPException
        import uvicorn
        import asyncio
        import openai
        
        # Only import pywhatkit if we're sure the display is working
        if check_x_server():
            from pywhatkit import sendwhatmsg
        else:
            logger.warning("X server not available, using alternative messaging method")
            # Define a fallback function with the same signature
            def sendwhatmsg(phone_no, message, hour, minute):
                logger.info(f"Would send to {phone_no}: {message} at {hour}:{minute}")
                logger.info("Using fallback method due to missing display server")
                return True
    
    except ImportError as e:
        logger.error(f"Failed to import required modules: {str(e)}")
        sys.exit(1)
        
except Exception as e:
    logger.error(f"Error setting up X environment: {str(e)}")
    sys.exit(1)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 70))
MODEL = os.getenv('MODEL', 'gpt-3.5-turbo')

app = FastAPI()
client = None

async def generate_ai_response(prompt):
    try:
        response = await openai.ChatCompletion.acreate(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return "Sorry, I couldn't process your request at the moment."

async def handle_message(message):
    try:
        if message.startswith('!ai '):
            # Extract the query
            query = message[4:].strip()

            # Generate response
            response = await generate_ai_response(query)

            # Send response using pywhatkit
            # Replace 'receiver_number' with the actual recipient's phone number
            receiver_number = "+919344115330"  # Example number, replace with actual
            
            try:
                sendwhatmsg(receiver_number, response, 22, 0)  # Example time: 22:00
                logger.info("Message sent successfully")
            except Exception as e:
                logger.error(f"Failed to send WhatsApp message: {str(e)}")

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")

@app.on_event("startup")
async def startup_event():
    logger.info("Bot is ready to send messages using pywhatkit.")

@app.get("/health")
async def health_check():
    if client and client.is_ready:
        return {"status": "healthy"}
    raise HTTPException(status_code=503, detail="WhatsApp client not ready")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
