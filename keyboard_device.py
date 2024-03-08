import paho.mqtt.client as mqtt
from tkinter import simpledialog
import threading
import json


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
        client.publish(limitedkey_topic,json.dumps(user_input))


device_id_payload={"device_id": device_id}
client.publish(registration_devices_topic, json.dumps(device_id_payload))

while True:
    input_thread = threading.Thread(target=handle_keyboard_input, daemon=True)
    input_thread.start()
  
    
    client.loop_start()
    input_thread.join()  

client.loop_stop()


