import cv2
import os
import time
import logging
import numpy as np
import datetime
from yoloseg import YOLOSeg
from paho.mqtt import client as mqtt_client

# Function to determine if an image is blurry
def is_blurry(img, threshold=1000):

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Resized to 720x1280
    resize_img = cv2.resize(gray, (1280, 720))

    # Apply Laplace function
    dst = cv2.Laplacian(resize_img, cv2.CV_16S, ksize=3)
    abs_dst = cv2.convertScaleAbs(dst)
    
    # Threshold 
    (thresh, bw_img) = cv2.threshold(abs_dst, 60, 255, cv2.THRESH_BINARY)

    # Erode
    kernel = np.ones((3, 3), np.uint8)
    erosion_img = cv2.erode(bw_img, kernel)
    
    # cv2.imwrite(name, erosion_img)
    cnt_pixel = cv2.countNonZero(erosion_img)

    if cnt_pixel < threshold:
        return True
    else:
        return False


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker success!")

def get_datetime():
    current_time = datetime.datetime.now()
    return current_time.strftime("%Y%m%d_%H:%M:%S")


def main(mqtt_config):
    client = mqtt_client.Client(mqtt_config["client_id"])
    client.on_connect = on_connect
    retry_interval = 2  # seconds

    model_path = "models/yolov8n-salmon-seg.onnx"
    yoloseg = YOLOSeg(model_path, conf_thres=0.5, iou_thres=0.3)

    while True:
        try:
            client.username_pw_set(mqtt_config["username"], mqtt_config["password"])
            client.connect(mqtt_config["broker"],  mqtt_config["port"])
            image_folder = "/data/src"
            for filename in (os.listdir(image_folder)):
                if filename.endswith(('.jpg', '.png', '.jpeg')):
                    image_path = os.path.join(image_folder, filename)
                    # Read the image
                    img = cv2.imread(image_path)
            
                    if not is_blurry(img, 1500):
                        # Detect Objects
                        boxes, scores, class_ids, masks = yoloseg(img)
                        mask_img = img.copy()

                        for i, (box, class_id) in enumerate(zip(boxes, class_ids)):
                            x1, y1, x2, y2 = box.astype(int)
                            # Size filter
                            if (x2 - x1 > 1920) or (y2 - y1 > 1080):
                                crop_mask = masks[i][y1:y2, x1:x2]
                                crop_mask_img = mask_img[y1:y2, x1:x2]
                                crop_mask_img[np.where(crop_mask == 0)] = (0, 0, 0)

                                _, image_encoded = cv2.imencode('.jpg', crop_mask_img)
                                image_bytes = image_encoded.tobytes()
                                client.publish(mqtt_config["topic_pub"], image_bytes)

        except Exception as e:
            logging.error(f"Connection attempt failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

if __name__ == "__main__":
    logging.info("Image filter is start")

    mqtt_config = {
        "broker":       os.environ.get("BROKER"),
        "port":         int(os.environ.get("PORT")),
        "topic_pub":    os.environ.get("TOPIC_PUB"),
        "client_id":    os.environ.get("CLIENT_ID"),
        "username":     os.environ.get("USER_NAME"),
        "password":     os.environ.get("PASS_WORD"),
    }
    main(mqtt_config)