from __future__ import print_function
import africastalking
import os
from dotenv import load_dotenv
import traceback

# works with both python 2 and 3
from .encryption_utils import MessageEncryptor

load_dotenv()

class SMS:
    def __init__(self):
        # Set your app credentials
        self.username = os.getenv('AFRICASTALKING_USERNAME')
        self.api_key = os.getenv('AFRICASTALKING_API_KEY')

        if not self.username or not self.api_key:
            raise RuntimeError("Invalid username and/or api_key ")

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS

        self.encryptor = MessageEncryptor()

    def send(self, recipients, message):
        try:
            # Encrypt message
            message = self.encryptor.encrypt_message(message)

            print(message)
            # Thats it, hit send and we'll take care of the rest.
            response = self.sms.send(message, [recipients])
            print(response)

        except Exception as e:
            print('Encountered an error while sending: %s' % str(e))
            print(traceback.format_exc())
