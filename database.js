const sqlite3 = require('sqlite3').verbose();
const { DB_PATH } = require('./config');

class Database {
    constructor() {
        this.db = new sqlite3.Database(DB_PATH, (err) => {
            if (err) {
                console.error('Database connection error:', err);
            } else {
                this.initializeTables();
            }
        });
    }

    initializeTables() {
        const userActivityTable = `
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id TEXT PRIMARY KEY,
                group_id TEXT,
                last_activity TIMESTAMP,
                join_date TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        `;

        this.db.run(userActivityTable);
    }

    updateUserActivity(userId, groupId) {
        const query = `
            INSERT INTO user_activity (user_id, group_id, last_activity, join_date, message_count)
            VALUES (?, ?, datetime('now'), datetime('now'), 1)
            ON CONFLICT(user_id) DO UPDATE SET
            last_activity = datetime('now'),
            message_count = message_count + 1
        `;
        
        return new Promise((resolve, reject) => {
            this.db.run(query, [userId, groupId], (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }

    getInactiveUsers(groupId, thresholdMs) {
        const query = `
            SELECT user_id FROM user_activity
            WHERE group_id = ?
            AND (strftime('%s', 'now') - strftime('%s', last_activity)) * 1000 > ?
        `;

        return new Promise((resolve, reject) => {
            this.db.all(query, [groupId, thresholdMs], (err, rows) => {
                if (err) reject(err);
                else resolve(rows.map(row => row.user_id));
            });
        });
    }

    addNewUser(userId, groupId) {
        const query = `
            INSERT INTO user_activity (user_id, group_id, last_activity, join_date)
            VALUES (?, ?, datetime('now'), datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
            join_date = datetime('now')
        `;

        return new Promise((resolve, reject) => {
            this.db.run(query, [userId, groupId], (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }

    close() {
        this.db.close();
    }
}

module.exports = new Database();
