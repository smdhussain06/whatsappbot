const bot = require('./bot');

// Start the WhatsApp bot
bot.initialize()
    .then(() => {
        console.log('Bot initialization started. Scan the QR code to connect.');
    })
    .catch((error) => {
        console.error('Failed to start the bot:', error);
    });
