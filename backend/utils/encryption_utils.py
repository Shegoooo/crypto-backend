from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
import os


def generate_rsa_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

class MessageEncryptor:
    def __init__(self):
        # get keys from environment variables
        self.private_key, self.public_key = generate_rsa_keys()
        self.key = ''

    def pad_message(self, message):
        return message + (16 - len(message) % 16) * ' '

    def encrypt_message_aes(self, message):
        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_message = cipher.encrypt(self.pad_message(message).encode())
        return base64.b64encode(encrypted_message).decode('utf-8'), key

    def decrypt_message_aes(self, encrypted_message, key):
        encrypted_message = base64.b64decode(encrypted_message)
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted_message = cipher.decrypt(encrypted_message).decode('utf-8').strip()
        return decrypted_message

    def encrypt_key_rsa(self, aes_key, public_key):
        assert public_key
        rsa_key = RSA.import_key(public_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        encrypted_key = cipher_rsa.encrypt(aes_key)
        return base64.b64encode(encrypted_key).decode('utf-8')

    def decrypt_key_rsa(self, encrypted_key, private_key):
        encrypted_key = base64.b64decode(encrypted_key)
        rsa_key = RSA.import_key(private_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        decrypted_key = cipher_rsa.decrypt(encrypted_key)
        return decrypted_key

    def encrypt_message(self, message):
        
        encrypted_message, aes_key = self.encrypt_message_aes(message)
        try:
            encrypted_aes_key = self.encrypt_key_rsa(aes_key, self.public_key)
        except AssertionError:
            raise Exception("Missing public key")
        except Exception as e:
            raise Exception(f"Failed to encrypt AES key: {str(e)}")
        return encrypted_message, encrypted_aes_key

    def decrypt_message(self, encrypted_message, encrypted_aes_key):
        aes_key = self.decrypt_key_rsa(encrypted_aes_key, self.private_key)
        decrypted_message = self.decrypt_message_aes(encrypted_message, aes_key)
        return decrypted_message

def test_encryption():
    # Create a MessageEncryptor instance
    encryptor = MessageEncryptor()

    # Encrypt a message
    message = "Hello, Baddie!"
    encrypted_message, encrypted_aes_key = encryptor.encrypt_message(message)

    # check tyoe of enc_aes_key
    print(type(encrypted_aes_key))
    print(encrypted_aes_key)
    # Print the encrypted message and the encrypted AES key
    # print("Encrypted message:", encrypted_message)
    # print("Encrypted AES key:", encrypted_aes_key)

    # breakpoint()
    # Decrypt the message
    decrypted_message = encryptor.decrypt_message(encrypted_message, encrypted_aes_key)

    # Print the original message and the decrypted message
    print("Original message:", message)
    print("Encrypted message:", encrypted_message)
    print("Decrypted message:", decrypted_message)

# # Run the test function
# test_encryption()