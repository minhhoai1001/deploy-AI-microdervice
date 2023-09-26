import os
import sys
import cv2
import numpy as np
from yoloseg import YOLOSeg
from mqtt_sub import MQTT_SUB
from mqtt_pub import MQTT_PUB

def main(sub, pub):
    # Initialize YOLOv5 Instance Segmentator
    model_path = "models/yolov8n-salmon-seg.onnx"
    yoloseg = YOLOSeg(model_path, conf_thres=0.5, iou_thres=0.3)

    sub_client = sub.start()
    pub_client = pub.start()
    
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

                # pub.publish(pub_client, f"{img_path}")

    while True:
        sub_client.on_message = on_message

if __name__ == "__main__":
    broker = '172.17.0.3'
    port = 1883
    client_id = 'fish-seg-1'
    username = 'emqx'
    password = 'public'
    topic_sub = "image/filter"
    topic_pub = "mask/fish"
    
    sub = MQTT_SUB(broker=broker, port=port, topic=topic_sub,
                    client_id=client_id, username=username,
                    password=password)
    
    pub = MQTT_PUB(broker=broker, port=port, topic=topic_pub,
                client_id=client_id, username=username,
                password=password)
    main(sub, pub)