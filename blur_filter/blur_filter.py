# import cv2
from PIL import Image, ImageFilter
import os
import sys
import numpy as np
# from mqtt_pub import MQTT_PUB

# # Function to determine if an image is blurry
# def is_blurry(img, threshold=1000):

#     # Convert the image to grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     h, w = gray.shape[:2]

#     # Crop center with 80%
#     crop_img = gray[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)]
    
#     # Resized to 720x1280
#     resize_img = cv2.resize(crop_img, (1280, 720))

#     # Apply Laplace function
#     dst = cv2.Laplacian(resize_img, cv2.CV_16S, ksize=3)
#     abs_dst = cv2.convertScaleAbs(dst)
    
#     # Threshold 
#     (thresh, bw_img) = cv2.threshold(abs_dst, 60, 255, cv2.THRESH_BINARY)

#     # Erode
#     kernel = np.ones((3, 3), np.uint8)
#     erosion_img = cv2.erode(bw_img, kernel)
    
#     # cv2.imwrite(name, erosion_img)
#     cnt_pixel = cv2.countNonZero(erosion_img)

#     if cnt_pixel < threshold:
#         return True
#     else:
#         return False

def is_blurry(img, filename, threshold=50000):
    # Convert the image to grayscale
    gray_img = img.convert('L')

    # Get the dimensions
    w, h = gray_img.size

    # Crop the center with 80%
    left = int(w * 0.1)
    upper = int(h * 0.1)
    right = int(w * 0.9)
    lower = int(h * 0.9)
    cropped_img = gray_img.crop((left, upper, right, lower))

    # Resize to 1280x720
    resized_img = cropped_img.resize((1280, 720), Image.LANCZOS)

    # Apply Laplacian filter
    laplace_img = resized_img.filter(ImageFilter.FIND_EDGES)

    # Convert the Laplacian image to grayscale
    gray_laplace_img = laplace_img.convert('L')

    # Threshold
    threshold_value = 60
    bw_img = gray_laplace_img.point(lambda p: p < threshold_value and 255)

    # Erode
    eroded_img = bw_img.filter(ImageFilter.MinFilter(size=3))
    
    # eroded_img.save(filename)
    # Count non-zero pixels
    cnt_pixel = sum(1 for pixel in eroded_img.getdata() if pixel == 0)

    # print("cnt_pixel: ", cnt_pixel)
    # eroded_img.save(str(cnt_pixel) + filename)

    if cnt_pixel < threshold:
        return True
    else:
        return False


    
def main(pub, image_folder):
    # pub_client = pub.start()

    for filename in (os.listdir(image_folder)):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            image_path = os.path.join(image_folder, filename)

            # Read the image
            img = Image.open(image_path) 
            if not (is_blurry(img, filename, 50000)):
                img_path = f"../imgs/filtered/{filename.replace('png', 'jpg')}"
                img.save(img_path)
                # pub.publish(pub_client, f"{img_path}")


if __name__ == "__main__":
    image_folder = sys.argv[1]
    broker = '172.17.0.2'
    port = 1883
    topic = "image/filter"
    client_id = 'blur-filter'
    username = 'emqx'
    password = 'public'

    # pub = MQTT_PUB(broker=broker, port=port, topic=topic,
    #                 client_id=client_id, username=username,
    #                 password=password)
    pub = 0
    
    main(pub, image_folder)