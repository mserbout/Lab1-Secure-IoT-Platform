import paho.mqtt.client as mqtt
import time
import tkinter as tk
import threading
from queue import Queue
import json
import random
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets

# topics
registration_devices_topic = "registration_devices"
sensor_topic = "sensor_topic"

# MQTT Broker Details
broker_address = "patternzebra757.cloud.shiftr.io"
broker_port = 1883
username = "patternzebra757"
password = "dl5jtYZxKbD2taNs"

# device id
device_id = "smallscreen_device1"

# Asymmetric Key Generation
parameters = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())
private_key = parameters.generate_private_key()
public_key = private_key.public_key()
pem_private_key = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())
pem_public_key = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

# Function to update the small screen when we receive a new message
def update_screen(message):
    label.config(text=message)

#Function to generate a random humidity value within a specified range.
def get_humidity():
    return random.uniform(15/100, 50/100)

#Function to generate a random temperature value within a specified range.
def get_temperature():
    return random.uniform(20, 50)

#Callback function called when the MQTT client successfully connects to the broker.
def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    client.subscribe(sensor_topic)

# The callback for when a PUBLISH message is received from the server.
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = msg.payload
    print(msg.topic + ": " + payload.decode('utf-8', 'ignore'))
    # calling the update_screen() function
    update_screen(payload)

# Connection to the mqtt broker
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username, password)
client.connect(broker_address, broker_port, 60)

# Creating the main window for the Tkinter application using the Tk() class.
root = tk.Tk()
#Setting the title of the main window to "small screen".
root.title("small screen")

# Configuring small screen Elements.
label = tk.Label(root, text="Welcome to our screen")
label.pack(pady=50)

# Start the MQTT loop
client.loop_start()

# Publish the device_id_payload id to the registration_devices_topic topic
device_id_payload = {
    "device_id": device_id,
    "public_key": pem_public_key.decode('utf-8')
}
client.publish(registration_devices_topic, json.dumps(device_id_payload))

#Receive messages from both scripts
message_queue = Queue()

# Function to process messages from the queue
def process_messages():
    while True:
        message = message_queue.get()
        update_screen(message)

# Start a separate thread to process messages
message_thread = threading.Thread(target=process_messages, daemon=True)
message_thread.start()

# Generate a random 16-byte AES key
aes_key = secrets.token_bytes(16)

# Generate a random 16-byte nonce
nonce = secrets.token_bytes(16)

# Function to generate and publish sensor payload
def publish_sensor_payload():
    while True:
        payload = {
            "device_id": device_id,
            "humidity": get_humidity(),
            "temperature": get_temperature()
        }
        # Encrypt payload using symmetric key
        cipher = Cipher(algorithms.AES(aes_key), modes.CTR(nonce))
        encryptor = cipher.encryptor()
        ct = encryptor.update(json.dumps(payload).encode()) + encryptor.finalize()
        # Publish encrypted payload to sensor_topic
        client.publish(sensor_topic, ct)
        time.sleep(5)

# Start a separate thread for publishing sensor payload
publish_thread = threading.Thread(target=publish_sensor_payload, daemon=True)
publish_thread.start()

# Main GUI loop
root.mainloop()