from flask import Flask, request, jsonify
from dotenv import load_dotenv
from .utils.africastalking_config import SMS
from .utils.encryption_utils import generate_rsa_keys, MessageEncryptor
from flask_cors import CORS
import os
import traceback


# Load environment variables from .env file
load_dotenv()

# Generate keys 
def generate_keys():
    private_key, public_key = generate_rsa_keys()
    
    
    # Set environment variables
    os.environ['PRIVATE_KEY'] = str(private_key)
    os.environ['PUBLIC_KEY'] = str(public_key)

    assert os.getenv('PRIVATE_KEY') and os.getenv('PUBLIC_KEY')

    print('Keys generated')


# Generate RSA keys
generate_keys()

# Initialize Flask application
app = Flask(__name__, static_folder='../secure-messaging-app/src', static_url_path='/')
CORS(app)  # Enable CORS for all domains on all routes

# Endpoint for encrypting a message and sending AES key via SMS
@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    message = data.get('message')

    # Init Class 
    encryptor = MessageEncryptor()

    # Encrypt message with recipient's public key
    encrypted_message = encryptor.encrypt_message(message)

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

    # Init Class
    encryptor = MessageEncryptor()

    # Decrypt message using private key and AES key
    decrypted_message = encryptor.decrypt_message(encrypted_message=encrypted_message)

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
    recipient_phone = data.get('phone')

    if not message or not recipient_phone:
        return jsonify({'success': False, 'error': 'Missing message or recipient phone number'})
    
    print(message, recipient_phone)
    # Send message to recipient's phone number
    try:
        # Init Class
        sms = SMS()
        # print("Sending message: ", message, " to: ", recipient_phone)
        sms.send(recipients=recipient_phone, message=message)

        jsonify({'success': True})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})
    
    # Return success response
    return jsonify({'success': True})

# Endpoint to serve index.html or landing page
@app.route('/')
def index():
    return app.send_static_file('index.html')


# Run the Flask application
if __name__ == '__main__':

    app.run(debug=True)