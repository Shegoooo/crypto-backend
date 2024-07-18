import datetime
import traceback
import requests

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

# Project Specific Files
from .utils.encryption_utils import (
    generate_rsa_keys, MessageEncryptor)
from .utils.db_init import DBwrapper


# Load environment variables from .env file
load_dotenv()
db = DBwrapper()
message_service = MessageEncryptor()

# send whatsapp message 
def send_wa(number, message):
    
    if not number or not message:
        raise ValueError('Missing number or message')
    
    # make api call
    url = 'https://9e99-38-242-211-198.ngrok-free.app/v1/messages'

    payload = {
        'number': number,
        'message': message
    }

    response = requests.post(url, json=payload)

    # print(response.text)

def send_message(number, message):
    # encrypt message
    encrypted_message, key = message_service.encrypt_message(message)
    send_wa(number, encrypted_message)
    # Once we send the value to the person we store
    query = 'INSERT INTO messages (created, phone_number, message_key, message_content) VALUES (?,?,?,?)'
    db_id = db.execute(
        query=query,
        params=(datetime.datetime.now(), number, key, message)
    )
    return key, encrypted_message, db_id


# Initialize Flask application
app = Flask(__name__, static_folder='../secure-messaging-app/src', static_url_path='/')
CORS(app)  # Enable CORS for all domains on all routes

# Endpoint for encrypting a message and sending AES key via SMS
@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    message = data.get('message')

    # Encrypt message with recipient's public key
    encrypted_message = message_service.encrypt_message(message)

    # Return encrypted message and information response
    return jsonify({
        'encrypted_message': encrypted_message,
        'info': 'The message has been encrypted !'
    })

# Endpoint for decrypting a message using AES key
@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    encrypted_message = data.get('encrypted_message')
    encrypted_aes_key = data.get('encrypted_aes_key')

    # Do another query to get the key from the DB
    query = f'SELECT * FROM messages WHERE message_key = "{encrypted_aes_key}"'
    rows = db.select(query)
    
    if rows == []:
        return jsonify({
            'info': 'The message has not been found'
        })
    
    db_data = rows[0]

    try:
        # Decrypt message using private key and AES key
        decrypted_message = message_service.decrypt_message(
            encrypted_message=encrypted_message,
            encrypted_aes_key=encrypted_aes_key
        )
    except Exception as e:
        return jsonify({
            'info': 'An error occurred while decrypting the message',
            'error': str(e)
        })

    # Return decrypted message
    return jsonify({
        'decrypted_message': decrypted_message,
        'info': 'The message has been decrypted !'
    })

# API to send messages 
@app.route('/send', methods=['POST'])
def send():
    data = request.json
    message = data.get('message')
    recipient_phone = data.get('number')

    if not message or not recipient_phone:
        return jsonify({'success': False, 'error': 'Missing message or recipient phone number'})
    
    # Send message to recipient's phone number
    try:
        # Send whatapp message 
        key, message_s, db_id = send_message(number=recipient_phone, message=message)
        send_wa(recipient_phone, f'This is your key : {key}')
    except Exception as e:
        # print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})
    
    # Return success response
    return jsonify({
        'success': True,
        'id': db_id,
        'key': key,
        'message': message_s,
        'info': 'The message has been sent !'
        })

# API to display messages sent to a specific phone number
@app.route('/messages', methods=['GET'])
def get_messages():
    phone_number = request.args.get('phone_number')
    if not phone_number:
        return jsonify({'success': False, 'error': 'Missing phone number'})

    try:
        query = f'SELECT id, created, phone_number, message_content FROM messages WHERE phone_number="+{phone_number.replace(" ", "")}"'
        rows = db.select(query)
        print(query)

        messages = []
        for row in rows:
            message = {
                'id': row[0],
                'created_at': row[1],
                'number': row[2],
                'message_content': row[3]
            }
            messages.append(message)

        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})

# Endpoint to serve index.html or landing page
@app.route('/')
def index():
    return app.send_static_file('index.html')


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)