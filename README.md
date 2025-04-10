# WhatsApp AI Bot

A Python-based WhatsApp bot that uses OpenAI's API to respond to messages prefixed with "!ai".

## Features
- Responds to both personal and group messages
- Generates concise AI responses (limited to 70 characters)
- Auto-reconnection capability
- Error handling for API and connection issues
- Health check endpoint

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key in the `.env` file

## Running the Bot

1. Local development:
   ```
   python whatsapp_bot.py
   ```
2. Scan the QR code with WhatsApp when prompted

## Usage

- In personal chats or groups, send a message starting with "!ai" followed by your question
- Example: "!ai What is the capital of France?"

## Deployment

### Deploying to Heroku:
1. Create a new Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy using Heroku Git:
   ```
   heroku login
   heroku git:remote -a your-app-name
   git push heroku main
   ```

### Deploying to Replit:
1. Create a new Repl
2. Upload project files
3. Add environment variables in Replit Secrets
4. Click "Run"

## Error Handling

The bot includes error handling for:
- Invalid API responses
- Connection issues
- Message processing errors

## Limitations

- Responses are limited to 70 characters to optimize token usage
- Requires a stable internet connection
- WhatsApp account must remain connected
