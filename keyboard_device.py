import paho.mqtt.client as mqtt
from tkinter import simpledialog
import threading
import json

#import libraries
import random
import time
import paho.mqtt.publish as publish
import sys
from cryptography.hazmat.primitives.serialization import ParameterFormat
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.serialization import load_pem_parameters
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from cryptography.fernet import Fernet
import base64


# MQTT Broker Details
broker_address = "cottonlady422.cloud.shiftr.io"
broker_port = 1883
username = "cottonlady422"
password = "ZxstVjOX76fqt4SO"

#topics
limitedkey_topic = "limitedkey_topic" 
registration_devices_topic="registration_devices"

#device id
device_id = "keypad_device"



# Generating Diffie-Hellman parameters
parameters_pub1 = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())

#generate private and public key pairs
prv_Key_pub1 = parameters_pub1.generate_private_key()
public_Key_pub1 = prv_Key_pub1.public_key()

# Converting DH parameters and public key to bytes
dh_parameters_bytes = parameters_pub1.parameter_bytes(encoding=serialization.Encoding.DER, format=serialization.ParameterFormat.PKCS3)
public_key_pem = public_Key_pub1.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
received_public_key_pub1 = serialization.load_pem_public_key(public_key_pem, backend=default_backend())

# Exchange public keys
shared_key = prv_Key_pub1.exchange(received_public_key_pub1)

# # Convert the shared key to a format suitable for Fernet
#shared_key_bytes = shared_key.to_bytes(32, byteorder='big')
encoded_shared_key = base64.urlsafe_b64encode(shared_key)

fernet = Fernet(encoded_shared_key)



def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    client.subscribe(limitedkey_topic)

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(msg.topic + ": " + payload)


# Connection to the mqtt broker
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username, password)
client.connect(broker_address, broker_port, 60)


def handle_keyboard_input():
    user_input = simpledialog.askstring("Input", "Enter message:")
    if user_input:
         # Encrypt user input
        encrypted_message = fernet.encrypt(user_input.encode())
        client.publish(limitedkey_topic,encrypted_message)
        print(encrypted_message)
        print(f"shared_key:{shared_key}")

device_id_payload={"device_id": device_id}
client.publish(registration_devices_topic, json.dumps(device_id_payload))

while True:
    input_thread = threading.Thread(target=handle_keyboard_input, daemon=True)
    input_thread.start()
  
    
    client.loop_start()
    input_thread.join()  

client.loop_stop()


