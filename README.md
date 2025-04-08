# WhatsApp Bot

A WhatsApp bot that welcomes new members, tracks activity, and manages group participants.

## Features
- Welcomes new group members with a personalized message
- Tracks user activity in groups
- Automatically removes inactive members (30 days without messages)
- Auto-reconnection handling
- Persistent session management

## Deployment Guide

### Prerequisites
- Node.js 16 or higher
- A Railway.app account
- WhatsApp account for the bot

### Deployment Steps on Railway

1. Fork/Clone this repository to your GitHub account

2. Go to [Railway.app](https://railway.app) and sign up/login

3. Click "New Project" → "Deploy from GitHub repo"

4. Select your repository

5. Add the following environment variables in Railway dashboard:
   - `NODE_ENV=production`
   - `DEBUG_LOGS=false`

6. Once deployed, go to your project's deployment logs to see the QR code

7. Scan the QR code with WhatsApp (Settings → Linked Devices → Link a Device)

8. The bot will start running automatically

### Important Notes
- The bot needs to be authenticated only once
- Session data is stored in the `auth_info` directory
- Database is stored in SQLite file
- The bot will automatically reconnect if disconnected

## Local Development
```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Run in production mode
npm run prod
```

## Monitoring
- Use `pm2 status` to check bot status
- Use `pm2 logs whatsapp-bot` to view logs
- The bot auto-restarts on crashes
