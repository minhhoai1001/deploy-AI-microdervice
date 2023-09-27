from paho.mqtt import client as mqtt_client
import time

class MQTT_PUB:
    def __init__(self, broker, port, topic, client_id, username, password):
        self.broker     = broker
        self.port       = 1883
        self.topic      = topic
        self.client_id  = client_id
        self.username   = username
        self.password   = password

    def connect_mqtt(self):
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
        client.loop_start()
        return client
        
    def publish(self, client, msg):
        result = client.publish(self.topic, msg)

        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{self.topic}`")
        else:
            print(f"Failed to send message to topic {self.topic}")


if __name__ == '__main__':
    broker = '172.17.0.3'
    port = 1883
    topic = "python/mqtt"
    # generate client ID with pub prefix randomly
    client_id = 'python-mqtt-2'
    username = 'emqx'
    password = 'public'

    pub = MQTT_PUB(broker=broker, port=port, topic=topic,
                    client_id=client_id, username=username,
                    password=password)
    pub_client = pub.start()
    for i in range(10):
        time.sleep(0.5)
        pub.publish(pub_client, f"{i}")
