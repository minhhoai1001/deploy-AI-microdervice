import os
import cv2
import time
import numpy as np
from yoloseg import YOLOSeg
from functools import partial
import logging
import datetime
from paho.mqtt import client as mqtt_client

received_image1 = None
received_image2 = None
count = 0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker success!")  

def get_datetime():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y%m%d_%H:%M:%S")

    return formatted_time 

def seg_on_message(yoloseg, topic_pub, client, userdata, msg):
    global received_image1, received_image2, count

    # Check the length of received_image1
    if count == 0:
        received_image1 = np.frombuffer(msg.payload, dtype=np.uint8)
        count = 1
    elif count == 1:
        received_image2 = np.frombuffer(msg.payload, dtype=np.uint8)

        image_array1 = cv2.imdecode(received_image1, cv2.IMREAD_COLOR)
        image_array2 = cv2.imdecode(received_image2, cv2.IMREAD_COLOR)
        # Merge the two images into one
        img = np.hstack((image_array1, image_array2))
        count = 0
        # Detect Objects
        boxes, scores, class_ids, masks = yoloseg(img)
        mask_img = img.copy()

        for i, (box, class_id) in enumerate(zip(boxes, class_ids)):
            x1, y1, x2, y2 = box.astype(int)
            if (x2 - x1 > 1920) or (y2 - y1 > 1080):
                crop_mask = masks[i][y1:y2, x1:x2]
                crop_mask_img = mask_img[y1:y2, x1:x2]
                crop_mask_img[np.where(crop_mask == 0)] = (0, 0, 0)

                _, image_encoded = cv2.imencode('.jpg', crop_mask_img)
                image_bytes = image_encoded.tobytes()
                client.publish(topic_pub, image_bytes)


def main(mqtt_config):
    model_path = "models/yolov8n-salmon-seg.onnx"
    yoloseg = YOLOSeg(model_path, conf_thres=0.5, iou_thres=0.3)

    client = mqtt_client.Client(mqtt_config["client_id"])
    client.on_connect = on_connect
    retry_interval = 2  # seconds

    while True:
        try:
            client.username_pw_set(mqtt_config["username"], mqtt_config["password"])
            client.connect(mqtt_config["broker"], mqtt_config["port"])
            client.subscribe(mqtt_config["topic_sub"])
            client.loop_start()

            while True:
                on_message_callback = partial(seg_on_message, yoloseg, mqtt_config["topic_pub"])
                client.on_message = on_message_callback


        except Exception as e:
            logging.error(f"Connection attempt failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

if __name__ == "__main__":
    mqtt_config = {
        "broker":       os.environ.get("BROKER"),
        "port":         int(os.environ.get("PORT")),
        "topic_sub":    os.environ.get("TOPIC_SUB"),
        "topic_pub":    os.environ.get("TOPIC_PUB"),
        "client_id":    os.environ.get("CLIENT_ID"),
        "username":     os.environ.get("USER_NAME"),
        "password":     os.environ.get("PASS_WORD")
    }
    main(mqtt_config)