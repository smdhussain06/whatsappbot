const { default: makeWASocket, DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const qrcode = require('qrcode-terminal');
const { INACTIVITY_THRESHOLD, WELCOME_MESSAGE } = require('./config');
const database = require('./database');

class WhatsAppBot {
    constructor() {
        this.sock = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    async initialize() {
        try {
            // Using auth state management
            const { state, saveCreds } = await useMultiFileAuthState('auth_info');
            
            this.sock = makeWASocket({
                auth: state,
                printQRInTerminal: true,
            });

            // Handle connection events
            this.sock.ev.on('connection.update', async (update) => {
                const { connection, lastDisconnect } = update;

                if (connection === 'close') {
                    const shouldReconnect = 
                        (lastDisconnect?.error instanceof Boom)?.output?.statusCode !== DisconnectReason.loggedOut;
                    
                    if (shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnectAttempts++;
                        await this.initialize();
                    }
                } else if (connection === 'open') {
                    console.log('Connected to WhatsApp');
                    this.reconnectAttempts = 0;
                }
            });

            // Save credentials whenever they are updated
            this.sock.ev.on('creds.update', saveCreds);

            // Handle messages
            this.sock.ev.on('messages.upsert', async ({ messages }) => {
                for (const message of messages) {
                    if (message.key.remoteJid.endsWith('@g.us')) { // Group messages only
                        await this.handleGroupMessage(message);
                    }
                }
            });

            // Handle group participants
            this.sock.ev.on('group-participants.update', async (update) => {
                await this.handleGroupParticipantsUpdate(update);
            });

            // Start inactivity check timer
            this.startInactivityCheck();

        } catch (error) {
            console.error('Error in initialization:', error);
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                await this.initialize();
            }
        }
    }

    async handleGroupMessage(message) {
        try {
            const senderId = message.key.participant;
            const groupId = message.key.remoteJid;

            // Update user activity
            await database.updateUserActivity(senderId, groupId);

        } catch (error) {
            console.error('Error handling group message:', error);
        }
    }

    async handleGroupParticipantsUpdate(update) {
        try {
            const { id: groupId, participants, action } = update;

            if (action === 'add') {
                for (const participant of participants) {
                    // Add new user to database
                    await database.addNewUser(participant, groupId);

                    // Send welcome message
                    const welcomeMsg = WELCOME_MESSAGE.replace('{username}', '@' + participant.split('@')[0]);
                    await this.sock.sendMessage(groupId, {
                        text: welcomeMsg,
                        mentions: [participant]
                    });
                }
            }
        } catch (error) {
            console.error('Error handling group participants update:', error);
        }
    }

    async startInactivityCheck() {
        // Check for inactive users every 24 hours
        setInterval(async () => {
            try {
                const groups = await this.sock.groupFetchAllParticipating();
                
                for (const groupId of Object.keys(groups)) {
                    const inactiveUsers = await database.getInactiveUsers(groupId, INACTIVITY_THRESHOLD);
                    
                    for (const userId of inactiveUsers) {
                        try {
                            // Remove inactive user
                            await this.sock.groupParticipantsUpdate(
                                groupId,
                                [userId],
                                'remove'
                            );
                            console.log(`Removed inactive user ${userId} from group ${groupId}`);
                        } catch (error) {
                            console.error(`Error removing user ${userId}:`, error);
                        }
                    }
                }
            } catch (error) {
                console.error('Error in inactivity check:', error);
            }
        }, 24 * 60 * 60 * 1000); // 24 hours
    }
}

module.exports = new WhatsAppBot();
