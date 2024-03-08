import paho.mqtt.client as mqtt
import json

# MQTT Broker Details
broker_address = "cottonlady422.cloud.shiftr.io"
broker_port = 1883
username = "cottonlady422"
password = "ZxstVjOX76fqt4SO"


#topics
registration_devices_topic = "registration_devices"
limitedkey_topic = "limitedkey_topic" 
sensor_topic = "sensor_topic"


registered_topics = []
registered_devices = {}
last_received_message = {}

def on_connect(client, userdata, flags, rc, properties):
    # print("Connected with result code " + str(rc))
    client.subscribe(registration_devices_topic)
    client.subscribe(limitedkey_topic)
    client.subscribe(sensor_topic)
    


def on_message(client, userdata, msg):
    global last_received_message
    topic = msg.topic
    payload = json.loads(msg.payload.decode())

    #add the devices id to registered_devices dictionary
    if topic == registration_devices_topic:
        device_id = payload.get("device_id")
        if device_id not in registered_devices:
            registered_devices[device_id] = {}

    #add topics to registered_topics table
    if topic not in registered_topics:
        registered_topics.append(topic)
    
    last_received_message = msg






                
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
            if topic_input == last_received_message.topic:
                print("Last message payload:", last_received_message.payload.decode())
            else:
                print(f"No message received yet for topic {topic_input}.")
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
