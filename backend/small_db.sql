DROP TABLE IF EXISTS messages;

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    phone_number VARCHAR NOT NULL,
    message_key TEXT NOT NULL,
    message_content TEXT NOT NULL
);
