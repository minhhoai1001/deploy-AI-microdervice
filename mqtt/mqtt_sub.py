from paho.mqtt import client as mqtt_client
import time

class MQTT_SUB:
    def __init__(self, broker, port, topic, client_id, username, password):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.username = username
        self.password = password

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print(f"Failed to connect, return code {rc}\n")

        client = mqtt_client.Client(self.client_id)
        client.username_pw_set(self.username, self.password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def start(self):
        client = self.connect_mqtt()
        client.subscribe(self.topic)
        client.loop_start()
        return client


if __name__ == '__main__':
    broker = '172.17.0.3'
    port = 1883
    topic = "python/mqtt"
    # generate client ID with pub prefix randomly
    client_id = 'python-mqtt-1'
    username = 'emqx'
    password = 'public'

    sub = MQTT_SUB(broker=broker, port=port, topic=topic,
                        client_id=client_id, username=username,
                        password=password)
    sub_client = sub.start()

    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    while True:
        sub_client.on_message = on_message
        # client.loop_start()
        time.sleep(2)
