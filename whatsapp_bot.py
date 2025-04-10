import os

# Ensure DISPLAY environment variable is set for headless environments
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":99"

import logging
from dotenv import load_dotenv
import openai
from fastapi import FastAPI, HTTPException
import uvicorn
import asyncio
from pywhatkit import sendwhatmsg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            receiver_number = "+1234567890"  # Example number, replace with actual
            sendwhatmsg(receiver_number, response, 22, 0)  # Example time: 22:00

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
