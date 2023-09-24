import os
import sys
import cv2
import numpy as np
from yoloseg import YOLOSeg

def main(image_folder):
    # Initialize YOLOv5 Instance Segmentator
    model_path = "models/yolov8n-salmon-seg.onnx"
    yoloseg = YOLOSeg(model_path, conf_thres=0.5, iou_thres=0.3)

    for filename in (os.listdir(image_folder)):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            image_path = os.path.join(image_folder, filename)
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

                    cv2.imwrite(f"../imgs/mask_fish/{filename.replace('png', 'jpg')}", crop_mask_img)

if __name__ == "__main__":
    image_folder = sys.argv[1]
    main(image_folder)