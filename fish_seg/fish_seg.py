import os
import cv2
import time
import numpy as np
from yoloseg import YOLOSeg
# from mqtt_sub_pub import MQTT_SUB_PUB
from paho.mqtt import client as mqtt_client

def main(mqtt):
    # Initialize YOLOv5 Instance Segmentator
    model_path = "models/yolov8n-salmon-seg.onnx"
    yoloseg = YOLOSeg(model_path, conf_thres=0.5, iou_thres=0.3)

    def on_message(client, userdata, msg):
        image_path = msg.payload.decode()
        print(image_path)
        img = cv2.imread(image_path)

        # Detect Objects
        boxes, scores, class_ids, masks = yoloseg(img)

        mask_img = img.copy()

        for i, (box, class_id) in enumerate(zip(boxes, class_ids)):
            x1, y1, x2, y2 = box.astype(int)
            if masks is None:
                cv2.rectangle(mask_img, (x1, y1), (x2, y2), (255, 0, 0), -1)
            else:
                crop_mask = masks[i][y1:y2, x1:x2]
                crop_mask_img = mask_img[y1:y2, x1:x2]
                crop_mask_img[np.where(crop_mask == 0)] = (0, 0, 0)
                img_path = f"../imgs/mask_fish/{image_path.split('/')[-1]}"
                cv2.imwrite(img_path, crop_mask_img)

                result = client.publish(topic_pub, f"{img_path}")
                status = result[0]
                if status == 0:
                    print(f"Send msg to topic `{topic_pub}`")
                else:
                    print(f"Failed to send message to topic {topic_pub}")

    client = mqtt.connect_mqtt()
    client.subscribe(topic_sub)
    client.loop_start()

    while True:
        client.on_message = on_message

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker success!")  

if __name__ == "__main__":
    broker      = os.environ.get("BROKER")
    port        = os.environ.get("PORT")
    client_id   = os.environ.get("CLIENT_ID")
    username    = os.environ.get("USER_NAME")
    password    = os.environ.get("PASS_WORD")
    topic_sub   = os.environ.get("TOPIC_SUB")
    topic_pub   = os.environ.get("TOPIC_PUB")
    
    # mqtt = MQTT_SUB_PUB(broker=broker, port=port, client_id=client_id, username=username, password=password)
    model_path = "models/yolov8n-salmon-seg.onnx"
    yoloseg = YOLOSeg(model_path, conf_thres=0.5, iou_thres=0.3)

    def on_message(client, userdata, msg):
        image_path = msg.payload.decode()
        print(image_path)
        img = cv2.imread(image_path)

        # Detect Objects
        boxes, scores, class_ids, masks = yoloseg(img)

        mask_img = img.copy()

        for i, (box, class_id) in enumerate(zip(boxes, class_ids)):
            x1, y1, x2, y2 = box.astype(int)
            if masks is None:
                cv2.rectangle(mask_img, (x1, y1), (x2, y2), (255, 0, 0), -1)
            else:
                crop_mask = masks[i][y1:y2, x1:x2]
                crop_mask_img = mask_img[y1:y2, x1:x2]
                crop_mask_img[np.where(crop_mask == 0)] = (0, 0, 0)
                img_path = f"/data/mask_fish/{image_path.split('/')[-1]}"
                cv2.imwrite(img_path, crop_mask_img)

                client.publish(topic_pub, img_path)
                
    # main(mqtt)
    print("Image filter is start")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    retry_interval = 2  # seconds
    while True:
        try:
            client.username_pw_set(username, password)
            client.connect(broker, int(port))
            client.subscribe(topic_sub)
            client.loop_start()
            while True:
                client.on_message = on_message

        except Exception as e:
            print(f"Connection attempt failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)