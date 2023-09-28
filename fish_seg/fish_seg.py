import cv2
import numpy as np
from yoloseg import YOLOSeg
from mqtt_sub_pub import MQTT_SUB_PUB

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
    

if __name__ == "__main__":
    broker      = '172.17.0.2'
    port        = 1883
    topic_sub   = "image/filter"
    topic_pub   = "mask/fish"
    client_id   = 'fish-seg-mqtt-1'
    username    = 'emqx'
    password    = 'public'
    
    mqtt = MQTT_SUB_PUB(broker=broker, port=port, client_id=client_id, username=username, password=password)

    main(mqtt)
