import os
import logging
from dotenv import load_dotenv
import openai
from whatsapp_web.js import Client, LocalAuth
from fastapi import FastAPI, HTTPException
import uvicorn
import asyncio

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
        if message.body.startswith('!ai '):
            # Extract the query
            query = message.body[4:].strip()
            
            # Generate response
            response = await generate_ai_response(query)
            
            # Send response
            chat = await message.getChat()
            await chat.sendMessage(response)
            
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")

async def initialize_whatsapp():
    global client
    client = Client(
        puppeteer={
            'headless': True,
            'args': ['--no-sandbox']
        }
    )
    
    @client.on('qr')
    def on_qr(qr):
        logger.info(f"QR Code received: {qr}")
    
    @client.on('ready')
    def on_ready():
        logger.info("WhatsApp client is ready!")
    
    @client.on('message')
    def on_message(message):
        asyncio.create_task(handle_message(message))
    
    @client.on('disconnected')
    def on_disconnect():
        logger.warning("WhatsApp client disconnected. Attempting to reconnect...")
        asyncio.create_task(client.initialize())
    
    await client.initialize()

@app.on_event("startup")
async def startup_event():
    await initialize_whatsapp()

@app.get("/health")
async def health_check():
    if client and client.is_ready:
        return {"status": "healthy"}
    raise HTTPException(status_code=503, detail="WhatsApp client not ready")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
