import paho.mqtt.client as mqtt
import time
import tkinter as tk
import threading
from queue import Queue
import json
import random

# topics
registration_devices_topic = "registration_devices"
sensor_topic = "sensor_topic"

# MQTT Broker Details
broker_address = "cottonlady422.cloud.shiftr.io"
broker_port = 1883
username = "cottonlady422"
password = "ZxstVjOX76fqt4SO"

# device id
device_id = "smallscreen_device1"

# Function to update the small screen when we receive a new message
def update_screen(message):
    label.config(text=message)

#Function to generate a random humidity value within a specified range.
def get_humedad():
    return random.uniform(15/100, 50/100)

#Function to generate a random temperature value within a specified range.
def get_temperatur():
    return random.uniform(20, 50)

#Callback function called when the MQTT client successfully connects to the broker.
def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    client.subscribe(sensor_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(msg.topic + ": " + payload)
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
#Seting the title of the main window to "small screen".
root.title("small screen")

# Configuring small screen Elements.
label = tk.Label(root, text="Welcome to our screen")
label.pack(pady=50)

# Start the MQTT loop
client.loop_start()

# Publish the device_id_payload id to the registration_devices_topic topic
device_id_payload = {
    "device_id": device_id
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

# Function to generate and publish sensor payload
def publish_sensor_payload():
    while True:
        payload = {
            "device_id": device_id,
            "humedad": get_humedad(),
            "temperatur": get_temperatur()
        }
        # Publish payload to sensor_topic
        client.publish(sensor_topic, json.dumps(payload))
        time.sleep(5)

# Start a separate thread for publishing sensor payload
publish_thread = threading.Thread(target=publish_sensor_payload, daemon=True)
publish_thread.start()

# Main GUI loop
root.mainloop()
