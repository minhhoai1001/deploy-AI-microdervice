from paho.mqtt import client as mqtt_client

class MQTT_SUB_PUB:
    def __init__(self, broker, port, client_id, username, password):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print(f"Failed to connect, return code {rc}\n")

        client     = mqtt_client.Client(self.client_id)
        client.username_pw_set(self.username, self.password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

def on_message(client, userdata, msg):
    image_path = msg.payload.decode()
    print(image_path)
    result = client.publish(topic_pub, image_path)
    status = result[0]
    if status == 0:
        print(f"Send msg to topic `{topic_pub}`")
    else:
        print(f"Failed to send message to topic {topic_pub}")

if __name__ == '__main__':
    broker      = '172.17.0.2'
    port        = 1883
    topic_sub   = "image/filter"
    topic_pub   = "mask/fish"
    client_id   = 'python-mqtt-1'
    username    = 'emqx'
    password    = 'public'

    mqtt = MQTT_SUB_PUB(broker=broker, port=port, client_id=client_id, username=username, password=password)
    client = mqtt.connect_mqtt()
    client.subscribe(topic_sub)
    client.loop_start()

    while True:
        # client.subscribe(topic_sub)
        client.on_message = on_message
    #     # client.loop_start()
    #     client.publish(topic_pub, "msg")
