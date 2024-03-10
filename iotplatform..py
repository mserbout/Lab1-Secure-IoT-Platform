import paho.mqtt.client as mqtt
import json

# MQTT Broker Details
broker_address = "patternzebra757.cloud.shiftr.io"
broker_port = 1883
username = "patternzebra757"
password = "dl5jtYZxKbD2taNs"

# topics
registration_devices_topic = "registration_devices"
limitedkey_topic = "limitedkey_topic" 
sensor_topic = "sensor_topic"

registered_topics = []
registered_devices = {}
limetedkeypad_msgs = {}
sensor_msgs = {}

def on_connect(client, userdata, flags, rc, properties):
    client.subscribe(registration_devices_topic)
    client.subscribe(limitedkey_topic)
    client.subscribe(sensor_topic)

def decrypt_message(encrypted_msg):
    # Implement your decryption logic here
    # Example: decrypted_msg = your_decryption_function(encrypted_msg)
    decrypted_msg = encrypted_msg.decode()
    return decrypted_msg

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())

    if topic == registration_devices_topic:
        device_id = payload.get("device_id")
        if device_id not in registered_devices:
            registered_devices[device_id] = {}

    if topic == limitedkey_topic:
        limitedkeypad_msg = msg.payload
        limetedkeypad_msgs[limitedkeypad_msg] = {}

    if topic == sensor_topic:
        encrypted_sensor_msg = msg.payload
        decrypted_sensor_msg = decrypt_message(encrypted_sensor_msg)
        sensor_msgs[decrypted_sensor_msg] = {}

    if topic not in registered_topics:
        registered_topics.append(topic)
    



                
#list devices function
def list_devices():
    for device_id, device_info in registered_devices.items():
        print(f"Device ID: {device_id}")

#remove devices from the registered_devices
def remove_device(device_id):
    if device_id in registered_devices:
        del registered_devices[device_id]
        print(f"Device with ID '{device_id}' has been removed from the list of enrolled devices.")
    else:
        print(f"Device with ID '{device_id}' is not registered.")



def select_option():
    print("Welcome to our platform:")
    print("1. List Topics")
    print("2. List new Devices")
    print("3. List/Removest Devices")
    print("4. Exit")
    user_input = input("Enter option number: ")
    return user_input


# Connection to the mqtt broker
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set(username, password)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect(broker_address, broker_port)

# Start the MQTT loop 
mqttc.loop_start()

while True:
    #call the select_option() function to display the platform interface
    option = select_option()
    #if the use choose the first option
    if option == "1":
        print("Registered Topics:")
        for topic in registered_topics:
            print(topic)
        topic_input = input("Please choose a topic: ")
        if topic_input in registered_topics:

            if topic_input == limitedkey_topic:
                for keypadmsg in limetedkeypad_msgs:
                    print(keypadmsg)

            elif topic_input == sensor_topic:
                for sensormsg in sensor_msgs:
                    print(sensormsg)
            elif topic_input == registration_devices_topic:
                for device in registered_devices:
                    print(device)
        else:
         print(f"Invalid topic: {topic_input}. Please choose a valid topic.")

    #if the use choose the second option
    elif option == "2":
        print("New devices Registering")
        list_devices()
    
    #if the use choose the third option
    elif option == "3":
        list_devices()
        remove_device_input = input("Enter device ID to remove: ")
        if remove_device_input:
            remove_device(remove_device_input)
    elif option == "4":
        break
    else:
        print("Invalid option. Please try again.")
    

# Stop the MQTT loop when the user exits
mqttc.loop_stop()