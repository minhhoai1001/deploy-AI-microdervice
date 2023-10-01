import cv2
import os
import sys
import time
import logging
import numpy as np
import datetime
from paho.mqtt import client as mqtt_client

# Function to determine if an image is blurry
def is_blurry(img, threshold=1000):

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]

    # Crop center with 80%
    crop_img = gray[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)]
    
    # Resized to 720x1280
    resize_img = cv2.resize(crop_img, (1280, 720))

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
    formatted_time = current_time.strftime("%Y%m%d_%H:%M:%S")

    return formatted_time

if __name__ == "__main__":
    image_folder = sys.argv[1]
    broker      = os.environ.get("BROKER")
    port        = os.environ.get("PORT")
    topic       = os.environ.get("TOPIC")
    client_id   = os.environ.get("CLIENT_ID")
    username    = os.environ.get("USER_NAME")
    password    = os.environ.get("PASS_WORD")

    logging.info("Image filter is start")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    retry_interval = 2  # seconds

    while True:
        try:
            client.username_pw_set(username, password)
            client.connect(broker, int(port))
            while True:
                for filename in (os.listdir(image_folder)):
                    if filename.endswith(('.jpg', '.png', '.jpeg')):
                        image_path = os.path.join(image_folder, filename)
                        # Read the image
                        img = cv2.imread(image_path)
                        if not (is_blurry(img, 1000)):
                            # img_path = f"/data/filtered/{get_datetime()}.jpg"
                            # cv2.imwrite(img_path, img)
                            h, w, _     = img.shape
                            half_w      = w // 2
                            img_left    = img[:, :half_w, :]
                            img_right   = img[:, half_w:, :]
                            _, left_encoded     = cv2.imencode(".jpg", img_left)
                            _, right_encoded    = cv2.imencode(".jpg", img_right)
                            left_bytes  = left_encoded.tobytes()
                            right_bytes = right_encoded.tobytes()
                            client.publish(topic, payload=left_bytes)
                            client.publish(topic, payload=right_bytes)


        except Exception as e:
            logging.error(f"Connection attempt failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)